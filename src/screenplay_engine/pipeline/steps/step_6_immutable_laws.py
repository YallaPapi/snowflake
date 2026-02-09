"""
Step 6 Implementation: Immutable Laws Validation (Save the Cat Ch.6)
Evaluates the Board and Beat Sheet against Blake Snyder's 7 Immutable Laws
of Screenplay Physics. This is a VALIDATION GATE -- the board must pass
all 7 laws before proceeding to screenplay writing.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_6_validator import Step6Validator
from src.screenplay_engine.pipeline.prompts.step_6_prompt import Step6Prompt
from src.ai.generator import AIGenerator


class Step6ImmutableLaws:
    """
    Screenplay Engine Step 6: Immutable Laws Validation

    Takes the finished screenplay_artifact plus step_5_artifact (Board),
    step_4_artifact (Beat Sheet), and step_3_artifact (Hero) and evaluates
    the FINISHED SCREENPLAY against all 7 Immutable Laws of Screenplay Physics.

    This step is a VALIDATION GATE. If any law fails, the step returns
    success=False with fix suggestions for screenplay revision.
    """

    VERSION = "2.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 6 executor.

        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step6Validator()
        self.prompt_generator = Step6Prompt()
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
        Execute Step 6: Evaluate finished screenplay against 7 Immutable Laws.

        Args:
            screenplay_artifact: Finished screenplay artifact (Step 6/8 output).
            step_5_artifact: Validated Step 5 Board artifact (scene cards).
            step_4_artifact: Validated Step 4 Beat Sheet artifact (15 beats).
            step_3_artifact: Validated Step 3 Hero artifact (hero profile).
            project_id: Project UUID (auto-generated if not provided).
            model_config: AI model configuration overrides.

        Returns:
            Tuple of (success, artifact, message).
            success is True ONLY if all 7 laws pass.
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
            error_message = "IMMUTABLE LAWS VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

            # Save artifact even on failure for inspection
            self.save_artifact(artifact, project_id)

            return False, artifact, error_message

        # Save artifact to disk
        save_path = self.save_artifact(artifact, project_id)

        return True, artifact, f"Screenplay Step 6 Immutable Laws saved to {save_path}"

    # ── Internal Helpers ───────────────────────────────────────────────

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
            "step": "sp_6",
            "step_name": "Immutable Laws (Save the Cat Ch.6)",
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
        artifact_path = project_path / "sp_step_6_immutable_laws.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_6_immutable_laws.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 6: IMMUTABLE LAWS (Save the Cat Ch.6)\n")
            f.write("=" * 55 + "\n\n")

            all_passed = artifact.get("all_passed", False)
            f.write(f"Overall Result: {'ALL PASSED' if all_passed else 'FAILED'}\n\n")

            laws = artifact.get("laws", [])
            for law in laws:
                if isinstance(law, dict):
                    num = law.get("law_number", "?")
                    name = law.get("law_name", "Unknown")
                    passed = law.get("passed", False)
                    status = "PASS" if passed else "FAIL"
                    f.write(f"Law {num}: {name} [{status}]\n")
                    if not passed:
                        f.write(f"  Violation: {law.get('violation_details', 'N/A')}\n")
                        f.write(f"  Fix: {law.get('fix_suggestion', 'N/A')}\n")
                    f.write("\n")

            f.write(f"Generated: {artifact.get('metadata', {}).get('created_at', 'N/A')}\n")
            f.write(f"Version: {artifact.get('metadata', {}).get('version', 'N/A')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_6_immutable_laws.json"
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
            return True, "Step 6 Immutable Laws passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
