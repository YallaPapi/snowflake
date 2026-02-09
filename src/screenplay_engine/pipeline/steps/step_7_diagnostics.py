"""
Step 7 Implementation: Diagnostic Checks (Save the Cat Ch.7)
Executes 9 script-doctor diagnostics against the Board, Beat Sheet, and Hero profile.

Unlike Step 6 (hard gate), Step 7 diagnostics report problems WITH fixes --
the step succeeds even if diagnostics find issues, as long as the diagnostic
checks themselves ran properly.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_7_validator import Step7Validator
from src.screenplay_engine.pipeline.prompts.step_7_prompt import Step7Prompt
from src.ai.generator import AIGenerator


class Step7Diagnostics:
    """
    Screenplay Engine Step 7: Diagnostic Checks

    Takes the finished screenplay_artifact plus step_5_artifact (Board),
    step_4_artifact (Beat Sheet), and step_3_artifact (Hero profile), then
    runs 9 Blake Snyder Ch.7 diagnostic checks on the FINISHED SCREENPLAY.
    The step succeeds as long as all 9 diagnostics were executed -- individual
    check failures are reported with fixes but do NOT block the pipeline.
    """

    VERSION = "2.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 7 executor.

        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step7Validator()
        self.prompt_generator = Step7Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        screenplay_artifact: Dict[str, Any],
        step_5_artifact: Dict[str, Any],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 7: Run 9 diagnostic checks on finished screenplay.

        Args:
            screenplay_artifact: Finished screenplay artifact (Step 6/8 output).
            step_5_artifact: Validated Step 5 Board artifact.
            step_4_artifact: Validated Step 4 Beat Sheet artifact.
            step_3_artifact: Validated Step 3 Hero profile artifact.
            project_id: Project UUID (auto-generated if not provided).
            model_config: AI model configuration overrides.

        Returns:
            Tuple of (success, artifact, message).
            success is True as long as all 9 checks ran, regardless of
            whether individual checks passed or failed.
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

        # Generate prompt from upstream artifacts (screenplay is primary evaluation target)
        prompt_data = self.prompt_generator.generate_prompt(
            screenplay_artifact, step_5_artifact, step_4_artifact, step_3_artifact
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

        # Build summary message
        checks_passed = artifact.get("checks_passed_count", 0)
        total_checks = artifact.get("total_checks", 9)
        message = (
            f"Screenplay Step 7 diagnostics saved to {save_path} "
            f"({checks_passed}/{total_checks} checks passed)"
        )

        return True, artifact, message

    # -- Internal Helpers --------------------------------------------------

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
            "step": "sp_7",
            "step_name": "Diagnostic Checks (Save the Cat Ch.7)",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
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
        artifact_path = project_path / "sp_step_7_diagnostics.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_7_diagnostics.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 7: DIAGNOSTIC CHECKS (Save the Cat Ch.7)\n")
            f.write("=" * 60 + "\n\n")

            checks_passed = artifact.get("checks_passed_count", 0)
            total_checks = artifact.get("total_checks", 9)
            f.write(f"Result: {checks_passed}/{total_checks} checks passed\n\n")

            diagnostics = artifact.get("diagnostics", [])
            for diag in diagnostics:
                status = "PASS" if diag.get("passed") else "FAIL"
                f.write(f"  [{status}] {diag.get('check_number', '?')}. "
                        f"{diag.get('check_name', 'Unknown')}\n")
                if not diag.get("passed"):
                    f.write(f"         Problem: {diag.get('problem_details', '')}\n")
                    f.write(f"         Fix:     {diag.get('fix_suggestion', '')}\n")
                f.write("\n")

            f.write(f"Generated: {artifact.get('metadata', {}).get('created_at', 'N/A')}\n")
            f.write(f"Version: {artifact.get('metadata', {}).get('version', 'N/A')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_7_diagnostics.json"
        if not artifact_path.exists():
            return None

        with open(artifact_path, 'r', encoding='utf-8') as f:
            return json.load(f)

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
            return True, "Step 7 diagnostics pass all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
