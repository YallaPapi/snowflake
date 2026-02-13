"""
Checkpoint Prompt Generator: Builds incremental diagnostic prompts.

Generates prompts tailored to the artifacts available at each pipeline step,
asking the AI to evaluate only the applicable subset of Ch.7 diagnostic checks.
"""

import json
import hashlib
from typing import Dict, Any, List

from src.screenplay_engine.pipeline.checkpoint.checkpoint_config import (
    get_applicable_checks,
    get_check_definitions,
    get_check_name,
    STEP_ARTIFACT_KEYS,
    STEP_SPECIFIC_GUIDANCE,
)


class CheckpointPrompt:
    """Generates incremental diagnostic prompts for each pipeline step."""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! script analyst running incremental diagnostics. "
        "Examine the provided artifact(s) against the specified subset of Blake Snyder "
        "Chapter 7 diagnostic checks. Evaluate ONLY what the artifact can reasonably "
        "demonstrate at this stage — read the EVALUATION SCOPE instructions carefully "
        "for each check.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    # Step-specific evaluation context descriptions
    STEP_CONTEXT: Dict[int, str] = {
        1: (
            "You are evaluating a LOGLINE artifact (Step 1). The screenplay has NOT been "
            "written yet — evaluate whether the logline's foundation sets up the right conditions "
            "for the checks below. Flag structural weaknesses that will become problems later."
        ),
        2: (
            "You are evaluating a GENRE CLASSIFICATION artifact (Step 2). The logline exists but "
            "the screenplay has NOT been written yet — evaluate whether the genre choice and its "
            "working parts set up the right conditions for the checks below."
        ),
        3: (
            "You are evaluating a HERO CONSTRUCTION artifact (Step 3). Logline and genre exist but "
            "the screenplay has NOT been written yet — evaluate whether the hero, antagonist, and "
            "B-story character designs set up the right conditions for the checks below."
        ),
        4: (
            "You are evaluating a BEAT SHEET artifact (Step 4 — 15 beats). Logline, genre, and hero "
            "exist but the screenplay has NOT been written yet — evaluate whether the beat structure "
            "sets up the right conditions for the checks below."
        ),
        5: (
            "You are evaluating a BOARD artifact (Step 5 — 40 scene cards). Logline, genre, hero, "
            "and beat sheet exist but the screenplay has NOT been written yet — evaluate whether the "
            "scene cards set up the right conditions for the checks below. Note: dialogue doesn't "
            "exist yet, so evaluate based on scene descriptions, conflicts, and character assignments."
        ),
        6: (
            "You are evaluating a FINISHED SCREENPLAY (Step 6). All upstream artifacts exist. "
            "Evaluate the ACTUAL scenes, dialogue, and action against ALL diagnostic checks."
        ),
    }

    def generate_prompt(
        self,
        step_number: int,
        artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a checkpoint diagnostic prompt for the given step.

        Args:
            step_number: Which pipeline step just completed (1-6).
            artifacts: Dict of available artifacts keyed by step name.
                Expected keys depend on step_number (see STEP_ARTIFACT_KEYS).

        Returns:
            Dict with system/user prompts and metadata.
        """
        applicable_checks = get_applicable_checks(step_number)
        check_defs = get_check_definitions(applicable_checks)

        # Build check descriptions block with step-specific guidance
        checks_block = self._format_check_definitions(check_defs, step_number)

        # Build artifacts block (only include what's available)
        artifacts_block = self._format_artifacts(step_number, artifacts)

        # Build expected output format
        output_format = self._format_output_template(applicable_checks)

        # Step-specific context
        context = self.STEP_CONTEXT.get(step_number, "Evaluate the artifact(s) below.")

        user_prompt = f"""INCREMENTAL DIAGNOSTIC CHECKPOINT — After Step {step_number}

{context}

{artifacts_block}

DIAGNOSTIC CHECKS TO RUN ({len(applicable_checks)} checks):

{checks_block}

INSTRUCTIONS:
- Evaluate ONLY the {len(applicable_checks)} checks listed above.
- For each check, provide observations and identify any rough spots based on what the artifact(s) can demonstrate AT THIS STAGE.
- Read the EVALUATION SCOPE for each check — only identify rough spots for issues the artifact CAN address.
- If you find rough spots, describe them with specific scene references and rewrite suggestions.

OUTPUT FORMAT (JSON):
{output_format}

RULES:
- You MUST run ALL {len(applicable_checks)} checks listed above — do not skip any.
- For clean checks: observations non-empty, rough_spots empty list, rewrite_suggestions empty dict.
- For checks with rough spots: observations non-empty, rough_spots non-empty with scene/issue details, rewrite_suggestions non-empty.
- total_checks MUST be {len(applicable_checks)}.
- Use the EXACT check_name values shown in the output format."""

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_revision_feedback(self, failures: List[Dict[str, Any]], max_failures: int = 2) -> str:
        """
        Format diagnostic checkpoint failures into a concise revision reason string.

        Only includes the top failures (by priority) with truncated details to avoid
        overwhelming the generator with a wall of text that causes confusion.

        Args:
            failures: List of failed check dicts from CheckpointResult.
            max_failures: Maximum number of failures to include (default 2).

        Returns:
            Formatted revision reason string.
        """
        # Limit to top N failures to keep revision prompt focused
        top_failures = failures[:max_failures]

        lines = [f"DIAGNOSTIC CHECKPOINT: {len(failures)} check(s) have rough spots. Focus on fixing these {len(top_failures)}:"]
        for f in top_failures:
            check_name = f.get("check_name", "Unknown")
            # Support both old and new format
            fix = f.get("fix_suggestion") or ""
            if not fix:
                # New format: extract from rewrite_suggestions
                rewrites = f.get("rewrite_suggestions", {})
                if rewrites:
                    fix = next(iter(rewrites.values()), "No suggestion")
                else:
                    fix = f.get("observations", "No suggestion")
            # Truncate fix to 300 chars to keep it concise
            if len(fix) > 300:
                fix = fix[:297] + "..."
            lines.append(f"\n[ROUGH SPOT] {check_name}")
            lines.append(f"  Fix: {fix}")
        return "\n".join(lines)

    def _format_check_definitions(self, check_defs: List[Dict[str, str]], step_number: int = 0) -> str:
        """Format check definitions into the prompt text with step-specific guidance."""
        blocks = []
        for cd in check_defs:
            num = cd["check_number"]
            name = cd["name"]
            desc = cd["description"]
            fail = cd["fail_criteria"]
            fix = cd["fix_template"]
            sub = cd.get("sub_checks", "")

            block = f"{num}. {name} — {desc}"

            # Add step-specific guidance if available
            guidance_key = (step_number, num)
            if guidance_key in STEP_SPECIFIC_GUIDANCE:
                block += f"\n   EVALUATION SCOPE FOR THIS STEP: {STEP_SPECIFIC_GUIDANCE[guidance_key]}"
            elif sub:
                block += f"\n   Sub-checks:\n   {sub}"

            block += f"\n   - Look for: {fail}"
            block += f"\n   - If rough spots exist: {fix}"
            blocks.append(block)

        return "\n\n".join(blocks)

    def _format_artifacts(self, step_number: int, artifacts: Dict[str, Any]) -> str:
        """Format available artifacts into prompt context blocks."""
        sections = []

        # Map artifact keys to labels
        label_map = {
            "step_1": "LOGLINE (Step 1)",
            "step_2": "GENRE CLASSIFICATION (Step 2)",
            "step_3": "HERO PROFILE (Step 3)",
            "step_4": "BEAT SHEET (Step 4)",
            "step_5": "THE BOARD (Step 5)",
            "screenplay": "FINISHED SCREENPLAY (Step 6)",
        }

        expected_keys = STEP_ARTIFACT_KEYS.get(step_number, [])
        for key in expected_keys:
            if key in artifacts and artifacts[key]:
                label = label_map.get(key, key.upper())
                artifact_json = json.dumps(artifacts[key], indent=2, ensure_ascii=False)
                sections.append(f"{label}:\n{artifact_json}")

        return "\n\n".join(sections)

    def _format_output_template(self, applicable_checks: List[int]) -> str:
        """Build the expected JSON output template for the applicable checks."""
        examples = []
        for i, check_num in enumerate(applicable_checks):
            name = get_check_name(check_num)
            if i % 2 == 0:
                # Clean check example
                examples.append(
                    f'        {{"check_number": {check_num}, "check_name": "{name}", '
                    f'"observations": "<factual analysis>", '
                    f'"rough_spots": [], '
                    f'"rewrite_suggestions": {{}}}}'
                )
            else:
                # Check with rough spots example
                examples.append(
                    f'        {{"check_number": {check_num}, "check_name": "{name}", '
                    f'"observations": "<factual analysis with rough spots>", '
                    f'"rough_spots": [{{"scene": 1, "issue": "<description>", "current_text": "<quoted>"}}], '
                    f'"rewrite_suggestions": {{"1": "CURRENT: ... REPLACE WITH: ... FIXES: ..."}}}}'
                )

        checks_json = ",\n".join(examples)
        return (
            "{\n"
            '    "diagnostics": [\n'
            f"{checks_json}\n"
            "    ],\n"
            f'    "total_checks": {len(applicable_checks)}\n'
            "}"
        )
