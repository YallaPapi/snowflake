"""
Step 9 Implementation: Marketing Validation (Save the Cat Ch.8 "Final Fade In")
Final validation step - checks if the finished screenplay still matches
the logline that sold it, per Blake Snyder Chapter 8.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_9_validator import Step9Validator
from src.screenplay_engine.pipeline.prompts.step_9_prompt import Step9Prompt
from src.ai.generator import AIGenerator


class Step9Marketing:
    """
    Step 9: Marketing Validation (Save the Cat Ch.8)
    Checks that the finished screenplay still delivers on the promise
    of its logline, genre, and audience.
    """

    VERSION = "2.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 9 executor.

        Args:
            project_dir: Directory to store artifacts.
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step9Validator()
        self.prompt_generator = Step9Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_8_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 9: Marketing Validation.

        Takes the completed screenplay (step 8) and original logline (step 1)
        and validates that the screenplay still delivers on the logline's promise.

        Args:
            step_8_artifact: Complete screenplay artifact from Step 8.
            step_1_artifact: Original logline artifact from Step 1.
            project_id: Optional project UUID. Generated if not provided.
            model_config: Optional AI model configuration.

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
                "seed": 42,
            }

        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(
            step_8_artifact, step_1_artifact
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
            prompt_data["prompt_hash"],
            model_config,
        )

        # Validate artifact (final pass)
        is_valid, errors = self.validator.validate(artifact)

        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            return False, artifact, error_message

        # Save artifact
        save_path = self._save_artifact(artifact, project_id)

        return True, artifact, f"Step 9 artifact saved to {save_path}"

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
            "step": "sp_9",
            "step_name": "Marketing Validation (Save the Cat Ch.8)",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
        }
        return artifact

    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk as sp_step_9_marketing.json."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        artifact_path = project_path / "sp_step_9_marketing.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = (
            self.project_dir / project_id / "sp_step_9_marketing.json"
        )
        if not artifact_path.exists():
            return None

        with open(artifact_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_only(
        self, artifact: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate an artifact without executing generation.

        Args:
            artifact: The artifact to validate.

        Returns:
            Tuple of (is_valid, message).
        """
        is_valid, errors = self.validator.validate(artifact)

        if is_valid:
            return True, "Step 9 marketing validation passes all checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
