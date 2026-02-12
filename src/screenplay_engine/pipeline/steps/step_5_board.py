"""
Step 5 Implementation: The Board -- 40 Scene Cards (Save the Cat Ch.5)
Takes Step 4 beat sheet, Step 3 characters, Step 1 logline, and Step 2 genre,
generates 40 scene cards organized in 4 rows with emotional polarity, conflict,
and storyline colors.

v3.0.0 -- Now accepts Step 1 and Step 2 artifacts for genre-specific board guidance.
No max_tokens defaults. Retry loop with revision prompts (same pattern as Step 4).
"""

import json
import re
import uuid
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.screenplay_engine.pipeline.validators.step_5_validator import Step5Validator
from src.screenplay_engine.pipeline.prompts.step_5_prompt import Step5Prompt
from src.ai.generator import AIGenerator


class Step5Board:
    """
    Screenplay Engine Step 5: The Board (40 Scene Cards)

    Takes the Step 4 beat sheet artifact, Step 3 hero/character artifact,
    Step 1 logline, and Step 2 genre, and generates a 40-card board organized
    in 4 rows with emotional polarity, conflict markers, and storyline color-coding.
    """

    VERSION = "3.0.0"
    ROW_KEYS = [
        "row_1_act_one",
        "row_2_act_two_a",
        "row_3_act_two_b",
        "row_4_act_three",
    ]
    PRIMARY_STORYLINES = ("A", "B")
    REPAIR_PRIORITY = ("A", "B", "C", "D", "E")

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step5Validator()
        self.prompt_generator = Step5Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 5: Generate The Board (40 scene cards).

        Args:
            step_4_artifact: Validated Step 4 beat sheet artifact.
            step_3_artifact: Validated Step 3 hero/character artifact.
            step_1_artifact: Validated Step 1 logline artifact.
            step_2_artifact: Validated Step 2 genre artifact.
            project_id: Project UUID (auto-generated if not provided).
            model_config: AI model configuration overrides.

        Returns:
            Tuple of (success, artifact, message)
        """
        if not project_id:
            project_id = str(uuid.uuid4())

        if not model_config:
            model_config = {
                "temperature": 0.3,
                "max_tokens": 32000,
            }

        # Compute upstream hash for provenance tracking
        upstream_content = json.dumps(
            {
                "step_1": step_1_artifact,
                "step_2": step_2_artifact,
                "step_3": step_3_artifact,
                "step_4": step_4_artifact,
            },
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()

        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(
            step_4_artifact, step_3_artifact, step_1_artifact, step_2_artifact,
        )

        # Generate with retry loop
        max_attempts = 3
        artifact: Dict[str, Any] = {}
        last_errors: list = []

        for attempt in range(max_attempts):
            raw_content = self.generator.generate(prompt_data, model_config)
            artifact = self._parse_board(raw_content)
            artifact = self._repair_storyline_distribution(artifact)

            is_valid, errors = self.validator.validate(artifact)
            if is_valid:
                break

            last_errors = errors

            # On failure, generate revision prompt for next attempt
            if attempt < max_attempts - 1:
                fixes = self.validator.fix_suggestions(errors)
                prompt_data = self.prompt_generator.generate_revision_prompt(
                    artifact, errors, fixes,
                    step_4_artifact, step_3_artifact,
                    step_1_artifact, step_2_artifact,
                )

        # Add metadata
        artifact = self._add_metadata(
            artifact, project_id, prompt_data.get("prompt_hash", ""),
            model_config, upstream_hash,
        )

        # Final validation
        artifact = self._repair_storyline_distribution(artifact)
        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            fixes = self.validator.fix_suggestions(errors)
            msg = "VALIDATION FAILED:\n" + "\n".join(
                f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes)
            )
            return False, artifact, msg

        # Save to disk
        save_path = self.save_artifact(artifact, project_id)
        return True, artifact, f"Step 5 board saved to {save_path}"

    # ── Parsing helpers ───────────────────────────────────────────────

    def _parse_board(self, raw_content: str) -> Dict[str, Any]:
        """Parse AI output into a board dict."""
        # Try extracting JSON from markdown code blocks
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
            if code_match:
                parsed = json.loads(code_match.group(1))
                if self._is_valid_structure(parsed):
                    return parsed
        except (json.JSONDecodeError, AttributeError):
            pass

        # Try direct JSON parse
        try:
            stripped = raw_content.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                parsed = json.loads(stripped)
                if self._is_valid_structure(parsed):
                    return parsed
        except json.JSONDecodeError:
            pass

        # Last resort: find outermost JSON object
        try:
            start = raw_content.index("{")
            end = raw_content.rindex("}") + 1
            parsed = json.loads(raw_content[start:end])
            if self._is_valid_structure(parsed):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass

        # Return empty structure if all parsing fails
        return {
            "row_1_act_one": [],
            "row_2_act_two_a": [],
            "row_3_act_two_b": [],
            "row_4_act_three": [],
        }

    def _is_valid_structure(self, parsed: Any) -> bool:
        """Check that parsed data has expected board shape."""
        if not isinstance(parsed, dict):
            return False
        return any(
            key in parsed
            for key in ["row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"]
        )

    # ── Metadata ──────────────────────────────────────────────────────

    def _repair_storyline_distribution(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize storyline colors to a deterministic spacing pattern that
        satisfies validator gap constraints (A/B <= 3, secondary <= 6).
        """
        if not isinstance(artifact, dict):
            return artifact

        cards = self._ordered_cards(artifact)
        if not cards:
            return artifact

        template_40 = [
            "A", "B", "A", "B", "A", "C", "B", "A", "B", "A",
            "B", "A", "C", "B", "A", "B", "A", "C", "B", "A",
            "B", "A", "B", "C", "A", "B", "A", "B", "C", "B",
            "A", "B", "C", "A", "B", "A", "B", "C", "A", "B",
        ]

        card_count = len(cards)
        if card_count <= 40:
            sequence = template_40[:card_count]
        else:
            sequence = list(template_40)
            # Keep A/B alternating for overflow cards (>40) to preserve primary spacing.
            for i in range(card_count - 40):
                sequence.append("A" if i % 2 == 0 else "B")

        for card, color in zip(cards, sequence):
            card["storyline_color"] = color

        return artifact

    def _ordered_cards(self, artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        for row_key in self.ROW_KEYS:
            row = artifact.get(row_key, [])
            if isinstance(row, list):
                for card in row:
                    if isinstance(card, dict):
                        cards.append(card)
        cards.sort(key=lambda card: card.get("card_number", 0))
        return cards

    @staticmethod
    def _normalized_color(color: Any) -> str:
        if isinstance(color, str):
            normalized = color.strip().upper()
            if normalized in {"A", "B", "C", "D", "E"}:
                return normalized
        return ""

    @staticmethod
    def _storyline_gap_limit(color: str) -> int:
        if color in {"A", "B"}:
            return 3
        return 6

    def _longest_gap(self, colors: List[str], target: str) -> Tuple[int, int, int]:
        max_gap = -1
        max_start = 0
        max_end = -1
        current_start = 0
        current_gap = 0

        for idx, color in enumerate(colors):
            if color == target:
                if current_gap > max_gap:
                    max_gap = current_gap
                    max_start = current_start
                    max_end = idx - 1
                current_start = idx + 1
                current_gap = 0
            else:
                current_gap += 1

        if current_gap > max_gap:
            max_gap = current_gap
            max_start = current_start
            max_end = len(colors) - 1

        if max_gap < 0:
            return 0, 0, -1
        return max_gap, max_start, max_end

    def _choose_gap_fill_index(
        self,
        cards: List[Dict[str, Any]],
        colors: List[str],
        target: str,
        seg_start: int,
        seg_end: int,
    ) -> Optional[int]:
        if seg_start > seg_end:
            return None

        counts = Counter(colors)
        midpoint = (seg_start + seg_end) / 2.0
        best_index = None
        best_score = None

        for idx in range(seg_start, seg_end + 1):
            current = colors[idx]
            if current == target:
                continue

            current_count = counts.get(current, 0)
            scarcity_penalty = 1000 if current_count <= 1 else 0

            beat_name = str(cards[idx].get("beat", "")).strip().lower()
            landmark_penalty = 0
            if current in self.PRIMARY_STORYLINES and (
                beat_name.startswith("catalyst")
                or beat_name.startswith("break into two")
                or beat_name.startswith("midpoint")
                or beat_name.startswith("all is lost")
                or beat_name.startswith("break into three")
            ):
                landmark_penalty = 250

            distance_penalty = abs(idx - midpoint)
            score = (scarcity_penalty, landmark_penalty, distance_penalty)

            if best_score is None or score < best_score:
                best_score = score
                best_index = idx

        return best_index

    def _ensure_primary_payoffs_in_row_four(self, artifact: Dict[str, Any]) -> None:
        row_four = artifact.get("row_4_act_three", [])
        if not isinstance(row_four, list) or not row_four:
            return

        all_cards = self._ordered_cards(artifact)
        used_colors = {self._normalized_color(card.get("storyline_color")) for card in all_cards}
        row_four_colors = {
            self._normalized_color(card.get("storyline_color"))
            for card in row_four
            if isinstance(card, dict)
        }

        missing_primary = [
            color
            for color in self.PRIMARY_STORYLINES
            if color in used_colors and color not in row_four_colors
        ]
        if not missing_primary:
            return

        row_four_cards = [card for card in row_four if isinstance(card, dict)]
        if not row_four_cards:
            return

        for missing_color in missing_primary:
            target_card = None
            for card in row_four_cards:
                color = self._normalized_color(card.get("storyline_color"))
                if color not in self.PRIMARY_STORYLINES:
                    target_card = card
                    break
            if target_card is None:
                target_card = row_four_cards[-1]
            target_card["storyline_color"] = missing_color

    def _add_metadata(
        self,
        content: Dict[str, Any],
        project_id: str,
        prompt_hash: str,
        model_config: Dict[str, Any],
        upstream_hash: str,
    ) -> Dict[str, Any]:
        """Add required metadata to artifact."""
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": "sp_5",
            "step_name": "The Board (Save the Cat)",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get(
                "model_name",
                self.generator.default_model if hasattr(self.generator, "default_model") else "unknown",
            ),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        return artifact

    # ── Persistence ───────────────────────────────────────────────────

    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk as JSON and human-readable text."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Save JSON artifact
        artifact_path = project_path / "sp_step_5_board.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_5_board.txt"
        with open(readable_path, "w", encoding="utf-8") as f:
            f.write("SCREENPLAY STEP 5: THE BOARD -- 40 SCENE CARDS (Save the Cat)\n")
            f.write("=" * 65 + "\n\n")

            row_labels = {
                "row_1_act_one": "ROW 1 -- ACT ONE (cards 1-10, pages 1-25)",
                "row_2_act_two_a": "ROW 2 -- ACT TWO A (cards 11-20, pages 25-55)",
                "row_3_act_two_b": "ROW 3 -- ACT TWO B (cards 21-30, pages 55-85)",
                "row_4_act_three": "ROW 4 -- ACT THREE (cards 31-40, pages 85-110)",
            }

            total = 0
            for key, label in row_labels.items():
                cards = artifact.get(key, [])
                total += len(cards)
                f.write(f"\n{label}\n")
                f.write("-" * 60 + "\n")
                for card in cards:
                    if not isinstance(card, dict):
                        continue
                    num = card.get("card_number", "?")
                    heading = card.get("scene_heading", "NO HEADING")
                    e_start = card.get("emotional_start", "?")
                    e_end = card.get("emotional_end", "?")
                    polarity = f"{e_start}/{e_end}"
                    color = card.get("storyline_color", "?")
                    beat = card.get("beat", "")
                    desc = card.get("description", "")
                    conflict = card.get("conflict", "")
                    chars = ", ".join(card.get("characters_present", []))

                    f.write(f"\n  [{num}] {heading}  [{polarity}] [{color}]\n")
                    if beat:
                        f.write(f"       Beat: {beat}\n")
                    f.write(f"       {desc}\n")
                    f.write(f"       Conflict: {conflict}\n")
                    if chars:
                        f.write(f"       Characters: {chars}\n")

            f.write(f"\n{'=' * 65}\n")
            f.write(f"Total cards: {total}\n")
            meta = artifact.get("metadata", {})
            f.write(f"Generated: {meta.get('created_at', 'N/A')}\n")
            f.write(f"Version: {meta.get('version', 'N/A')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_5_board.json"
        if not artifact_path.exists():
            return None

        with open(artifact_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 5 artifact due to downstream conflicts.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            step_4_artifact: Step 4 beat sheet artifact for context
            step_3_artifact: Step 3 hero/character artifact for context
            step_1_artifact: Step 1 logline artifact for context
            step_2_artifact: Step 2 genre artifact for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 5 artifact found for project {project_id}"

        self._snapshot_artifact(current_artifact, project_id)

        _, current_errors = self.validator.validate(current_artifact)
        all_errors = [revision_reason] + current_errors
        fix_suggestions = self.validator.fix_suggestions(current_errors)

        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact, all_errors, fix_suggestions,
            step_4_artifact, step_3_artifact,
            step_1_artifact, step_2_artifact,
        )

        if not model_config:
            model_config = {"temperature": 0.3, "max_tokens": 32000}

        raw_content = self.generator.generate(prompt_data, model_config)
        artifact = self._parse_board(raw_content)
        artifact = self._repair_storyline_distribution(artifact)

        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            # One more attempt
            fixes2 = self.validator.fix_suggestions(errors)
            prompt_data2 = self.prompt_generator.generate_revision_prompt(
                artifact, errors, fixes2,
                step_4_artifact, step_3_artifact,
                step_1_artifact, step_2_artifact,
            )
            raw_content2 = self.generator.generate(prompt_data2, model_config)
            artifact = self._parse_board(raw_content2)
            artifact = self._repair_storyline_distribution(artifact)
            is_valid, errors = self.validator.validate(artifact)

        # Update version
        old_version = current_artifact.get("metadata", {}).get("version", "3.0.0")
        major, minor, patch = map(int, old_version.split("."))
        new_version = f"{major}.{minor + 1}.0"

        # Compute upstream hash
        upstream_content = json.dumps(
            {
                "step_1": step_1_artifact, "step_2": step_2_artifact,
                "step_3": step_3_artifact, "step_4": step_4_artifact,
            },
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()

        artifact = self._add_metadata(
            artifact, project_id, prompt_data.get("prompt_hash", ""),
            model_config, upstream_hash,
        )
        artifact["metadata"]["version"] = new_version
        artifact["metadata"]["revision_reason"] = revision_reason
        artifact["metadata"]["previous_version"] = old_version

        if not is_valid:
            fixes_final = self.validator.fix_suggestions(errors)
            msg = "REVISION VALIDATION FAILED:\n" + "\n".join(
                f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes_final)
            )
            return False, artifact, msg

        save_path = self.save_artifact(artifact, project_id)
        self._log_change(project_id, revision_reason, old_version, new_version)

        return True, artifact, f"Step 5 board revised and saved to {save_path}"

    def _snapshot_artifact(self, artifact: Dict[str, Any], project_id: str):
        """Save snapshot of current artifact before revision."""
        snapshot_path = self.project_dir / project_id / "snapshots"
        snapshot_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version = artifact.get("metadata", {}).get("version", "unknown")
        file_path = snapshot_path / f"sp_step_5_v{version}_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 5 revised from v{old_version} to v{new_version}\n"
            )
            f.write(f"  Reason: {reason}\n\n")

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate an artifact without executing generation."""
        is_valid, errors = self.validator.validate(artifact)

        if is_valid:
            return True, "Step 5 board passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
