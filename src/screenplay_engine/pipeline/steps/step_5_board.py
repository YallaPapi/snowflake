"""
Step 5 Implementation: The Board -- 40 Scene Cards (Save the Cat Ch.5)
Takes Step 4 beat sheet and Step 3 characters, generates 40 scene cards
organized in 4 rows with emotional polarity, conflict, and storyline colors.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_5_validator import Step5Validator
from src.screenplay_engine.pipeline.prompts.step_5_prompt import Step5Prompt
from src.ai.generator import AIGenerator


class Step5Board:
    """
    Screenplay Engine Step 5: The Board (40 Scene Cards)

    Takes the Step 4 beat sheet artifact and Step 3 hero/character artifact
    and generates a 40-card board organized in 4 rows with emotional polarity,
    conflict markers, and storyline color-coding on every card.
    """

    VERSION = "2.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 5 executor.

        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step5Validator()
        self.prompt_generator = Step5Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 5: Generate The Board (40 scene cards) from beat sheet
        and character data.

        Args:
            step_4_artifact: Validated Step 4 beat sheet artifact.
            step_3_artifact: Validated Step 3 hero/character artifact.
            project_id: Project UUID (auto-generated if not provided).
            model_config: AI model configuration overrides.

        Returns:
            Tuple of (success, artifact, message)
        """
        # Generate project ID if not provided
        if not project_id:
            project_id = str(uuid.uuid4())

        # Default model config -- higher max_tokens for 40 scene cards
        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.3,
                "max_tokens": 12000,
                "seed": 42,
            }

        # Compute upstream hash for provenance tracking
        upstream_content = json.dumps(
            {"step_4": step_4_artifact, "step_3": step_3_artifact},
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()

        # Generate prompt from input artifacts
        prompt_data = self.prompt_generator.generate_prompt(
            step_4_artifact, step_3_artifact
        )

        # Call AI generator with validation loop
        try:
            artifact_content = self.generator.generate_with_validation(
                prompt_data, self.validator, model_config
            )
        except Exception as e:
            return False, {}, f"AI generation failed: {e}"

        # Add metadata
        artifact = self._add_metadata(
            artifact_content,
            project_id,
            prompt_data["prompt_hash"],
            model_config,
            upstream_hash,
        )

        # Final validation pass
        is_valid, errors = self.validator.validate(artifact)

        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            return False, artifact, error_message

        # Save artifact to disk
        save_path = self.save_artifact(artifact, project_id)

        return True, artifact, f"Screenplay Step 5 board saved to {save_path}"

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 5 artifact due to downstream conflicts.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            step_4_artifact: Step 4 beat sheet artifact for context
            step_3_artifact: Step 3 hero/character artifact for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return (
                False,
                {},
                f"No existing Step 5 artifact found for project {project_id}",
            )

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Validate current to get errors
        _, current_errors = self.validator.validate(current_artifact)
        all_errors = [revision_reason] + current_errors

        fix_suggestions = self.validator.fix_suggestions(current_errors)

        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            all_errors,
            fix_suggestions,
            step_4_artifact,
            step_3_artifact,
        )

        # Default model config for board revision — needs high token budget for 40 cards
        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.3,
                "max_tokens": 12000,
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

        # Compute upstream hash
        upstream_content = json.dumps(
            {"step_4": step_4_artifact, "step_3": step_3_artifact},
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()

        # Add metadata
        artifact = self._add_metadata(
            artifact_content,
            project_id,
            prompt_data["prompt_hash"],
            model_config or {"model_name": "gpt-5.2-2025-12-11", "temperature": 0.3},
            upstream_hash,
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

        return (
            True,
            artifact,
            f"Screenplay Step 5 board revised and saved to {save_path}",
        )

    # ── Internal Helpers ───────────────────────────────────────────────

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
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        return artifact

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
                    e_start = card.get("emotional_start", card.get("emotional_polarity", "?"))
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

    def _snapshot_artifact(self, artifact: Dict[str, Any], project_id: str):
        """Save snapshot of current artifact before revision."""
        snapshot_path = self.project_dir / project_id / "snapshots"
        snapshot_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version = artifact.get("metadata", {}).get("version", "unknown")
        file_path = snapshot_path / f"sp_step_5_v{version}_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(
        self, project_id: str, reason: str, old_version: str, new_version: str
    ):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 5 revised from v{old_version} to v{new_version}\n"
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
            return True, "Step 5 board passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
