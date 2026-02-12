"""
Step 8 Implementation: Screenplay Writing (Save the Cat)

Three generation modes:
  - monolithic (v2): All 40 scenes in one GPT call. Fast, coherent, but hard to edit.
  - scene_by_scene (v3): One scene at a time with per-scene GPT self-checks.
  - act_by_act (v4): GPT writes ~10 scenes per act, Grok (xAI) checks with fresh eyes,
    GPT rewrites based on Grok's feedback. Best quality.
"""

import json
import os
import re
import uuid
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Set

logger = logging.getLogger(__name__)

from src.screenplay_engine.pipeline.validators.step_8_validator import Step8Validator
from src.screenplay_engine.pipeline.prompts.step_8_prompt import Step8Prompt
from src.ai.generator import AIGenerator


# Milestone check definitions for each act break (used by scene_by_scene mode)
MILESTONE_CHECKS = {
    "Act 1": (
        "EMOTIONAL COLOR WHEEL: Review all scenes written so far. What emotions have been "
        "hit? (Options: lust, fear, joy, hope, despair, anger, tenderness, surprise, longing, "
        "regret, frustration, near-miss anxiety, triumph, human foible.) Are at least 3 "
        "different emotions present? If the palette is narrow, FAIL and suggest which emotions "
        "to emphasize in Act 2."
    ),
    "Midpoint": (
        "TURN TURN TURN: Is the story accelerating? Are obstacles escalating in complexity "
        "and stakes? Or is the pacing flat — same level of difficulty repeated? Snyder: "
        "'It's not enough for the plot to go forward, it must go forward faster.'\n\n"
        "MAKE THE BAD GUY BADDER: Is the antagonist becoming more threatening across scenes? "
        "Does the antagonist have a slight edge over the hero? Snyder: 'Making the bad guy "
        "badder automatically makes the hero bigger.'"
    ),
    "Act 2B": (
        "TAKE A STEP BACK: Do characters start far enough back emotionally? Is the hero's "
        "growth arc visible — are they clearly NOT yet the person they'll become? Snyder: "
        "'By drawing the bow back to its very quivering end point, the flight of the arrow "
        "is its strongest.'\n\n"
        "EMOTIONAL COLOR WHEEL: Full palette check — has the screenplay hit at least 6 "
        "distinct emotions across all scenes so far? List which are missing."
    ),
}

# Act boundaries for act-by-act mode
ACT_DEFINITIONS = [
    ("Act 1", 0, 10),     # Cards 1-10  (Set-Up through Break into Two)
    ("Act 2A", 10, 20),   # Cards 11-20 (B Story through Midpoint)
    ("Act 2B", 20, 30),   # Cards 21-30 (Bad Guys Close In through Break into Three)
    ("Act 3", 30, None),  # Cards 31+   (Finale through Final Image)
]


class Step8Screenplay:
    """
    Screenplay Engine Step 8: Screenplay Writing

    Three generation modes:
      - monolithic: All scenes in one massive GPT call (fast, coherent)
      - scene_by_scene: One scene at a time with per-scene GPT self-checks
      - act_by_act: GPT writes per act, Grok checks with fresh eyes, GPT revises
    """

    VERSION = "5.0.0"

    # Max revision attempts per scene (structural + diagnostic)
    MAX_SCENE_REVISIONS = 1

    # Act-by-act generation defaults (can be overridden by env vars)
    DEFAULT_WRITER_TEMPERATURE = 0.2
    DEFAULT_WRITER_MAX_TOKENS = 64000
    DEFAULT_CHECKER_MAX_TOKENS = 32000
    DEFAULT_REVISION_MAX_TOKENS = 24000
    DEFAULT_MAX_REVISIONS = 4
    DEFAULT_CHECKER_RETRIES = 2

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step8Validator()
        self.prompt_generator = Step8Prompt()
        self.generator = AIGenerator()  # GPT — the writer

    def execute(
        self,
        step_5_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        generation_mode: str = "act_by_act",
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 8: Generate screenplay.

        Args:
            step_5_artifact: The Board with 40 scene cards (step 5 output)
            step_3_artifact: Hero / characters artifact (step 3 output)
            step_2_artifact: Genre classification artifact (step 2 output)
            step_1_artifact: Logline / title artifact (step 1 output)
            project_id: Project UUID (auto-generated if not provided)
            model_config: AI model configuration overrides
            generation_mode: "monolithic", "scene_by_scene", or "act_by_act"

        Returns:
            Tuple of (success, artifact, message)
        """
        if not project_id:
            project_id = str(uuid.uuid4())

        # ── Extract context from upstream artifacts ──────────────────────
        board_cards = self.prompt_generator._extract_board_cards(step_5_artifact)
        title = step_1_artifact.get("title", "UNTITLED")
        logline = step_1_artifact.get("logline", "MISSING")
        genre = step_2_artifact.get("genre", "MISSING")
        format_value = step_2_artifact.get("format", "feature")

        hero_summary = self._build_hero_summary(step_3_artifact)
        characters_summary = self._build_characters_summary(step_3_artifact)
        character_identifiers = self._build_character_identifiers(step_3_artifact)

        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        hero_name = hero.get("name", "HERO")
        antagonist = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        antagonist_name = antagonist.get("name", "ANTAGONIST")

        ctx = {
            "board_cards": board_cards, "title": title, "logline": logline,
            "genre": genre, "format_value": format_value,
            "hero_summary": hero_summary, "characters_summary": characters_summary,
            "character_identifiers": character_identifiers,
            "hero_name": hero_name, "antagonist_name": antagonist_name,
            "project_id": project_id, "model_config": model_config,
            "step_5_artifact": step_5_artifact,
            "step_3_artifact": step_3_artifact,
            "step_2_artifact": step_2_artifact,
            "step_1_artifact": step_1_artifact,
        }

        logger.info("=" * 60)
        logger.info("SCREENPLAY GENERATION MODE: %s (v%s)", generation_mode, self.VERSION)
        logger.info("=" * 60)

        if generation_mode == "monolithic":
            return self._execute_monolithic(ctx)
        elif generation_mode == "scene_by_scene":
            return self._execute_scene_by_scene(ctx)
        elif generation_mode == "act_by_act":
            return self._execute_act_by_act(ctx)
        else:
            return False, {}, f"Unknown generation_mode: {generation_mode}"

    # ══════════════════════════════════════════════════════════════════════
    # MODE 1: MONOLITHIC (v2.0.0 — all 40 scenes in one GPT call)
    # ══════════════════════════════════════════════════════════════════════

    def _execute_monolithic(self, ctx: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Generate all scenes in a single massive GPT call."""
        logger.info("MONOLITHIC: Generating all scenes in one call")

        model_config = ctx["model_config"] or {
            "model_name": "gpt-5.2-2025-12-11",
            "temperature": self.DEFAULT_WRITER_TEMPERATURE,
            "max_tokens": 128000,
            "seed": 42,
        }
        # Ensure high token budget for monolithic
        if model_config.get("max_tokens", 0) < 64000:
            model_config["max_tokens"] = 128000

        prompt = self.prompt_generator.generate_prompt(
            ctx["step_5_artifact"], ctx["step_3_artifact"],
            ctx["step_2_artifact"], ctx["step_1_artifact"],
        )

        raw = self.generator.generate(prompt, model_config)
        screenplay = self._parse_screenplay(raw)

        # Add metadata
        screenplay = self._add_metadata(screenplay, ctx["project_id"], prompt.get("prompt_hash", ""), model_config)
        screenplay["metadata"]["generation_mode"] = "monolithic"

        # Validate
        is_valid, errors = self.validator.validate(screenplay)
        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            save_path = self.save_artifact(screenplay, ctx["project_id"])
            return False, screenplay, error_message

        save_path = self.save_artifact(screenplay, ctx["project_id"])
        scene_count = len(screenplay.get("scenes", []))
        return True, screenplay, f"Monolithic screenplay saved to {save_path} ({scene_count} scenes)"

    # ══════════════════════════════════════════════════════════════════════
    # MODE 2: SCENE-BY-SCENE (v3.0.0 — one scene at a time, GPT self-check)
    # ══════════════════════════════════════════════════════════════════════

    def _execute_scene_by_scene(self, ctx: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Generate scenes one at a time with per-scene GPT diagnostics."""
        board_cards = ctx["board_cards"]
        scene_model_config = ctx["model_config"] or {
            "model_name": "gpt-5.2-2025-12-11",
            "temperature": self.DEFAULT_WRITER_TEMPERATURE,
            "max_tokens": 8000,
            "seed": 42,
        }
        diag_model_config = {
            "model_name": scene_model_config.get("model_name", "gpt-5.2-2025-12-11"),
            "temperature": 0.0,
            "max_tokens": 4000,
            "seed": 42,
        }

        scenes: List[Dict[str, Any]] = []
        emotions_seen: Set[str] = set()
        milestone_guidance = ""
        milestone_indices = self._get_milestone_indices(len(board_cards))
        scenes_revised = 0
        scenes_diag_passed = 0

        logger.info("SCENE-BY-SCENE: %d board cards", len(board_cards))

        for i, card in enumerate(board_cards):
            scene_number = i + 1
            card_num = card.get("card_number", scene_number)
            logger.info("--- Scene %d/%d (card %d, beat: %s) ---",
                        scene_number, len(board_cards), card_num, card.get("beat", "?"))

            prev_summary = self._build_previous_summary(scenes[-3:])

            # 1. Generate single scene
            prompt = self.prompt_generator.generate_single_scene_prompt(
                board_card=card, hero_summary=ctx["hero_summary"],
                characters_summary=ctx["characters_summary"], genre=ctx["genre"],
                logline=ctx["logline"], title=ctx["title"],
                previous_scenes_summary=prev_summary, scene_number=scene_number,
                character_identifiers=ctx["character_identifiers"],
                milestone_guidance=milestone_guidance,
            )
            raw = self.generator.generate(prompt, scene_model_config)
            scene = self._parse_single_scene(raw)
            scene["scene_number"] = scene_number
            scene["board_card_number"] = card_num

            # 2. Structural validation
            is_valid, errors = self.validator.validate_scene(scene, i)
            if not is_valid:
                logger.warning("Scene %d structural: %d errors", scene_number, len(errors))
                structural_failures = [
                    {"check_name": "Structural Format", "problem_details": e, "fix_suggestion": ""}
                    for e in errors
                ]
                revised = self._revise_scene(
                    scene, structural_failures, card, ctx["character_identifiers"],
                    prev_summary, scene_model_config,
                )
                if revised:
                    revised["scene_number"] = scene_number
                    revised["board_card_number"] = card_num
                    rev_valid, rev_errors = self.validator.validate_scene(revised, i)
                    if rev_valid or len(rev_errors) < len(errors):
                        scene = revised
                        scenes_revised += 1

            # 3. Per-scene AI diagnostic (GPT checking its own work)
            diag_result = self._run_scene_diagnostics(
                scene, ctx["hero_name"], ctx["character_identifiers"], prev_summary,
                emotions_seen, diag_model_config,
            )
            failures = diag_result.get("failures", [])
            if failures:
                logger.warning("Scene %d diagnostic: %d/%d failed", scene_number, len(failures), 5)
                revised = self._revise_scene(
                    scene, failures, card, ctx["character_identifiers"],
                    prev_summary, scene_model_config,
                )
                if revised:
                    revised["scene_number"] = scene_number
                    revised["board_card_number"] = card_num
                    rev_valid, _ = self.validator.validate_scene(revised, i)
                    if rev_valid:
                        rev_diag = self._run_scene_diagnostics(
                            revised, ctx["hero_name"], ctx["character_identifiers"], prev_summary,
                            emotions_seen, diag_model_config,
                        )
                        if not rev_diag.get("failures", []):
                            scene = revised
                            scenes_revised += 1
                            scenes_diag_passed += 1
                            rev_emotion = rev_diag.get("emotion_hit", "")
                            if rev_emotion:
                                diag_result["emotion_hit"] = rev_emotion
            else:
                scenes_diag_passed += 1

            emotion = diag_result.get("emotion_hit", "")
            if emotion:
                emotions_seen.add(emotion.lower().strip())
            scenes.append(scene)

            if scene_number in milestone_indices:
                guidance = self._run_milestone_check(
                    scenes, scene_number, ctx["hero_name"], ctx["antagonist_name"],
                    ctx["characters_summary"], diag_model_config,
                )
                if guidance:
                    milestone_guidance = guidance

        # Assemble
        screenplay = self._assemble_screenplay(
            scenes, ctx["title"], ctx["logline"], ctx["genre"], ctx["format_value"],
        )
        screenplay = self._add_metadata(screenplay, ctx["project_id"], "", scene_model_config)
        screenplay["metadata"]["generation_mode"] = "scene_by_scene"
        screenplay["metadata"]["scenes_revised"] = scenes_revised
        screenplay["metadata"]["scenes_diag_clean"] = scenes_diag_passed

        is_valid, errors = self.validator.validate(screenplay)
        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            self.save_artifact(screenplay, ctx["project_id"])
            return False, screenplay, error_message

        save_path = self.save_artifact(screenplay, ctx["project_id"])
        return True, screenplay, f"Scene-by-scene screenplay saved ({len(scenes)} scenes, {scenes_revised} revised)"

    # ══════════════════════════════════════════════════════════════════════
    # MODE 3: ACT-BY-ACT (v4.0.0 — GPT writes acts, Grok checks, GPT revises)
    # ══════════════════════════════════════════════════════════════════════

    def _execute_act_by_act(self, ctx: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate screenplay act by act with Grok as independent checker.

        For each act (~10 scenes):
          1. GPT writes all scenes for the act in one call
          2. Grok evaluates the act with fresh eyes (9 Ch.7 checks + Covenant of the Arc)
          3. If Grok finds problems, GPT rewrites based on Grok's specific feedback
          4. Move to next act with completed acts as context
        """
        board_cards = ctx["board_cards"]

        # Split cards into acts
        acts = self._split_into_acts(board_cards)

        # Runtime controls (override with env vars)
        # These are intentionally high by default to prioritize completion quality.
        writer_temp = self._env_float("SCREENPLAY_WRITER_TEMP", self.DEFAULT_WRITER_TEMPERATURE)
        writer_min_tokens = self._env_int(
            "SCREENPLAY_WRITER_MAX_TOKENS",
            self.DEFAULT_WRITER_MAX_TOKENS,
            minimum=32000,
        )
        checker_tokens = self._env_int(
            "SCREENPLAY_CHECKER_MAX_TOKENS",
            self.DEFAULT_CHECKER_MAX_TOKENS,
            minimum=8000,
        )
        revision_tokens = self._env_int(
            "SCREENPLAY_REVISION_MAX_TOKENS",
            self.DEFAULT_REVISION_MAX_TOKENS,
            minimum=8000,
        )
        max_revisions = self._env_int(
            "SCREENPLAY_MAX_REVISIONS",
            self.DEFAULT_MAX_REVISIONS,
            minimum=1,
        )

        # Check for model swap: SCREENPLAY_SWAP_MODELS=1 -> Grok writes, GPT reviews
        swap_models = os.getenv("SCREENPLAY_SWAP_MODELS", "").lower() in ("1", "true", "yes")

        if swap_models:
            logger.info("MODEL SWAP ENABLED: Grok writes, GPT reviews")
            # Grok as writer
            try:
                writer = AIGenerator(provider="xai")
            except Exception as e:
                logger.error("Failed to init Grok writer: %s — aborting swap", e)
                writer = self.generator
            writer_config = dict(ctx["model_config"] or {
                "model_name": "grok-4-1-fast-reasoning",
                "temperature": writer_temp,
                "max_tokens": writer_min_tokens,
            })
            # GPT as checker
            checker = self.generator  # already OpenAI
            checker_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.0,
                "max_tokens": checker_tokens,
            }
        else:
            logger.info("DEFAULT MODELS: GPT writes, Grok reviews")
            writer = self.generator
            # Writer model config — GPT for generation
            writer_config = dict(ctx["model_config"] or {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": writer_temp,
                "max_tokens": writer_min_tokens,  # ~10 scenes per act with full context
                "seed": 42,
            })
            # Initialize Grok checker
            try:
                checker = AIGenerator(provider="xai")
                checker_config = {
                    "model_name": "grok-4-1-fast-reasoning",
                    "temperature": 0.0,
                    "max_tokens": checker_tokens,
                }
                logger.info("Grok checker initialized (xAI)")
            except Exception as e:
                logger.error("Failed to initialize Grok checker: %s — falling back to GPT self-check", e)
                checker = self.generator
                checker_config = {
                    "model_name": writer_config.get("model_name", "gpt-5.2-2025-12-11"),
                    "temperature": 0.0,
                    "max_tokens": checker_tokens,
                }

        # Apply defaults/overrides regardless of branch
        if "temperature" not in writer_config:
            writer_config["temperature"] = writer_temp
        if writer_config.get("max_tokens", 0) < writer_min_tokens:
            writer_config["max_tokens"] = writer_min_tokens
        if checker_config.get("max_tokens", 0) < checker_tokens:
            checker_config["max_tokens"] = checker_tokens

        all_scenes: List[Dict[str, Any]] = []
        acts_revised = 0
        total_grok_failures = 0

        logger.info("ACT-BY-ACT GENERATION: %d acts, %d total cards", len(acts), len(board_cards))

        for act_idx, (act_label, act_cards) in enumerate(acts):
            start_scene = len(all_scenes) + 1
            logger.info("=" * 50)
            logger.info("ACT %d/%d: %s (%d cards, starting scene %d)",
                        act_idx + 1, len(acts), act_label, len(act_cards), start_scene)

            # 1. GPT writes all scenes for this act
            act_prompt = self.prompt_generator.generate_act_prompt(
                act_cards=act_cards,
                hero_summary=ctx["hero_summary"],
                characters_summary=ctx["characters_summary"],
                genre=ctx["genre"],
                logline=ctx["logline"],
                title=ctx["title"],
                previous_scenes=all_scenes,
                character_identifiers=ctx["character_identifiers"],
                act_label=act_label,
                start_scene_number=start_scene,
            )

            writer_label = "Grok" if swap_models else "GPT"
            logger.info(
                "Generating %s with %s (temp=%.2f, writer_tokens=%d, checker_tokens=%d)...",
                act_label,
                writer_label,
                float(writer_config.get("temperature", 0.0)),
                int(writer_config.get("max_tokens", 0)),
                int(checker_config.get("max_tokens", 0)),
            )
            raw = writer.generate(act_prompt, writer_config)
            act_scenes = self._parse_act_scenes(raw, start_scene)

            if not act_scenes:
                logger.error("%s: GPT returned no parseable scenes!", act_label)
                continue

            logger.info("%s: %s generated %d scenes", act_label, writer_label, len(act_scenes))

            # Structural validation on each scene
            for i, scene in enumerate(act_scenes):
                scene_idx = len(all_scenes) + i
                is_valid, errors = self.validator.validate_scene(scene, scene_idx)
                if not is_valid:
                    logger.warning("  Scene %d structural: %d errors", scene.get("scene_number", "?"), len(errors))

            # 2. Grok evaluates the act with fresh eyes
            logger.info("Grok checking %s...", act_label)
            diag_prompt = self.prompt_generator.generate_act_diagnostic_prompt(
                act_scenes=act_scenes,
                hero_name=ctx["hero_name"],
                antagonist_name=ctx["antagonist_name"],
                characters_summary=ctx["characters_summary"],
                character_identifiers=ctx["character_identifiers"],
                act_label=act_label,
                previous_scenes=all_scenes,
            )

            try:
                diagnostics = self._run_act_checker_with_retry(
                    checker=checker,
                    checker_config=checker_config,
                    diag_prompt=diag_prompt,
                    act_label=act_label,
                    phase="initial check",
                )
                failures = [d for d in diagnostics if not d.get("passed", True)]
                passed = sum(1 for d in diagnostics if d.get("passed", True))

                logger.info("Grok %s result: %d/%d passed", act_label, passed, len(diagnostics))
                for f in failures:
                    logger.warning("  FAIL: %s — %s", f.get("check_name", "?"),
                                  f.get("problem_details", "")[:120])
                    total_grok_failures += 1

            except Exception as e:
                logger.error("Checker diagnostic failed for %s: %s", act_label, e)
                return False, {}, (
                    f"Checker diagnostic failed for {act_label}: {e}. "
                    "Refusing to continue with unverified act output."
                )

            # 3. Revision loop: Grok found problems → GPT rewrites ONLY broken scenes → Grok re-checks
            MAX_REVISIONS = max_revisions
            revision_round = 0

            # Use smaller token limit for targeted scene revisions (not full act)
            revision_config = dict(writer_config)
            revision_config["max_tokens"] = revision_tokens  # Targeted rewrites only

            while failures and revision_round < MAX_REVISIONS:
                revision_round += 1

                # Count how many specific scenes are broken
                failing_scene_nums = set()
                for f in failures:
                    for sn in f.get("failing_scene_numbers", []):
                        failing_scene_nums.add(int(sn))
                # Fallback: extract scene numbers from problem text
                if not failing_scene_nums:
                    import re as _re
                    for f in failures:
                        found = _re.findall(r"[Ss]cene\s+(\d+)", f.get("problem_details", ""))
                        for sn_str in found:
                            failing_scene_nums.add(int(sn_str))

                logger.info("Revising %s round %d/%d — %d scenes broken (%s), %d checks failing...",
                            act_label, revision_round, MAX_REVISIONS,
                            len(failing_scene_nums), sorted(failing_scene_nums),
                            len(failures))

                revision_prompt = self.prompt_generator.generate_act_revision_prompt(
                    act_scenes=act_scenes,
                    failures=failures,
                    act_cards=act_cards,
                    hero_summary=ctx["hero_summary"],
                    characters_summary=ctx["characters_summary"],
                    character_identifiers=ctx["character_identifiers"],
                    previous_scenes=all_scenes,
                    act_label=act_label,
                    title=ctx["title"],
                    logline=ctx["logline"],
                    genre=ctx["genre"],
                    revision_round=revision_round,
                )

                try:
                    revised_raw = writer.generate(revision_prompt, revision_config)
                    revised_scenes = self._parse_act_scenes(revised_raw, start_scene)

                    if revised_scenes:
                        # Merge: replace ONLY the revised scenes, keep the rest unchanged
                        revised_by_num = {s.get("scene_number"): s for s in revised_scenes}
                        merged_count = 0
                        for idx, orig_scene in enumerate(act_scenes):
                            sn = orig_scene.get("scene_number")
                            if sn in revised_by_num:
                                act_scenes[idx] = revised_by_num[sn]
                                merged_count += 1
                        acts_revised += 1
                        logger.info("%s revision %d: merged %d revised scenes (of %d broken)",
                                    act_label, revision_round, merged_count, len(failing_scene_nums))
                    else:
                        logger.warning("%s revision %d: GPT returned 0 scenes, keeping previous",
                                      act_label, revision_round)
                        break
                except Exception as e:
                    logger.error("%s revision %d failed: %s — keeping previous", act_label, revision_round, e)
                    break

                # Re-evaluate with Grok after revision
                logger.info("Grok re-checking %s after revision %d...", act_label, revision_round)
                diag_prompt = self.prompt_generator.generate_act_diagnostic_prompt(
                    act_scenes=act_scenes,
                    hero_name=ctx["hero_name"],
                    antagonist_name=ctx["antagonist_name"],
                    characters_summary=ctx["characters_summary"],
                    character_identifiers=ctx["character_identifiers"],
                    act_label=act_label,
                    previous_scenes=all_scenes,
                )

                try:
                    diagnostics = self._run_act_checker_with_retry(
                        checker=checker,
                        checker_config=checker_config,
                        diag_prompt=diag_prompt,
                        act_label=act_label,
                        phase=f"revision {revision_round} re-check",
                    )
                    failures = [d for d in diagnostics if not d.get("passed", True)]
                    passed = sum(1 for d in diagnostics if d.get("passed", True))

                    logger.info("Grok re-check %s round %d: %d/%d passed",
                                act_label, revision_round, passed, len(diagnostics))
                    for f in failures:
                        failing_nums = f.get("failing_scene_numbers", [])
                        logger.warning("  STILL FAILING: %s (scenes %s) — %s",
                                      f.get("check_name", "?"), failing_nums,
                                      f.get("problem_details", "")[:150])
                        total_grok_failures += 1

                    if not failures:
                        logger.info("%s: Grok approved after %d revision(s)", act_label, revision_round)

                except Exception as e:
                    logger.error("Checker re-check failed for %s round %d: %s", act_label, revision_round, e)
                    return False, {}, (
                        f"Checker re-check failed for {act_label} round {revision_round}: {e}. "
                        "Refusing to continue with unverified act output."
                    )

            if not failures and revision_round == 0:
                logger.info("%s: Grok approved — no revision needed", act_label)
            elif failures and revision_round >= MAX_REVISIONS:
                remaining = [f.get("check_name", "?") for f in failures]
                failing_scenes = set()
                for f in failures:
                    for sn in f.get("failing_scene_numbers", []):
                        failing_scenes.add(int(sn))
                logger.warning("%s: %d checks still failing after %d revisions: %s (scenes: %s)",
                              act_label, len(failures), MAX_REVISIONS,
                              ", ".join(remaining), sorted(failing_scenes))

            all_scenes.extend(act_scenes)

        # Assemble full screenplay
        logger.info("=" * 50)
        logger.info("ASSEMBLY: %d scenes from %d acts (%d acts revised, %d total Grok failures)",
                    len(all_scenes), len(acts), acts_revised, total_grok_failures)

        screenplay = self._assemble_screenplay(
            all_scenes, ctx["title"], ctx["logline"], ctx["genre"], ctx["format_value"],
        )
        screenplay = self._add_metadata(screenplay, ctx["project_id"], "", writer_config)
        screenplay["metadata"]["generation_mode"] = "act_by_act"
        screenplay["metadata"]["acts_revised"] = acts_revised
        screenplay["metadata"]["total_grok_failures"] = total_grok_failures
        screenplay["metadata"]["checker_model"] = checker_config.get("model_name", "unknown")

        # Full validation
        is_valid, errors = self.validator.validate(screenplay)
        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            self.save_artifact(screenplay, ctx["project_id"])
            return False, screenplay, error_message

        save_path = self.save_artifact(screenplay, ctx["project_id"])
        return True, screenplay, (
            f"Act-by-act screenplay saved to {save_path} "
            f"({len(all_scenes)} scenes, {acts_revised} acts revised by Grok feedback)"
        )

    def _split_into_acts(self, board_cards: List[Dict[str, Any]]) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """Split board cards into acts based on ACT_DEFINITIONS."""
        acts = []
        for label, start, end in ACT_DEFINITIONS:
            if end is None:
                act_cards = board_cards[start:]
            else:
                act_cards = board_cards[start:end]
            if act_cards:
                acts.append((label, act_cards))
        return acts

    @staticmethod
    def _env_int(name: str, default: int, minimum: Optional[int] = None) -> int:
        raw = os.getenv(name, "").strip()
        if not raw:
            value = default
        else:
            try:
                value = int(raw)
            except ValueError:
                logger.warning("Invalid %s=%r; using default %d", name, raw, default)
                value = default
        if minimum is not None and value < minimum:
            value = minimum
        return value

    @staticmethod
    def _env_float(name: str, default: float) -> float:
        raw = os.getenv(name, "").strip()
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            logger.warning("Invalid %s=%r; using default %.3f", name, raw, default)
            return default

    def _run_act_checker_with_retry(
        self,
        checker: AIGenerator,
        checker_config: Dict[str, Any],
        diag_prompt: Dict[str, str],
        act_label: str,
        phase: str,
    ) -> List[Dict[str, Any]]:
        """
        Run act-level diagnostics with retry and strict schema validation.

        This prevents silent acceptance of malformed/partial checker output.
        """
        retries = self._env_int(
            "SCREENPLAY_CHECKER_RETRIES",
            self.DEFAULT_CHECKER_RETRIES,
            minimum=1,
        )
        last_error: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            try:
                diag_raw = checker.generate(diag_prompt, checker_config)
                logger.debug(
                    "Grok %s raw attempt %d/%d (%d chars): %s",
                    phase, attempt, retries, len(diag_raw), diag_raw[:500],
                )
                diagnostics = self._extract_diagnostics_from_raw(diag_raw, act_label)
                return diagnostics
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    logger.warning(
                        "Checker %s failed for %s (attempt %d/%d): %s; retrying",
                        phase, act_label, attempt, retries, exc,
                    )
                else:
                    logger.error(
                        "Checker %s failed for %s after %d/%d attempts: %s",
                        phase, act_label, attempt, retries, exc,
                    )

        raise last_error or RuntimeError(
            f"Checker {phase} failed for {act_label} with unknown error"
        )

    def _extract_diagnostics_from_raw(
        self,
        raw_content: str,
        act_label: str,
    ) -> List[Dict[str, Any]]:
        """Parse checker raw output and validate diagnostics schema."""
        parsed = self._parse_json_response(raw_content)

        diagnostics: Any = []
        if isinstance(parsed, dict):
            diagnostics = parsed.get("diagnostics", [])
            if not diagnostics and isinstance(parsed.get("_list"), list):
                diagnostics = parsed.get("_list")

        # Some models return a bare list instead of an object.
        if not diagnostics:
            stripped = (raw_content or "").strip()
            if stripped.startswith("["):
                try:
                    arr = json.loads(stripped)
                    if isinstance(arr, list):
                        diagnostics = arr
                except Exception:
                    pass

        if not isinstance(diagnostics, list):
            raise ValueError(
                f"Checker output for {act_label} has non-list diagnostics payload: {type(diagnostics).__name__}"
            )

        dict_diagnostics = [d for d in diagnostics if isinstance(d, dict)]
        if len(dict_diagnostics) != len(diagnostics):
            raise ValueError(
                f"Checker output for {act_label} contains non-object diagnostics entries"
            )
        if len(dict_diagnostics) < 10:
            raise ValueError(
                f"Checker output for {act_label} is incomplete: {len(dict_diagnostics)} checks (expected 10)"
            )

        required_keys = {"check_number", "check_name", "passed"}
        for idx, diag in enumerate(dict_diagnostics):
            missing = required_keys - set(diag.keys())
            if missing:
                raise ValueError(
                    f"Checker diagnostic #{idx + 1} for {act_label} missing keys: {sorted(missing)}"
                )

        return dict_diagnostics

    def _parse_act_scenes(self, raw_content: str, start_scene: int) -> List[Dict[str, Any]]:
        """Parse GPT output containing multiple scenes for one act."""
        if not raw_content:
            return []

        parsed = self._parse_json_response(raw_content)

        # Try "scenes" key
        scenes = parsed.get("scenes", [])
        if not scenes and isinstance(parsed, dict):
            # Maybe the root IS a single scene
            if "elements" in parsed:
                scenes = [parsed]

        if not scenes:
            # Try parsing as array
            try:
                stripped = raw_content.strip()
                if stripped.startswith("["):
                    scenes = json.loads(stripped)
            except json.JSONDecodeError:
                pass

        # Assign scene numbers if missing
        for i, scene in enumerate(scenes):
            if not scene.get("scene_number"):
                scene["scene_number"] = start_scene + i
            if not scene.get("board_card_number"):
                scene["board_card_number"] = scene.get("scene_number", start_scene + i)

        return scenes

    # ── Scene-by-Scene Helpers ────────────────────────────────────────────

    def _build_hero_summary(self, step_3_artifact: Dict[str, Any]) -> str:
        """Build hero summary string from step 3 artifact."""
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        return (
            f"Name: {hero.get('name', 'MISSING')}\n"
            f"Archetype: {hero.get('archetype', 'MISSING')}\n"
            f"Motivation: {hero.get('primal_motivation', hero.get('stated_goal', 'MISSING'))}\n"
            f"Arc: {hero.get('opening_state', 'MISSING')} -> {hero.get('final_state', 'MISSING')}"
        )

    def _build_characters_summary(self, step_3_artifact: Dict[str, Any]) -> str:
        """Build characters summary string from step 3 artifact."""
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        parts = [f"Hero: {hero.get('name', 'MISSING')}"]

        antagonist = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        if antagonist:
            parts.append(f"Antagonist: {antagonist.get('name', 'MISSING')} - {antagonist.get('adjective_descriptor', '')}")

        b_story = step_3_artifact.get("b_story_character", step_3_artifact.get("b_story", {}))
        if b_story:
            parts.append(f"B-Story: {b_story.get('name', 'MISSING')} - {b_story.get('relationship_to_hero', '')}")

        supporting_chars = step_3_artifact.get("supporting_characters")
        if not isinstance(supporting_chars, list):
            supporting_cast = step_3_artifact.get("supporting_cast", {})
            if isinstance(supporting_cast, dict):
                supporting_chars = supporting_cast.get("characters", [])

        if isinstance(supporting_chars, list) and supporting_chars:
            labels = []
            for char in supporting_chars:
                if not isinstance(char, dict):
                    continue
                name = (char.get("name") or "").strip()
                if not name:
                    continue
                role = (char.get("role") or "").strip()
                labels.append(f"{name} ({role})" if role else name)
            if labels:
                parts.append("Supporting Cast: " + ", ".join(labels))

        return "\n".join(parts)

    def _build_character_identifiers(self, step_3_artifact: Dict[str, Any]) -> str:
        """
        Build character voice guide from step 3 artifact, using full prose
        character biographies when available.
        """
        sections = []
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        hero_name = hero.get("name", "HERO")

        # Hero
        hero_bio = (hero.get("character_biography") or "").strip()
        hero_archetype = hero.get("archetype", "")
        if hero_bio:
            sections.append(
                f"=== {hero_name} (HERO — {hero_archetype}) ===\n"
                f"{hero_bio}\n"
                f"Arc: {hero.get('opening_state', '?')} → {hero.get('final_state', '?')}"
            )
        else:
            sections.append(
                f"=== {hero_name} (HERO — {hero_archetype}) ===\n"
                f"Goal: {hero.get('stated_goal', '?')}\n"
                f"Need: {hero.get('actual_need', '?')}\n"
                f"Arc: {hero.get('opening_state', '?')} → {hero.get('final_state', '?')}"
            )

        # Antagonist
        antagonist = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        if antagonist and antagonist.get("name"):
            antag_name = antagonist["name"]
            antag_bio = (antagonist.get("character_biography") or "").strip()
            antag_adj = antagonist.get("adjective_descriptor", "")
            if antag_bio:
                sections.append(
                    f"=== {antag_name} (ANTAGONIST — {antag_adj}) ===\n"
                    f"{antag_bio}\n"
                    f"Does NOT arc. Refuses to change — that's why they lose."
                )
            else:
                sections.append(
                    f"=== {antag_name} (ANTAGONIST — {antag_adj}) ===\n"
                    f"Mirror: {antagonist.get('mirror_principle', '?')}\n"
                    f"Moral line: {antagonist.get('moral_difference', '?')}\n"
                    f"Does NOT arc. Refuses to change."
                )

        # B-story
        b_story = step_3_artifact.get("b_story_character", step_3_artifact.get("b_story", {}))
        if b_story and b_story.get("name"):
            b_name = b_story["name"]
            b_bio = (b_story.get("character_biography") or "").strip()
            b_rel = b_story.get("relationship_to_hero", "")
            if b_bio:
                sections.append(
                    f"=== {b_name} (B-STORY — {b_rel}) ===\n"
                    f"{b_bio}\n"
                    f"Arc: {b_story.get('opening_state', '?')} → {b_story.get('final_state', '?')}"
                )
            else:
                sections.append(
                    f"=== {b_name} (B-STORY — {b_rel}) ===\n"
                    f"Theme wisdom: {b_story.get('theme_wisdom', '?')}\n"
                    f"Arc: {b_story.get('opening_state', '?')} → {b_story.get('final_state', '?')}"
                )

        # Supporting cast (Step 3b, merged by orchestrator into step_3_artifact)
        supporting_chars = step_3_artifact.get("supporting_characters")
        if not isinstance(supporting_chars, list):
            supporting_cast = step_3_artifact.get("supporting_cast", {})
            if isinstance(supporting_cast, dict):
                supporting_chars = supporting_cast.get("characters", [])

        if isinstance(supporting_chars, list):
            for char in supporting_chars:
                if not isinstance(char, dict):
                    continue
                name = (char.get("name") or "").strip()
                if not name:
                    continue
                role = (char.get("role") or "").strip()
                rel = (char.get("relationship_to_hero") or "").strip()
                trait = (char.get("distinctive_trait") or "").strip()
                voice = (char.get("voice_profile") or "").strip()
                arc = (char.get("arc_summary") or "").strip()
                bio = (char.get("character_biography") or "").strip()

                heading = f"=== {name} (SUPPORTING"
                if role:
                    heading += f" — {role}"
                heading += ") ==="

                if bio:
                    block_lines = [
                        heading,
                        bio,
                    ]
                else:
                    block_lines = [heading]
                    if rel:
                        block_lines.append(f"Relationship to hero: {rel}")
                    if trait:
                        block_lines.append(f"Distinctive trait: {trait}")
                    if voice:
                        block_lines.append(f"Voice profile: {voice}")
                    if arc:
                        block_lines.append(f"Arc summary: {arc}")

                sections.append("\n".join(block_lines))

        return "\n\n".join(sections) if sections else "(No character data available.)"

    def _build_previous_summary(self, last_n_scenes: List[Dict[str, Any]]) -> str:
        """Build continuity summary from last N scenes (slugline + conflict + emotional arc)."""
        if not last_n_scenes:
            return ""

        parts = []
        for s in last_n_scenes:
            num = s.get("scene_number", "?")
            slug = s.get("slugline", "?")
            conflict = s.get("conflict", "?")
            e_start = s.get("emotional_start", "?")
            e_end = s.get("emotional_end", "?")
            beat = s.get("beat", "?")
            # Truncate conflict to keep context lean
            if len(conflict) > 100:
                conflict = conflict[:100] + "..."
            parts.append(
                f"Scene {num} [{beat}] {slug} | "
                f"Conflict: {conflict} | "
                f"Emotion: {e_start} -> {e_end}"
            )

        return "\n".join(parts)

    def _parse_single_scene(self, raw_content: str) -> Dict[str, Any]:
        """Parse AI output into a single scene dict. Never raises."""
        if not raw_content:
            return self._empty_scene()

        # Try markdown code block
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
            if code_match:
                parsed = json.loads(code_match.group(1))
                if isinstance(parsed, dict) and "elements" in parsed:
                    return parsed
        except (json.JSONDecodeError, AttributeError):
            pass

        # Try direct JSON
        try:
            stripped = raw_content.strip()
            if stripped.startswith("{"):
                parsed = json.loads(stripped)
                if isinstance(parsed, dict) and "elements" in parsed:
                    return parsed
        except json.JSONDecodeError:
            pass

        # Try extracting largest JSON object
        try:
            start = raw_content.index("{")
            end = raw_content.rindex("}") + 1
            parsed = json.loads(raw_content[start:end])
            if isinstance(parsed, dict) and "elements" in parsed:
                return parsed
            # Maybe it's a wrapper with a scene inside
            if isinstance(parsed, dict) and "scene" in parsed:
                scene = parsed["scene"]
                if isinstance(scene, dict) and "elements" in scene:
                    return scene
        except (json.JSONDecodeError, ValueError):
            pass

        return self._empty_scene()

    def _empty_scene(self) -> Dict[str, Any]:
        """Return an empty scene structure."""
        return {
            "scene_number": 0, "slugline": "", "int_ext": "INT.",
            "location": "", "time_of_day": "DAY",
            "elements": [], "estimated_duration_seconds": 0,
            "beat": "", "emotional_start": "+", "emotional_end": "-",
            "conflict": "", "characters_present": [], "board_card_number": 0,
        }

    def _revise_scene(
        self,
        scene: Dict[str, Any],
        failures: List[Dict[str, Any]],
        board_card: Dict[str, Any],
        character_identifiers: str,
        previous_scenes_summary: str,
        model_config: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Revise a scene that failed structural or diagnostic checks."""
        try:
            prompt = self.prompt_generator.generate_scene_revision_prompt(
                scene, failures, board_card, character_identifiers, previous_scenes_summary,
            )
            raw = self.generator.generate(prompt, model_config)
            return self._parse_single_scene(raw)
        except Exception as e:
            logger.error("Scene revision failed: %s", e)
            return None

    def _run_scene_diagnostics(
        self,
        scene: Dict[str, Any],
        hero_name: str,
        character_identifiers: str,
        previous_scenes_summary: str,
        emotions_seen: Set[str],
        model_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run per-scene AI diagnostic (5 Ch.7 checks) on a single scene.

        Returns dict with 'failures' (list of failure dicts), 'emotion_hit' (str),
        'total_checks' (int), 'checks_passed' (int).
        """
        emotions_str = ", ".join(sorted(emotions_seen)) if emotions_seen else ""

        prompt = self.prompt_generator.generate_scene_diagnostic_prompt(
            scene=scene,
            hero_name=hero_name,
            character_identifiers=character_identifiers,
            previous_scenes_summary=previous_scenes_summary,
            emotions_seen_so_far=emotions_str,
        )

        try:
            raw = self.generator.generate(prompt, model_config)
            result = self._parse_diagnostic_response(raw)
            return result
        except Exception as e:
            logger.error("Scene diagnostic AI call failed: %s", e)
            return {"failures": [], "emotion_hit": "", "total_checks": 0, "checks_passed": 0}

    def _parse_diagnostic_response(self, raw_content: str) -> Dict[str, Any]:
        """Parse the AI diagnostic response into a structured result."""
        artifact = self._parse_json_response(raw_content)
        diagnostics = artifact.get("diagnostics", [])

        failures = [d for d in diagnostics if not d.get("passed", True)]
        checks_passed = sum(1 for d in diagnostics if d.get("passed", False))

        # Extract emotion_hit from Emotional Color Wheel check
        emotion_hit = ""
        for d in diagnostics:
            if d.get("check_number") == 5 or "Color Wheel" in d.get("check_name", ""):
                emotion_hit = d.get("emotion_hit", "")
                break

        return {
            "failures": failures,
            "emotion_hit": emotion_hit,
            "total_checks": len(diagnostics),
            "checks_passed": checks_passed,
        }

    def _parse_json_response(self, raw_content: str) -> Dict[str, Any]:
        """Generic JSON parser for AI responses. Handles reasoning model output. Never raises."""
        if not raw_content:
            return {}

        # Strip <think>...</think> blocks from reasoning models
        cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
        cleaned = cleaned.replace("\x00", "")
        decoder = json.JSONDecoder()

        # 1. Try code-fenced JSON
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
            if code_match:
                return json.loads(code_match.group(1))
        except (json.JSONDecodeError, AttributeError):
            pass

        # 2. Try direct parse (response is pure JSON)
        try:
            stripped = cleaned.strip()
            if stripped.startswith("{"):
                return json.loads(stripped)
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return {"_list": parsed}
        except json.JSONDecodeError:
            pass

        # 3. Parse first JSON object from the first '{' using raw_decode.
        # This handles trailing prose after valid JSON, which is common with reasoning models.
        for match in re.finditer(r"\{", cleaned):
            start = match.start()
            try:
                parsed, _ = decoder.raw_decode(cleaned[start:])
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {"_list": parsed}
            except json.JSONDecodeError:
                continue

        # 4. Find outermost { ... } using bracket counting (legacy fallback).
        try:
            # Search backwards from end to find the main JSON object
            depth = 0
            end_pos = -1
            start_pos = -1
            for i in range(len(cleaned) - 1, -1, -1):
                c = cleaned[i]
                if c == '}':
                    if depth == 0:
                        end_pos = i
                    depth += 1
                elif c == '{':
                    depth -= 1
                    if depth == 0:
                        start_pos = i
                        break

            if start_pos >= 0 and end_pos > start_pos:
                candidate = cleaned[start_pos:end_pos + 1]
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
                if isinstance(result, list):
                    return {"_list": result}
        except (json.JSONDecodeError, ValueError):
            pass

        # 5. Last resort: find first { to last } (old approach)
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            result = json.loads(cleaned[start:end])
            if isinstance(result, dict):
                return result
            if isinstance(result, list):
                return {"_list": result}
        except (json.JSONDecodeError, ValueError):
            pass

        logger.warning("_parse_json_response: Could not parse JSON from %d chars. First 300: %s",
                       len(raw_content), raw_content[:300])
        return {}

    def _get_milestone_indices(self, total_cards: int) -> List[int]:
        """Return scene numbers at which to run milestone diagnostics."""
        if total_cards <= 10:
            return []
        # Approximately: end of Act 1, Midpoint, end of Act 2B
        act1_end = min(10, total_cards)
        midpoint = min(20, total_cards)
        act2b_end = min(30, total_cards)
        milestones = []
        if act1_end < total_cards:
            milestones.append(act1_end)
        if midpoint < total_cards:
            milestones.append(midpoint)
        if act2b_end < total_cards:
            milestones.append(act2b_end)
        return milestones

    def _run_milestone_check(
        self,
        scenes: List[Dict[str, Any]],
        scene_number: int,
        hero_name: str,
        antagonist_name: str,
        characters_summary: str,
        model_config: Dict[str, Any],
    ) -> str:
        """
        Run milestone diagnostic at an act break. Returns guidance string
        for upcoming scenes, or empty string if all checks pass.
        """
        # Determine milestone label and applicable checks
        if scene_number <= 10:
            label = "Act 1"
        elif scene_number <= 20:
            label = "Midpoint"
        else:
            label = "Act 2B"

        applicable_checks = MILESTONE_CHECKS.get(label, "")
        if not applicable_checks:
            return ""

        # Build scenes summary (condensed — not full JSON)
        summary_parts = []
        for s in scenes:
            num = s.get("scene_number", "?")
            slug = s.get("slugline", "?")
            beat = s.get("beat", "?")
            conflict = s.get("conflict", "?")[:80]
            e_start = s.get("emotional_start", "?")
            e_end = s.get("emotional_end", "?")
            # Include first dialogue line for voice check
            first_dialogue = ""
            for elem in s.get("elements", []):
                if elem.get("element_type") == "dialogue":
                    first_dialogue = elem.get("content", "")[:60]
                    break
            summary_parts.append(
                f"Scene {num} [{beat}] {slug} | {e_start}->{e_end} | {conflict}"
                + (f" | Dialogue: \"{first_dialogue}...\"" if first_dialogue else "")
            )
        scenes_summary = "\n".join(summary_parts)

        prompt = self.prompt_generator.generate_milestone_diagnostic_prompt(
            scenes_summary=scenes_summary,
            hero_name=hero_name,
            antagonist_name=antagonist_name,
            characters_summary=characters_summary,
            milestone_label=label,
            applicable_checks=applicable_checks,
        )

        try:
            raw = self.generator.generate(prompt, model_config)
            result = self._parse_json_response(raw)
            diagnostics = result.get("diagnostics", [])

            # Collect guidance from failures
            guidance_parts = []
            for d in diagnostics:
                if not d.get("passed", True):
                    guidance = d.get("guidance_for_upcoming_scenes", "")
                    if guidance:
                        guidance_parts.append(f"[{d.get('check_name', '?')}] {guidance}")

            if guidance_parts:
                logger.warning("Milestone %s: %d checks failed", label, len(guidance_parts))
                return "\n".join(guidance_parts)

            logger.info("Milestone %s: ALL PASSED", label)
            return ""

        except Exception as e:
            logger.error("Milestone check failed: %s", e)
            return ""

    def _assemble_screenplay(
        self,
        scenes: List[Dict[str, Any]],
        title: str,
        logline: str,
        genre: str,
        format_value: str,
    ) -> Dict[str, Any]:
        """Assemble individual scenes into a full screenplay artifact."""
        total_duration = sum(
            s.get("estimated_duration_seconds", 0)
            for s in scenes
            if isinstance(s.get("estimated_duration_seconds"), (int, float))
        )
        total_pages = total_duration / 60.0 if total_duration > 0 else 0.0

        return {
            "title": title,
            "author": "AI Generated",
            "format": format_value,
            "genre": genre,
            "logline": logline,
            "total_pages": round(total_pages, 1),
            "estimated_duration_seconds": total_duration,
            "scenes": scenes,
        }

    # ── Legacy Parsers (kept for backward compatibility with revise()) ────

    def _parse_screenplay(self, raw_content: str) -> Dict[str, Any]:
        """Parse AI output into a screenplay dict. Never raises."""
        # Try extracting JSON from markdown code blocks
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_content, re.DOTALL)
            if code_match:
                parsed = json.loads(code_match.group(1))
                if isinstance(parsed, dict) and "scenes" in parsed:
                    return parsed
        except Exception:
            pass

        # Try direct JSON parse
        try:
            stripped = raw_content.strip()
            if stripped.startswith("{"):
                parsed = json.loads(stripped)
                if isinstance(parsed, dict) and "scenes" in parsed:
                    return parsed
        except Exception:
            pass

        # Try to find the largest JSON object containing "scenes"
        try:
            start = raw_content.index("{")
            end = raw_content.rindex("}") + 1
            parsed = json.loads(raw_content[start:end])
            if isinstance(parsed, dict) and "scenes" in parsed:
                return parsed
        except Exception:
            pass

        return {
            "title": "", "author": "AI Generated", "format": "feature",
            "genre": "", "logline": "", "total_pages": 0.0,
            "estimated_duration_seconds": 0, "scenes": []
        }

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_5_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 8 artifact due to downstream conflicts.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            step_5_artifact: The Board with 40 scene cards
            step_3_artifact: Hero / characters artifact
            step_2_artifact: Genre classification artifact
            step_1_artifact: Logline / title artifact
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 8 artifact found for project {project_id}"

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            [revision_reason],
            step_5_artifact,
            step_3_artifact,
            step_2_artifact,
            step_1_artifact,
        )

        # Default model config for screenplay revision — needs high token budget
        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": self.DEFAULT_WRITER_TEMPERATURE,
                "max_tokens": 128000,
            }

        # Call AI for revision
        try:
            artifact_content = self.generator.generate_with_validation(
                prompt_data, self.validator, model_config
            )
        except Exception as e:
            return False, {}, f"AI revision failed: {e}"

        # Update version
        old_version = current_artifact.get("metadata", {}).get("version", "1.0.0")
        major, minor, patch = map(int, old_version.split("."))
        new_version = f"{major}.{minor + 1}.0"

        # Add metadata
        artifact = self._add_metadata(
            artifact_content,
            project_id,
            prompt_data["prompt_hash"],
            model_config or {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": self.DEFAULT_WRITER_TEMPERATURE,
            },
        )
        artifact["metadata"]["version"] = new_version
        artifact["metadata"]["revision_reason"] = revision_reason
        artifact["metadata"]["previous_version"] = old_version

        # Validate revised artifact
        is_valid, errors = self.validator.validate(artifact)

        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "REVISION VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            return False, artifact, error_message

        # Save revised artifact
        save_path = self.save_artifact(artifact, project_id)

        # Log change
        self._log_change(project_id, revision_reason, old_version, new_version)

        return True, artifact, f"Screenplay Step 8 revised and saved to {save_path}"

    # -- Internal Helpers -------------------------------------------------------

    def _add_metadata(
        self,
        content: Dict[str, Any],
        project_id: str,
        prompt_hash: str,
        model_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add required metadata to artifact."""
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": "sp_8",
            "step_name": "Screenplay Writing (Save the Cat)",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", self.DEFAULT_WRITER_TEMPERATURE),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
        }
        return artifact

    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk as JSON and human-readable text."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Save JSON artifact
        artifact_path = project_path / "sp_step_8_screenplay.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_8_screenplay.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 8: SCREENPLAY WRITING (Save the Cat)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Title: {artifact.get('title', 'ERROR: MISSING')}\n")
            f.write(f"Author: {artifact.get('author', 'AI Generated')}\n")
            f.write(f"Genre: {artifact.get('genre', 'ERROR: MISSING')}\n")
            f.write(f"Logline: {artifact.get('logline', 'ERROR: MISSING')}\n")
            f.write(f"Total Pages: {artifact.get('total_pages', 0)}\n")
            f.write(f"Estimated Duration: {artifact.get('estimated_duration_seconds', 0)}s\n")
            f.write(f"\nGenerated: {artifact.get('metadata', {}).get('created_at', 'N/A')}\n")
            f.write(f"Version: {artifact.get('metadata', {}).get('version', 'N/A')}\n")
            f.write("\n" + "-" * 60 + "\n\n")

            scenes = artifact.get("scenes", [])
            for scene in scenes:
                f.write(f"SCENE {scene.get('scene_number', '?')}")
                f.write(f" [{scene.get('beat', '')}]")
                f.write(f" ({scene.get('emotional_polarity', '')})\n")
                f.write(f"{scene.get('slugline', '')}\n")
                f.write(f"Conflict: {scene.get('conflict', '')}\n")
                f.write(f"Duration: {scene.get('estimated_duration_seconds', 0)}s\n\n")

                for element in scene.get("elements", []):
                    etype = element.get("element_type", "")
                    content = element.get("content", "")
                    if etype == "slugline":
                        f.write(f"{content}\n\n")
                    elif etype == "action":
                        f.write(f"{content}\n\n")
                    elif etype == "character":
                        f.write(f"                    {content}\n")
                    elif etype == "parenthetical":
                        f.write(f"               ({content})\n")
                    elif etype == "dialogue":
                        f.write(f"          {content}\n\n")
                    elif etype == "transition":
                        f.write(f"                                        {content}\n\n")

                f.write("\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_8_screenplay.json"
        if not artifact_path.exists():
            return None

        with open(artifact_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _snapshot_artifact(self, artifact: Dict[str, Any], project_id: str):
        """Save snapshot of current artifact before revision."""
        snapshot_path = self.project_dir / project_id / "snapshots"
        snapshot_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version = artifact.get("metadata", {}).get("version", "unknown")
        file_path = snapshot_path / f"sp_step_8_v{version}_{timestamp}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 8 revised from v{old_version} to v{new_version}\n"
            )
            f.write(f"  Reason: {reason}\n\n")

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate an artifact without executing generation.

        Args:
            artifact: The artifact to validate

        Returns:
            Tuple of (is_valid, message)
        """
        is_valid, errors = self.validator.validate(artifact)

        if is_valid:
            return True, "Step 8 screenplay passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
