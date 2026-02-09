"""
Step 1 Implementation: Logline (Save the Cat)
Executes Screenplay Engine Step 1 to generate a validated logline from Snowflake artifacts.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_1_validator import Step1Validator
from src.screenplay_engine.pipeline.prompts.step_1_prompt import Step1Prompt
from src.ai.generator import AIGenerator


class Step1Logline:
    """
    Screenplay Engine Step 1: Logline

    Takes Snowflake artifacts (step_0 and step_1) and generates a
    Save the Cat logline with irony, killer title, hero/villain
    adjectives, and primal goal.
    """

    VERSION = "1.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 1 executor.

        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step1Validator()
        self.prompt_generator = Step1Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        snowflake_artifacts: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 1: Generate logline artifact from Snowflake outputs.

        Args:
            snowflake_artifacts: Dict with keys 'step_0' and 'step_1' from the
                Snowflake pipeline.  step_0 must contain category, story_kind,
                audience_delight.  step_1 must contain logline.
            project_id: Project UUID (auto-generated if not provided)
            model_config: AI model configuration overrides

        Returns:
            Tuple of (success, artifact, message)
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

        # Generate prompt from Snowflake artifacts
        prompt_data = self.prompt_generator.generate_prompt(snowflake_artifacts)

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

        return True, artifact, f"Screenplay Step 1 logline saved to {save_path}"

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        snowflake_artifacts: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 1 artifact due to downstream conflicts.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            snowflake_artifacts: Original Snowflake artifacts for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 1 artifact found for project {project_id}"

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            [revision_reason],
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
            prompt_data["prompt_hash"],
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
        save_path = self.save_artifact(artifact, project_id)

        # Log change
        self._log_change(project_id, revision_reason, old_version, new_version)

        return True, artifact, f"Screenplay Step 1 logline revised and saved to {save_path}"

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
            "step": "sp_1",
            "step_name": "Logline (Save the Cat)",
            "version": "1.0.0",
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
        artifact_path = project_path / "sp_step_1_logline.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_1_logline.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 1: LOGLINE (Save the Cat Ch.1)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Title: {artifact.get('title', 'ERROR: MISSING')}\n")
            f.write(f"Logline: {artifact.get('logline', 'ERROR: MISSING')}\n\n")
            f.write(f"--- Component 1: Irony ---\n")
            f.write(f"Ironic Element: {artifact.get('ironic_element', 'ERROR: MISSING')}\n")
            f.write(f"Hero Adjective: {artifact.get('hero_adjective', 'ERROR: MISSING')}\n\n")
            f.write(f"--- Component 2: Mental Picture ---\n")
            f.write(f"Character Type: {artifact.get('character_type', 'ERROR: MISSING')}\n")
            f.write(f"Time Frame: {artifact.get('time_frame', 'ERROR: MISSING')}\n")
            f.write(f"Story Beginning: {artifact.get('story_beginning', 'ERROR: MISSING')}\n")
            f.write(f"Story Ending: {artifact.get('story_ending', 'ERROR: MISSING')}\n\n")
            f.write(f"--- Component 3: Audience and Cost ---\n")
            f.write(f"Target Audience: {artifact.get('target_audience', 'ERROR: MISSING')}\n")
            f.write(f"Budget Tier: {artifact.get('budget_tier', 'ERROR: MISSING')}\n")
            f.write(f"Genre/Tone: {artifact.get('genre_tone', 'ERROR: MISSING')}\n\n")
            f.write(f"--- Component 4: Killer Title + High Concept ---\n")
            f.write(f"High Concept Score: {artifact.get('high_concept_score', 0)}/10\n")
            f.write(f"Poster Concept: {artifact.get('poster_concept', 'ERROR: MISSING')}\n")
            f.write(f"\nGenerated: {artifact.get('metadata', {}).get('created_at', 'N/A')}\n")
            f.write(f"Version: {artifact.get('metadata', {}).get('version', 'N/A')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_1_logline.json"
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
        file_path = snapshot_path / f"sp_step_1_v{version}_{timestamp}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_dir = self.project_dir / project_id
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "change_log.txt"

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 1 revised from v{old_version} to v{new_version}\n"
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
            return True, "Step 1 logline passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
