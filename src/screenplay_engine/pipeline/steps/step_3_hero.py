"""
Step 3 Implementation: Hero Construction (Save the Cat)
Executes Screenplay Engine Step 3 to construct the protagonist, antagonist,
and B-story character from logline, genre, and Snowflake character data.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_3_validator import Step3Validator
from src.screenplay_engine.pipeline.prompts.step_3_prompt import Step3Prompt
from src.ai.generator import AIGenerator


class Step3Hero:
    """
    Screenplay Engine Step 3: Hero Construction

    Takes logline (Step 1), genre classification (Step 2), and
    Snowflake character data (steps 3, 5, 7) and constructs a complete
    Save the Cat hero profile with antagonist and B-story character.
    """

    VERSION = "2.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 3 executor.

        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.validator = Step3Validator()
        self.prompt_generator = Step3Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 3: Construct hero, antagonist, and B-story character.

        Args:
            step_1_artifact: Output from Screenplay Step 1 (logline v2.0.0).
                Must contain: logline, title, hero_adjective, character_type,
                ironic_element, time_frame, target_audience.
            step_2_artifact: Output from Screenplay Step 2 (genre classification).
                Must contain: genre, core_question, working_parts, rules.
            snowflake_artifacts: Dict with Snowflake pipeline outputs.
                Uses step_3 (character summaries), step_5 (character synopses),
                step_7 (character bibles) if available.
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

        # Generate prompt from inputs
        prompt_data = self.prompt_generator.generate_prompt(
            step_1_artifact, step_2_artifact, snowflake_artifacts
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

        return True, artifact, f"Screenplay Step 3 hero construction saved to {save_path}"

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 3 artifact due to downstream conflicts.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            step_1_artifact: Logline artifact for context
            step_2_artifact: Genre artifact for context
            snowflake_artifacts: Original Snowflake artifacts for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 3 artifact found for project {project_id}"

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            [revision_reason],
            step_1_artifact,
            step_2_artifact,
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

        return True, artifact, f"Screenplay Step 3 hero construction revised and saved to {save_path}"

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
            "step": "sp_3",
            "step_name": "Hero Construction (Save the Cat)",
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
        artifact_path = project_path / "sp_step_3_hero.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Save human-readable version
        readable_path = project_path / "sp_step_3_hero.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 3: HERO CONSTRUCTION (Save the Cat)\n")
            f.write("=" * 55 + "\n\n")

            hero = artifact.get("hero", {})
            f.write("--- HERO ---\n")
            f.write(f"Name: {hero.get('name', 'ERROR: MISSING')}\n")
            f.write(f"Descriptor: {hero.get('adjective_descriptor', 'ERROR: MISSING')}\n")
            f.write(f"Age Range: {hero.get('age_range', 'N/A')}\n")
            f.write(f"Gender: {hero.get('gender', 'N/A')}\n")
            f.write(f"Archetype: {hero.get('archetype', 'ERROR: MISSING')}\n")
            f.write(f"Primal Motivation: {hero.get('primal_motivation', 'ERROR: MISSING')}\n")
            f.write(f"Stated Goal: {hero.get('stated_goal', 'ERROR: MISSING')}\n")
            f.write(f"Actual Need: {hero.get('actual_need', 'ERROR: MISSING')}\n")
            f.write(f"Surface to Primal: {hero.get('surface_to_primal_connection', 'ERROR: MISSING')}\n")
            f.write(f"Max Conflict: {hero.get('maximum_conflict_justification', 'ERROR: MISSING')}\n")
            f.write(f"Longest Journey: {hero.get('longest_journey_justification', 'ERROR: MISSING')}\n")
            f.write(f"Demographic Appeal: {hero.get('demographic_appeal_justification', 'ERROR: MISSING')}\n")
            f.write(f"Save the Cat Moment: {hero.get('save_the_cat_moment', 'ERROR: MISSING')}\n")
            f.write(f"Opening State: {hero.get('opening_state', 'ERROR: MISSING')}\n")
            f.write(f"Final State: {hero.get('final_state', 'ERROR: MISSING')}\n")
            f.write(f"Theme Carrier: {hero.get('theme_carrier', 'ERROR: MISSING')}\n")

            six_things = hero.get("six_things_that_need_fixing", [])
            f.write("\nSix Things That Need Fixing:\n")
            for i, thing in enumerate(six_things, 1):
                f.write(f"  {i}. {thing}\n")

            antagonist = artifact.get("antagonist", {})
            f.write("\n--- ANTAGONIST ---\n")
            f.write(f"Name: {antagonist.get('name', 'ERROR: MISSING')}\n")
            f.write(f"Descriptor: {antagonist.get('adjective_descriptor', 'ERROR: MISSING')}\n")
            f.write(f"Power Level: {antagonist.get('power_level', 'ERROR: MISSING')}\n")
            f.write(f"Moral Difference: {antagonist.get('moral_difference', 'ERROR: MISSING')}\n")
            f.write(f"Mirror Principle: {antagonist.get('mirror_principle', 'ERROR: MISSING')}\n")

            b_story = artifact.get("b_story_character", {})
            f.write("\n--- B-STORY CHARACTER ---\n")
            f.write(f"Name: {b_story.get('name', 'ERROR: MISSING')}\n")
            f.write(f"Relationship: {b_story.get('relationship_to_hero', 'ERROR: MISSING')}\n")
            f.write(f"Theme Wisdom: {b_story.get('theme_wisdom', 'ERROR: MISSING')}\n")

            f.write(f"\nGenerated: {artifact.get('metadata', {}).get('created_at', 'N/A')}\n")
            f.write(f"Version: {artifact.get('metadata', {}).get('version', 'N/A')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_3_hero.json"
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
        file_path = snapshot_path / f"sp_step_3_v{version}_{timestamp}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 3 revised from v{old_version} to v{new_version}\n"
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
            return True, "Step 3 hero construction passes all validation checks"

        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"

        return False, error_message
