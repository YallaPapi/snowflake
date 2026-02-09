"""
Step 2 Implementation: Genre Classification (Save the Cat Ch.2)
Classifies the story into one of Blake Snyder's 10 structural genres.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_2_validator import Step2Validator
from src.screenplay_engine.pipeline.prompts.step_2_prompt import Step2Prompt
from src.ai.generator import AIGenerator


class Step2Genre:
    """
    Step 2: Genre Classification
    Classifies the story into one of 10 Snyder structural genres
    using the logline (Step 1) and Snowflake synopsis data.
    """

    VERSION = "1.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 2 executor.

        Args:
            project_dir: Directory to store artifacts.
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step2Validator()
        self.prompt_generator = Step2Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 2: Classify the story into a Snyder genre.

        Args:
            step_1_artifact: Validated Step 1 logline artifact.
            snowflake_artifacts: Snowflake pipeline outputs (synopsis data).
            project_id: Project identifier. Generated if not provided.
            model_config: AI model configuration overrides.

        Returns:
            Tuple of (success, artifact, message).
        """
        # Generate project ID if not provided
        if not project_id:
            project_id = str(uuid.uuid4())

        # Default model config
        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.3,
                "max_tokens": 4000,
            }

        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(
            step_1_artifact, snowflake_artifacts
        )

        # Call AI generator with validation
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
            prompt_data.get("prompt_hash", ""),
            model_config,
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
        save_path = self._save_artifact(artifact, project_id)

        return True, artifact, f"Step 2 genre classification saved to {save_path}"

    def _add_metadata(
        self,
        content: Dict[str, Any],
        project_id: str,
        prompt_hash: str,
        model_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add required metadata to the artifact."""
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 2,
            "step_name": "Genre Classification",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
        }
        return artifact

    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save the genre classification artifact to disk."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        artifact_path = project_path / "sp_step_2_genre.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        return artifact_path

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 2 artifact due to diagnostic checkpoint failures.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed (checkpoint failure details)
            step_1_artifact: Logline artifact for context
            snowflake_artifacts: Original Snowflake artifacts for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 2 artifact found for project {project_id}"

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Validate current to get structural errors
        _, current_errors = self.validator.validate(current_artifact)
        all_errors = [revision_reason] + current_errors
        fix_suggestions = self.validator.fix_suggestions(current_errors)

        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            all_errors,
            fix_suggestions,
            step_1_artifact,
            snowflake_artifacts,
        )

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
            prompt_data.get("prompt_hash", ""),
            model_config or {"model_name": "gpt-5.2-2025-12-11", "temperature": 0.3},
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
        save_path = self._save_artifact(artifact, project_id)

        # Log change
        self._log_change(project_id, revision_reason, old_version, new_version)

        return True, artifact, f"Step 2 genre classification revised and saved to {save_path}"

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load an existing Step 2 artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_2_genre.json"
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
        file_path = snapshot_path / f"sp_step_2_v{version}_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 2 revised from v{old_version} to v{new_version}\n"
            )
            f.write(f"  Reason: {reason}\n\n")

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate an artifact without executing generation.

        Args:
            artifact: The artifact to validate.

        Returns:
            Tuple of (is_valid, message).
        """
        is_valid, errors = self.validator.validate(artifact)

        if is_valid:
            return True, "Step 2 genre classification passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
