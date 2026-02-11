"""
Screenplay Engine Orchestrator
Runs the 9-step Save the Cat pipeline from Snowflake input to formatted screenplay.
"""

import json
import hashlib
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)

from src.screenplay_engine.models import (
    StoryFormat, SnyderGenre, Logline, GenreDefinition,
    HeroProfile, AntagonistProfile, BStoryCharacter, SupportingCast,
    BeatSheet, TheBoard, Screenplay, MarketingValidation,
    LawResult, DiagnosticResult,
)


class ScreenplayPipeline:
    """
    Orchestrates the 9-step Save the Cat screenplay pipeline.

    Pipeline order follows the book: Write FIRST, then Diagnose.
    Snyder Ch.7 opens with "You've made it! You've finally written THE END."
    — diagnostics and laws run on a finished screenplay, not pre-writing artifacts.

    Steps:
        1.  Logline Generation & Validation
        2.  Genre Classification
        3.  Hero Construction (hero, antagonist, B-story)
        3b. Supporting Cast (all other named characters)
        4.  Beat Sheet (BS2)
        5.  The Board (40 scene cards)
        6.  Screenplay Writing (from Board)
        7.  Immutable Laws Validation (on finished screenplay)
        8.  Diagnostic Checks (on finished screenplay)
        9.  Marketing Validation
    """

    STEP_NAMES = {
        1: "Logline",
        2: "Genre Classification",
        3: "Hero Construction",
        "3b": "Supporting Cast",
        4: "Beat Sheet (BS2)",
        5: "The Board",
        6: "Screenplay Writing",
        7: "Immutable Laws",
        8: "Diagnostics",
        "8b": "Targeted Rewrite (Grok)",
        9: "Marketing Validation",
    }

    # Max revision attempts per checkpoint
    MAX_CHECKPOINT_REVISIONS = 2

    def __init__(self, project_dir: str = "artifacts", screenplay_mode: str = "act_by_act"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.current_project_id: Optional[str] = None
        self.screenplay_mode = screenplay_mode  # "monolithic", "scene_by_scene", or "act_by_act"

        # Lazy-loaded step executors
        self._steps: Dict[int, Any] = {}

        # Diagnostic checkpoint runner (incremental Ch.7 checks after every step)
        from src.screenplay_engine.pipeline.checkpoint import CheckpointRunner
        self._checkpoint_runner = CheckpointRunner(str(self.project_dir))
        from src.screenplay_engine.pipeline.checkpoint.checkpoint_prompt import CheckpointPrompt
        self._checkpoint_prompt = CheckpointPrompt()

    def _get_step(self, step_num: int):
        """Lazy-load step executor."""
        if step_num not in self._steps:
            if step_num == 1:
                from src.screenplay_engine.pipeline.steps.step_1_logline import Step1Logline
                self._steps[1] = Step1Logline(str(self.project_dir))
            elif step_num == 2:
                from src.screenplay_engine.pipeline.steps.step_2_genre import Step2Genre
                self._steps[2] = Step2Genre(str(self.project_dir))
            elif step_num == 3:
                from src.screenplay_engine.pipeline.steps.step_3_hero import Step3Hero
                self._steps[3] = Step3Hero(str(self.project_dir))
            elif step_num == 4:
                from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
                self._steps[4] = Step4BeatSheet(str(self.project_dir))
            elif step_num == 5:
                from src.screenplay_engine.pipeline.steps.step_5_board import Step5Board
                self._steps[5] = Step5Board(str(self.project_dir))
            elif step_num == 6:
                from src.screenplay_engine.pipeline.steps.step_6_immutable_laws import Step6ImmutableLaws
                self._steps[6] = Step6ImmutableLaws(str(self.project_dir))
            elif step_num == 7:
                from src.screenplay_engine.pipeline.steps.step_7_diagnostics import Step7Diagnostics
                self._steps[7] = Step7Diagnostics(str(self.project_dir))
            elif step_num == 8:
                from src.screenplay_engine.pipeline.steps.step_8_screenplay import Step8Screenplay
                self._steps[8] = Step8Screenplay(str(self.project_dir))
            elif step_num == 9:
                from src.screenplay_engine.pipeline.steps.step_9_marketing import Step9Marketing
                self._steps[9] = Step9Marketing(str(self.project_dir))
            elif step_num == 85:  # 8b — targeted Grok rewrite
                from src.screenplay_engine.pipeline.steps.step_8b_targeted_rewrite import Step8bTargetedRewrite
                self._steps[85] = Step8bTargetedRewrite(str(self.project_dir))
        return self._steps.get(step_num)

    # ── Project Management ─────────────────────────────────────────────

    def create_project(self, project_name: str, target_format: StoryFormat = StoryFormat.FEATURE) -> str:
        """Create a new screenplay project."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        project_id = f"sp_{project_name.lower().replace(' ', '_')}_{timestamp}"
        logger.info("Creating project: %s (format=%s)", project_id, target_format.value)

        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)

        project_meta = {
            "project_id": project_id,
            "project_name": project_name,
            "target_format": target_format.value,
            "created_at": datetime.utcnow().isoformat(),
            "current_step": 0,
            "steps_completed": [],
            "pipeline_version": "1.0.0",
        }

        meta_path = project_path / "screenplay_project.json"
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(project_meta, f, indent=2)
        except PermissionError as e:
            raise PermissionError(f"Cannot write project metadata to {meta_path}. Details: {e}")

        self.current_project_id = project_id
        return project_id

    def load_project(self, project_id: str) -> Dict[str, Any]:
        """Load existing screenplay project."""
        meta_path = self.project_dir / project_id / "screenplay_project.json"
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except PermissionError as e:
            raise PermissionError(f"Cannot read project metadata: {e}")

        self.current_project_id = project_id
        return meta

    # ── Step Execution ─────────────────────────────────────────────────

    def _run_step(self, step_num, step_name: str, executor_fn):
        """Run a step with logging wrapper. Returns (success, artifact, message)."""
        logger.info("=" * 60)
        logger.info("STEP %s: %s — START", step_num, step_name)
        t0 = time.time()
        try:
            success, artifact, message = executor_fn()
        except Exception as exc:
            elapsed = time.time() - t0
            logger.error("STEP %s: %s — EXCEPTION after %.1fs: %s",
                        step_num, step_name, elapsed, exc)
            raise
        elapsed = time.time() - t0
        status = "PASS" if success else "FAIL"
        logger.info("STEP %s: %s — %s (%.1fs)", step_num, step_name, status, elapsed)
        if not success:
            logger.error("STEP %s failure details: %s", step_num, message[:500])
        else:
            # Log artifact summary
            self._log_artifact_summary(step_num, artifact)
        if success:
            self._update_project_state(step_num, artifact)
        return success, artifact, message

    def _log_artifact_summary(self, step_num, artifact: Dict[str, Any]):
        """Log a concise summary of the artifact produced by a step."""
        if not isinstance(artifact, dict):
            return
        # Logline
        if "logline" in artifact and "title" in artifact:
            logger.info("  title=%s logline_len=%d",
                       artifact.get("title", "?"), len(artifact.get("logline", "")))
        # Genre
        if "genre" in artifact and "working_parts" in artifact:
            parts = artifact.get("working_parts", [])
            logger.info("  genre=%s working_parts=%d",
                       artifact.get("genre", "?"), len(parts))
        # Hero
        if "hero" in artifact and "antagonist" in artifact:
            hero = artifact.get("hero", {})
            antag = artifact.get("antagonist", {})
            logger.info("  hero=%s antagonist=%s b_story=%s",
                       hero.get("name", "?"), antag.get("name", "?"),
                       artifact.get("b_story_character", {}).get("name", "?"))
        # Cast
        if "characters" in artifact and "total_speaking_roles" in artifact:
            logger.info("  cast=%d speaking=%d",
                       len(artifact.get("characters", [])),
                       artifact.get("total_speaking_roles", 0))
        # Beat sheet
        if "beats" in artifact and "midpoint_polarity" in artifact:
            logger.info("  beats=%d midpoint=%s all_is_lost=%s",
                       len(artifact.get("beats", [])),
                       artifact.get("midpoint_polarity", "?"),
                       artifact.get("all_is_lost_polarity", "?"))
        # Board
        if "row_1_act_one" in artifact:
            total = sum(len(artifact.get(k, [])) for k in
                       ["row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"])
            logger.info("  board_cards=%d", total)
        # Screenplay
        if "scenes" in artifact and "total_pages" in artifact:
            logger.info("  scenes=%d pages=%.1f duration=%ds",
                       len(artifact.get("scenes", [])),
                       artifact.get("total_pages", 0),
                       artifact.get("estimated_duration_seconds", 0))
        # Laws
        if "laws" in artifact and "all_passed" in artifact:
            passed = sum(1 for l in artifact.get("laws", []) if l.get("passed"))
            total = len(artifact.get("laws", []))
            logger.info("  laws=%d/%d all_passed=%s", passed, total, artifact.get("all_passed"))
        # Diagnostics
        if "diagnostics" in artifact and "checks_passed_count" in artifact:
            logger.info("  diagnostics=%d/%d",
                       artifact.get("checks_passed_count", 0),
                       artifact.get("total_checks", 0))
        # Marketing
        if "logline_still_accurate" in artifact:
            logger.info("  logline_accurate=%s genre_clear=%s title_works=%s",
                       artifact.get("logline_still_accurate"),
                       artifact.get("genre_clear"),
                       artifact.get("title_works"))

    # ── Diagnostic Checkpoints ──────────────────────────────────────────

    def _run_checkpoint_and_revise(
        self,
        step_num: int,
        artifact: Dict[str, Any],
        all_artifacts: Dict[Any, Dict[str, Any]],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run a diagnostic checkpoint after a step and revise if needed.

        Args:
            step_num: Pipeline step number (1-6).
            artifact: The artifact just produced by the step.
            all_artifacts: All artifacts produced so far (keyed by step num).
            snowflake_artifacts: Original Snowflake input.

        Returns:
            The artifact (possibly revised).
        """
        # Build checkpoint artifacts dict
        ckpt_artifacts = self._build_checkpoint_artifacts(step_num, artifact, all_artifacts)

        logger.info("=" * 40)
        logger.info("CHECKPOINT after Step %d — START", step_num)

        result = self._checkpoint_runner.run_checkpoint(
            step_num, ckpt_artifacts, self.current_project_id,
        )

        if result.passed:
            logger.info("CHECKPOINT after Step %d — ALL PASSED (%d/%d)",
                       step_num, result.checks_passed, result.checks_run)
            return artifact

        # Step 6 (screenplay) revision is too expensive (128K tokens, 10+ min).
        # Log findings and continue — Step 8 diagnostics will provide comprehensive review.
        if step_num == 6:
            logger.warning(
                "CHECKPOINT after Step %d — %d/%d FAILED (no revision for screenplay — too expensive, "
                "Step 8 diagnostics will evaluate)",
                step_num, result.checks_run - result.checks_passed, result.checks_run,
            )
            return artifact

        logger.warning(
            "CHECKPOINT after Step %d — %d/%d FAILED, attempting revision",
            step_num, result.checks_run - result.checks_passed, result.checks_run,
        )

        # Attempt revisions — track best score and keep highest-scoring version
        best_artifact = artifact
        best_score = result.checks_passed
        for revision_attempt in range(self.MAX_CHECKPOINT_REVISIONS):
            revision_reason = self._checkpoint_prompt.generate_revision_feedback(result.failures)

            logger.info("Revision attempt %d/%d for Step %d",
                       revision_attempt + 1, self.MAX_CHECKPOINT_REVISIONS, step_num)

            revised_artifact = self._call_step_revise(
                step_num, revision_reason, all_artifacts, snowflake_artifacts,
            )

            if revised_artifact is None:
                logger.warning("Step %d revise() failed or not available, keeping current artifact",
                             step_num)
                break

            # Re-run checkpoint on revised artifact
            ckpt_artifacts = self._build_checkpoint_artifacts(
                step_num, revised_artifact, all_artifacts,
            )
            result = self._checkpoint_runner.run_checkpoint(
                step_num, ckpt_artifacts, self.current_project_id,
            )

            # Only keep revision if it scored >= the current best
            if result.checks_passed >= best_score:
                best_artifact = revised_artifact
                best_score = result.checks_passed
                logger.info(
                    "Revision %d improved or maintained score: %d/%d (was %d)",
                    revision_attempt + 1, result.checks_passed, result.checks_run, best_score,
                )
            else:
                logger.warning(
                    "Revision %d scored WORSE: %d/%d (best is %d), keeping previous best",
                    revision_attempt + 1, result.checks_passed, result.checks_run, best_score,
                )

            if result.passed:
                logger.info(
                    "CHECKPOINT after Step %d — PASSED after revision %d (%d/%d)",
                    step_num, revision_attempt + 1, result.checks_passed, result.checks_run,
                )
                return best_artifact

        logger.warning(
            "CHECKPOINT after Step %d — continuing with best artifact (%d passed)",
            step_num, best_score,
        )
        return best_artifact

    def _build_checkpoint_artifacts(
        self,
        step_num: int,
        current_artifact: Dict[str, Any],
        all_artifacts: Dict[Any, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build the artifacts dict for a checkpoint prompt."""
        ckpt = {}

        # Include all prior step artifacts
        artifact_map = {
            1: "step_1",
            2: "step_2",
            3: "step_3",
            4: "step_4",
            5: "step_5",
            6: "screenplay",
        }

        for s in range(1, step_num):
            key = artifact_map.get(s)
            if key and s in all_artifacts:
                ckpt[key] = all_artifacts[s]

        # Include the current step's artifact
        current_key = artifact_map.get(step_num)
        if current_key:
            ckpt[current_key] = current_artifact

        return ckpt

    def _call_step_revise(
        self,
        step_num: int,
        revision_reason: str,
        all_artifacts: Dict[Any, Dict[str, Any]],
        snowflake_artifacts: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Call the appropriate step's revise() method.

        Returns the revised artifact, or None if revision failed.
        """
        project_id = self.current_project_id
        try:
            if step_num == 1:
                step = self._get_step(1)
                ok, artifact, msg = step.revise(project_id, revision_reason, snowflake_artifacts)
            elif step_num == 2:
                step = self._get_step(2)
                ok, artifact, msg = step.revise(
                    project_id, revision_reason,
                    all_artifacts.get(1, {}), snowflake_artifacts,
                )
            elif step_num == 3:
                step = self._get_step(3)
                ok, artifact, msg = step.revise(
                    project_id, revision_reason,
                    all_artifacts.get(1, {}), all_artifacts.get(2, {}),
                    snowflake_artifacts,
                )
            elif step_num == 4:
                step = self._get_step(4)
                ok, artifact, msg = step.revise(
                    project_id, revision_reason,
                    all_artifacts.get(1, {}), all_artifacts.get(2, {}),
                    all_artifacts.get(3, {}), snowflake_artifacts,
                )
            elif step_num == 5:
                step = self._get_step(5)
                ok, artifact, msg = step.revise(
                    project_id, revision_reason,
                    all_artifacts.get(4, {}), all_artifacts.get(3, {}),
                    all_artifacts.get(1, {}), all_artifacts.get(2, {}),
                )
            elif step_num == 6:
                step = self._get_step(8)  # Step 6 uses Step8Screenplay executor
                ok, artifact, msg = step.revise(
                    project_id, revision_reason,
                    all_artifacts.get(5, {}), all_artifacts.get(3, {}),
                    all_artifacts.get(2, {}), all_artifacts.get(1, {}),
                )
            else:
                return None

            if ok:
                logger.info("Step %d revision succeeded: %s", step_num, msg[:200])
                return artifact
            else:
                logger.warning("Step %d revision failed: %s", step_num, msg[:200])
                return None

        except Exception as e:
            logger.error("Step %d revision raised exception: %s", step_num, e)
            return None

    def execute_step_1(self, snowflake_artifacts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 1: Generate and validate logline from Snowflake output."""
        step = self._get_step(1)
        return self._run_step(1, "Logline", lambda: step.execute(snowflake_artifacts, self.current_project_id))

    def execute_step_2(self, step_1_artifact: Dict[str, Any], snowflake_artifacts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 2: Classify into one of 10 Snyder genres."""
        step = self._get_step(2)
        return self._run_step(2, "Genre Classification", lambda: step.execute(step_1_artifact, snowflake_artifacts, self.current_project_id))

    def execute_step_3(self, step_1_artifact: Dict[str, Any], step_2_artifact: Dict[str, Any], snowflake_artifacts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 3: Construct hero, antagonist, and B-story character."""
        step = self._get_step(3)
        return self._run_step(3, "Hero Construction", lambda: step.execute(step_1_artifact, step_2_artifact, snowflake_artifacts, self.current_project_id))

    def execute_step_4(self, step_1_artifact: Dict[str, Any], step_2_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any], snowflake_artifacts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 4: Generate 15-beat BS2."""
        step = self._get_step(4)
        return self._run_step(4, "Beat Sheet (BS2)", lambda: step.execute(step_1_artifact, step_2_artifact, step_3_artifact, snowflake_artifacts, self.current_project_id))

    def execute_step_5(self, step_4_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any], step_1_artifact: Dict[str, Any], step_2_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 5: Build The Board — 40 scene cards."""
        step = self._get_step(5)
        return self._run_step(5, "The Board", lambda: step.execute(step_4_artifact, step_3_artifact, step_1_artifact, step_2_artifact, self.current_project_id))

    def execute_step_6(self, step_5_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any], step_2_artifact: Dict[str, Any], step_1_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 6: Write the screenplay from validated Board (was old Step 8)."""
        step = self._get_step(8)  # Still uses Step8Screenplay executor internally
        mode = self.screenplay_mode
        return self._run_step(6, f"Screenplay Writing ({mode})", lambda: step.execute(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact,
            self.current_project_id, generation_mode=mode,
        ))

    def execute_step_7(self, screenplay_artifact: Dict[str, Any], step_5_artifact: Dict[str, Any], step_4_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 7: Validate 7 Immutable Laws on finished screenplay (Save the Cat Ch.6)."""
        step = self._get_step(6)  # Still uses Step6ImmutableLaws executor internally
        return self._run_step(7, "Immutable Laws", lambda: step.execute(screenplay_artifact, step_5_artifact, step_4_artifact, step_3_artifact, self.current_project_id))

    def execute_step_8(self, screenplay_artifact: Dict[str, Any], step_5_artifact: Dict[str, Any], step_4_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 8: Run 9 Diagnostic Checks on finished screenplay (Save the Cat Ch.7)."""
        step = self._get_step(7)  # Still uses Step7Diagnostics executor internally
        return self._run_step(8, "Diagnostics", lambda: step.execute(screenplay_artifact, step_5_artifact, step_4_artifact, step_3_artifact, self.current_project_id))

    def execute_step_8b(self, screenplay_artifact: Dict[str, Any], diagnostics_artifact: Dict[str, Any], step_3_artifact: Dict[str, Any], step_1_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 8b: Targeted Grok scene rewrite based on diagnostic failures."""
        step = self._get_step(85)
        return self._run_step("8b", "Targeted Rewrite (Grok)", lambda: step.execute(
            screenplay_artifact, diagnostics_artifact, step_3_artifact, step_1_artifact,
            self.current_project_id,
        ))

    def execute_step_9(self, screenplay_artifact: Dict[str, Any], step_1_artifact: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Step 9: Marketing validation — logline still accurate?"""
        step = self._get_step(9)
        return self._run_step(9, "Marketing Validation", lambda: step.execute(screenplay_artifact, step_1_artifact, self.current_project_id))

    # ── Full Pipeline ──────────────────────────────────────────────────

    def run_full_pipeline(self, snowflake_artifacts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Run all 9 steps sequentially with diagnostic checkpoints after steps 1-6.

        After each of steps 1-6, runs applicable Ch.7 diagnostic checks. If any
        fail, feeds failures into the step's revise() method (max 2 attempts).
        This catches structural problems incrementally instead of only at the end.

        Args:
            snowflake_artifacts: Dict with keys 'step_0' through 'step_9' from Snowflake output

        Returns:
            (success, final_artifact, message)
        """
        artifacts: Dict[Any, Dict[str, Any]] = {}

        # Steps 1-6: Generation + diagnostic checkpoint after each
        checkpointed_steps = [
            (1, lambda: self.execute_step_1(snowflake_artifacts)),
            (2, lambda: self.execute_step_2(artifacts[1], snowflake_artifacts)),
            (3, lambda: self.execute_step_3(artifacts[1], artifacts[2], snowflake_artifacts)),
            (4, lambda: self.execute_step_4(artifacts[1], artifacts[2], artifacts[3], snowflake_artifacts)),
            (5, lambda: self.execute_step_5(artifacts[4], artifacts[3], artifacts[1], artifacts[2])),
            # Step 6: Write screenplay FIRST (book order: write, then diagnose)
            (6, lambda: self.execute_step_6(artifacts[5], artifacts[3], artifacts[2], artifacts[1])),
        ]

        # Steps 7-9: Post-screenplay validation (no checkpoints — they ARE the checks)
        post_steps = [
            # Step 7: Laws check on finished screenplay (artifacts[6]) + board/beats/hero
            (7, lambda: self.execute_step_7(artifacts[6], artifacts[5], artifacts[4], artifacts[3])),
            # Step 8: Final diagnostics on finished screenplay — should find fewer failures
            # now that incremental checkpoints caught problems early
            (8, lambda: self.execute_step_8(artifacts[6], artifacts[5], artifacts[4], artifacts[3])),
        ]

        # Step 8b: Targeted Grok scene rewrite (runs ONLY if Step 8 found failures)
        step_8b = ("8b", lambda: self.execute_step_8b(artifacts[6], artifacts[8], artifacts[3], artifacts[1]))

        # Step 9: Marketing validation (uses potentially rewritten screenplay)
        step_9 = (9, lambda: self.execute_step_9(artifacts[6], artifacts[1]))

        pipeline_t0 = time.time()
        logger.info("=" * 60)
        logger.info("FULL PIPELINE START (with diagnostic checkpoints) — project=%s",
                    self.current_project_id)
        logger.info("=" * 60)

        # Run checkpointed steps (1-6)
        for step_num, executor in checkpointed_steps:
            success, artifact, message = executor()
            if not success:
                elapsed = time.time() - pipeline_t0
                logger.error("PIPELINE FAILED at Step %s after %.1fs: %s",
                            step_num, elapsed, message[:300])
                return False, artifacts, f"Pipeline failed at Step {step_num} ({self.STEP_NAMES[step_num]}): {message}"

            # Run diagnostic checkpoint and possibly revise
            artifact = self._run_checkpoint_and_revise(
                step_num, artifact, artifacts, snowflake_artifacts,
            )
            artifacts[step_num] = artifact

        # Run post-screenplay steps (7-8) — no checkpoints
        for step_num, executor in post_steps:
            success, artifact, message = executor()
            if not success:
                elapsed = time.time() - pipeline_t0
                logger.error("PIPELINE FAILED at Step %s after %.1fs: %s",
                            step_num, elapsed, message[:300])
                return False, artifacts, f"Pipeline failed at Step {step_num} ({self.STEP_NAMES[step_num]}): {message}"
            artifacts[step_num] = artifact

        # Step 8b: Targeted Grok rewrite (only if diagnostics found failures)
        diag_passed = artifacts.get(8, {}).get("checks_passed_count", 9)
        if diag_passed < 9:
            logger.info("Step 8 found %d/9 failures — running Step 8b targeted rewrite", 9 - diag_passed)
            step_num_8b, executor_8b = step_8b
            success, artifact, message = executor_8b()
            if success:
                artifacts["8b"] = artifact
                # Update the screenplay artifact for downstream steps
                artifacts[6] = artifact
                logger.info("Step 8b complete: %s", message)
            else:
                logger.warning("Step 8b failed (non-fatal): %s", message[:300])
        else:
            logger.info("All 9 diagnostics passed — skipping Step 8b")

        # Step 9: Marketing validation (uses potentially rewritten screenplay)
        step_num_9, executor_9 = step_9
        success, artifact, message = executor_9()
        if not success:
            elapsed = time.time() - pipeline_t0
            logger.error("PIPELINE FAILED at Step 9 after %.1fs: %s", elapsed, message[:300])
            return False, artifacts, f"Pipeline failed at Step 9 (Marketing Validation): {message}"
        artifacts[9] = artifact

        elapsed = time.time() - pipeline_t0
        logger.info("=" * 60)
        logger.info("FULL PIPELINE COMPLETE — %.1fs total", elapsed)
        logger.info("=" * 60)
        return True, artifacts, "Screenplay pipeline completed successfully"

    # ── Internal Helpers ───────────────────────────────────────────────

    def _update_project_state(self, step_number: Any, artifact: Dict[str, Any]):
        """Update project metadata after step completion."""
        if not self.current_project_id:
            return

        meta_path = self.project_dir / self.current_project_id / "screenplay_project.json"

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                project_meta = json.load(f)
        except PermissionError:
            return

        # Handle mixed int/"3b" step numbering
        if isinstance(step_number, int):
            current = project_meta.get('current_step', 0)
            if isinstance(current, int):
                project_meta['current_step'] = max(current, step_number)
            else:
                project_meta['current_step'] = step_number
        steps_completed = project_meta.get('steps_completed', [])
        if step_number not in steps_completed:
            steps_completed.append(step_number)
        project_meta['steps_completed'] = steps_completed
        project_meta['last_updated'] = datetime.utcnow().isoformat()

        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(project_meta, f, indent=2)
        except PermissionError:
            pass

    def _load_step_artifact(self, step_number: int) -> Optional[Dict[str, Any]]:
        """Load a saved step artifact from disk."""
        if not self.current_project_id:
            return None

        step_files = {
            1: "sp_step_1_logline.json",
            2: "sp_step_2_genre.json",
            3: "sp_step_3_hero.json",

            4: "sp_step_4_beat_sheet.json",
            5: "sp_step_5_board.json",
            6: "sp_step_6_immutable_laws.json",
            7: "sp_step_7_diagnostics.json",
            8: "sp_step_8_screenplay.json",
            9: "sp_step_9_marketing.json",
        }

        artifact_path = self.project_dir / self.current_project_id / step_files.get(step_number, "")
        if not artifact_path.exists():
            return None

        try:
            with open(artifact_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except PermissionError:
            return None

    def _save_step_artifact(self, step_number: int, artifact: Dict[str, Any]):
        """Save a step artifact to disk."""
        if not self.current_project_id:
            return

        step_files = {
            1: "sp_step_1_logline.json",
            2: "sp_step_2_genre.json",
            3: "sp_step_3_hero.json",

            4: "sp_step_4_beat_sheet.json",
            5: "sp_step_5_board.json",
            6: "sp_step_6_immutable_laws.json",
            7: "sp_step_7_diagnostics.json",
            8: "sp_step_8_screenplay.json",
            9: "sp_step_9_marketing.json",
        }

        artifact_path = self.project_dir / self.current_project_id / step_files.get(step_number, "")
        try:
            with open(artifact_path, 'w', encoding='utf-8') as f:
                json.dump(artifact, f, indent=2, ensure_ascii=False)
        except PermissionError as e:
            raise PermissionError(f"Cannot save Step {step_number} artifact: {e}")
