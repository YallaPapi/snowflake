"""
Step 8b: Targeted Scene Rewrite (Grok)

After Step 8 diagnostics identify failing scenes, this step:
1. Parses the diagnostic output to build a per-scene task map
2. Deduplicates across checks (scene 7 might fail two checks)
3. Calls Grok to rewrite ONLY the failing scenes with minimum changes
4. Provides full prior-scene context so Grok can maintain continuity
5. Splices rewrites back into the screenplay
6. Optionally re-runs diagnostics to verify improvement

Key constraint from user: "it should not do like a full on rewrite, just change
enough that the rule isn't violated or whatever"
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from src.ai.generator import AIGenerator

logger = logging.getLogger(__name__)


class Step8bTargetedRewrite:
    """
    Targeted scene-level rewrite using Grok.

    Takes the screenplay artifact and Step 8 diagnostic results, identifies
    which scenes need fixing and what specific changes are needed, then calls
    Grok to rewrite only those scenes with minimum changes.
    """

    VERSION = "1.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        screenplay_artifact: Dict[str, Any],
        diagnostics_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute targeted scene rewrite based on diagnostic failures.

        Args:
            screenplay_artifact: The screenplay with scenes to potentially rewrite
            diagnostics_artifact: Step 8 diagnostic output with failing_scene_numbers
                and fix_per_scene for each failed check
            step_3_artifact: Hero/characters artifact for context
            step_1_artifact: Logline/title artifact for context
            project_id: Project directory name

        Returns:
            (success, updated_screenplay_artifact, message)
        """
        t0 = time.time()

        # 1. Parse diagnostics to build scene task map
        scene_tasks = self._build_scene_task_map(diagnostics_artifact)

        if not scene_tasks:
            logger.info("Step 8b: No failing scenes found — screenplay unchanged")
            return True, screenplay_artifact, "No diagnostic failures to fix — screenplay unchanged"

        logger.info("Step 8b: %d scenes need targeted rewrite", len(scene_tasks))
        for sn, tasks in sorted(scene_tasks.items()):
            checks = [t["check_name"] for t in tasks]
            logger.info("  Scene %d: %s", sn, ", ".join(checks))

        # 2. Initialize Grok as rewriter
        try:
            grok = AIGenerator(provider="xai")
            grok_config = {
                "model_name": "grok-4-1-fast-reasoning",
                "temperature": 0.3,
                "max_tokens": 8000,  # Single scene rewrite
            }
        except Exception as e:
            logger.error("Failed to initialize Grok for targeted rewrite: %s", e)
            return False, screenplay_artifact, f"Grok initialization failed: {e}"

        # 3. Build context
        scenes = screenplay_artifact.get("scenes", [])
        scenes_by_num = {s.get("scene_number"): s for s in scenes}
        title = step_1_artifact.get("title", "UNTITLED")
        logline = step_1_artifact.get("logline", "")
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        hero_name = hero.get("name", "HERO")

        # 4. Rewrite each failing scene
        rewritten_count = 0
        failed_rewrites = []

        for scene_num in sorted(scene_tasks.keys()):
            original_scene = scenes_by_num.get(scene_num)
            if not original_scene:
                logger.warning("Scene %d not found in screenplay — skipping", scene_num)
                continue

            tasks = scene_tasks[scene_num]
            logger.info("Rewriting scene %d (%d fixes needed)...", scene_num, len(tasks))

            # Build previous scenes context (all scenes before this one)
            prev_scenes = [s for s in scenes if s.get("scene_number", 0) < scene_num]

            prompt = self._build_scene_rewrite_prompt(
                original_scene=original_scene,
                tasks=tasks,
                prev_scenes=prev_scenes,
                title=title,
                logline=logline,
                hero_name=hero_name,
            )

            try:
                raw = grok.generate(prompt, grok_config)
                rewritten_scene = self._parse_rewritten_scene(raw, scene_num)

                if rewritten_scene and rewritten_scene.get("elements"):
                    # Preserve structural metadata from original
                    rewritten_scene["scene_number"] = scene_num
                    rewritten_scene["board_card_number"] = original_scene.get("board_card_number", scene_num)
                    rewritten_scene.setdefault("beat", original_scene.get("beat", ""))
                    rewritten_scene.setdefault("emotional_start", original_scene.get("emotional_start", ""))
                    rewritten_scene.setdefault("emotional_end", original_scene.get("emotional_end", ""))
                    rewritten_scene.setdefault("conflict", original_scene.get("conflict", ""))
                    rewritten_scene.setdefault("characters_present", original_scene.get("characters_present", []))
                    rewritten_scene.setdefault("slugline", original_scene.get("slugline", ""))

                    # Splice into screenplay
                    for i, s in enumerate(scenes):
                        if s.get("scene_number") == scene_num:
                            scenes[i] = rewritten_scene
                            break
                    rewritten_count += 1
                    logger.info("  Scene %d rewritten successfully", scene_num)
                else:
                    logger.warning("  Scene %d: Grok returned empty/unparseable result", scene_num)
                    failed_rewrites.append(scene_num)

            except Exception as e:
                logger.error("  Scene %d rewrite failed: %s", scene_num, e)
                failed_rewrites.append(scene_num)

        # 5. Update screenplay artifact
        screenplay_artifact["scenes"] = scenes
        screenplay_artifact.setdefault("metadata", {})
        screenplay_artifact["metadata"]["step_8b_version"] = self.VERSION
        screenplay_artifact["metadata"]["step_8b_scenes_rewritten"] = rewritten_count
        screenplay_artifact["metadata"]["step_8b_scenes_failed"] = len(failed_rewrites)

        elapsed = time.time() - t0

        # Save updated screenplay
        if project_id:
            save_path = self.project_dir / project_id / "sp_step_8_screenplay.json"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(screenplay_artifact, f, indent=2, ensure_ascii=False)
            logger.info("Updated screenplay saved to %s", save_path)

        msg = (
            f"Step 8b targeted rewrite: {rewritten_count}/{len(scene_tasks)} scenes "
            f"rewritten by Grok in {elapsed:.1f}s"
        )
        if failed_rewrites:
            msg += f" ({len(failed_rewrites)} failed: scenes {failed_rewrites})"

        return True, screenplay_artifact, msg

    def _build_scene_task_map(
        self, diagnostics_artifact: Dict[str, Any]
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Parse diagnostic output into a per-scene task map.

        Supports both old format (passed/failing_scene_numbers/fix_per_scene)
        and new observational format (rough_spots/rewrite_suggestions).

        Returns dict mapping scene_number -> list of tasks, where each task has:
          - check_name: which diagnostic check identified the issue
          - fix_instruction: the concrete rewrite instruction
        """
        scene_tasks: Dict[int, List[Dict[str, Any]]] = {}

        diagnostics = diagnostics_artifact.get("diagnostics", [])
        for diag in diagnostics:
            check_name = diag.get("check_name", "Unknown")

            # New observational format: rough_spots + rewrite_suggestions
            rough_spots = diag.get("rough_spots", [])
            rewrite_suggestions = diag.get("rewrite_suggestions", {})

            if rough_spots:
                for spot in rough_spots:
                    scene_num = int(spot.get("scene", 0))
                    if scene_num == 0:
                        continue

                    # Get the rewrite for this scene if available
                    fix_instruction = rewrite_suggestions.get(str(scene_num), "")
                    if not fix_instruction:
                        fix_instruction = rewrite_suggestions.get(scene_num, "")
                    if not fix_instruction:
                        # Fall back to the rough spot issue description
                        current = spot.get("current_text", "")
                        fix_instruction = f"Issue: {spot.get('issue', '')}. Current text: {current}"

                    task = {
                        "check_name": check_name,
                        "fix_instruction": fix_instruction,
                    }

                    if scene_num not in scene_tasks:
                        scene_tasks[scene_num] = []
                    scene_tasks[scene_num].append(task)
                continue

            # Old format fallback: passed/failing_scene_numbers/fix_per_scene
            if diag.get("passed", True):
                continue

            failing_scenes = diag.get("failing_scene_numbers", [])
            fix_per_scene = diag.get("fix_per_scene", {})

            for scene_num in failing_scenes:
                scene_num = int(scene_num)
                fix_instruction = fix_per_scene.get(str(scene_num), "")
                if not fix_instruction:
                    fix_instruction = fix_per_scene.get(scene_num, "")
                if not fix_instruction:
                    fix_instruction = diag.get("problem_details", "Fix the identified issue.")

                task = {
                    "check_name": check_name,
                    "fix_instruction": fix_instruction,
                }

                if scene_num not in scene_tasks:
                    scene_tasks[scene_num] = []
                scene_tasks[scene_num].append(task)

        return scene_tasks

    def _build_scene_rewrite_prompt(
        self,
        original_scene: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        prev_scenes: List[Dict[str, Any]],
        title: str,
        logline: str,
        hero_name: str,
    ) -> Dict[str, str]:
        """Build Grok prompt for rewriting a single scene."""

        # Format the original scene as screenplay text
        scene_text = self._format_scene_as_text(original_scene)
        scene_num = original_scene.get("scene_number", "?")
        slugline = original_scene.get("slugline", "?")
        beat = original_scene.get("beat", "?")

        # Build fix instructions
        fix_lines = []
        for i, task in enumerate(tasks, 1):
            fix_lines.append(
                f"FIX {i} ({task['check_name']}):\n{task['fix_instruction']}"
            )
        fixes_block = "\n\n".join(fix_lines)

        # Build prior scenes context (full text for continuity)
        if prev_scenes:
            prev_parts = []
            for s in prev_scenes:
                prev_parts.append(self._format_scene_as_text(s))
            prev_context = "\n\n".join(prev_parts)
            prev_section = (
                f"PREVIOUS SCENES (for context — maintain character voice, callbacks, "
                f"and continuity with these):\n\n{prev_context}"
            )
        else:
            prev_section = "(This is the first scene.)"

        system_prompt = (
            "You are a precise screenplay editor. You make MINIMUM TARGETED CHANGES to fix "
            "specific problems identified by a script doctor. You do NOT rewrite scenes from "
            "scratch. You preserve the existing structure, pacing, scene heading, characters, "
            "and overall flow. You ONLY change the specific dialogue, action, or elements "
            "called out in the fix instructions.\n\n"
            "You MUST respond with valid JSON only. No markdown fences, no commentary."
        )

        user_prompt = f"""TARGETED SCENE REWRITE — Scene {scene_num}

TITLE: {title}
LOGLINE: {logline}
HERO: {hero_name}

{prev_section}

═══════════════════════════════════════════════════
SCENE TO FIX — Scene {scene_num}: {slugline} ({beat})
═══════════════════════════════════════════════════

{scene_text}

═══════════════════════════════════════════════════
PROBLEMS TO FIX (make MINIMUM changes — do NOT rewrite the whole scene):
═══════════════════════════════════════════════════

{fixes_block}

═══════════════════════════════════════════════════
REWRITE RULES:
═══════════════════════════════════════════════════

1. MINIMUM CHANGES ONLY — keep 90%+ of the scene identical. Only change what the fix instructions say to change.
2. Preserve the scene_number, slugline, beat, emotional_start, emotional_end, conflict, and characters_present.
3. Follow the CURRENT/REPLACE WITH/FIXES format from the fix instructions exactly.
4. If a fix says to add something, add it at the specified location without removing surrounding content.
5. If a fix says to replace dialogue, keep the same character speaking — just change the words.
6. Do NOT add new characters not already in the scene or prior scenes.
7. Do NOT change the scene's plot outcome or structural function.

OUTPUT: Valid JSON with this structure:
{{
    "scene_number": {scene_num},
    "slugline": "{slugline}",
    "beat": "{beat}",
    "emotional_start": "{original_scene.get('emotional_start', '')}",
    "emotional_end": "{original_scene.get('emotional_end', '')}",
    "conflict": "{original_scene.get('conflict', '')}",
    "characters_present": {json.dumps(original_scene.get('characters_present', []))},
    "elements": [
        {{"element_type": "slugline", "content": "..."}},
        {{"element_type": "action", "content": "..."}},
        {{"element_type": "character", "content": "CHARACTER NAME"}},
        {{"element_type": "dialogue", "content": "..."}},
        ...
    ]
}}"""

        return {"system": system_prompt, "user": user_prompt}

    def _format_scene_as_text(self, scene: Dict[str, Any]) -> str:
        """Format a scene dict as readable screenplay text."""
        parts = []
        num = scene.get("scene_number", "?")
        slug = scene.get("slugline", "?")
        beat = scene.get("beat", "?")
        e_start = scene.get("emotional_start", "?")
        e_end = scene.get("emotional_end", "?")
        chars = ", ".join(scene.get("characters_present", []))

        parts.append(f"=== SCENE {num} — {beat} ===")
        parts.append(f"Emotional arc: {e_start} → {e_end}")
        parts.append(f"Characters: {chars}")
        parts.append("")

        for elem in scene.get("elements", []):
            etype = elem.get("element_type", "")
            content = elem.get("content", "")
            if etype == "slugline":
                parts.append(f"\n{content}\n")
            elif etype == "action":
                parts.append(content)
            elif etype == "character":
                parts.append(f"                    {content}")
            elif etype == "parenthetical":
                parts.append(f"               ({content})")
            elif etype == "dialogue":
                parts.append(f"          {content}\n")
            elif etype == "transition":
                parts.append(f"                                        {content}\n")

        return "\n".join(parts)

    def _parse_rewritten_scene(
        self, raw: str, expected_scene_num: int
    ) -> Optional[Dict[str, Any]]:
        """Parse Grok's JSON response into a scene dict."""
        if not raw:
            return None

        # Strip markdown fences
        import re
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)

        try:
            parsed = json.loads(raw.strip())
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(raw[start:end])
                except json.JSONDecodeError:
                    logger.error("Failed to parse Grok scene rewrite JSON")
                    return None
            else:
                return None

        # Handle nested "scene" key
        if "scene" in parsed and isinstance(parsed["scene"], dict):
            parsed = parsed["scene"]

        # Validate it has elements
        if not parsed.get("elements"):
            logger.warning("Parsed scene has no 'elements' array")
            return None

        return parsed
