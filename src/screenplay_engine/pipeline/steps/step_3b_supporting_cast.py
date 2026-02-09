"""
Step 3b Implementation: Supporting Cast
Defines all supporting characters BEFORE the Beat Sheet so the screenplay
has a canonical cast list. No character should be invented ad-hoc during writing.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_3b_validator import Step3bValidator
from src.screenplay_engine.pipeline.prompts.step_3b_prompt import Step3bPrompt
from src.ai.generator import AIGenerator


class Step3bSupportingCast:
    """
    Screenplay Engine Step 3b: Supporting Cast

    Takes logline (Step 1), genre (Step 2), hero/antagonist/b-story (Step 3),
    and Snowflake character data, then defines the complete supporting cast.
    """

    VERSION = "1.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step3bValidator()
        self.prompt_generator = Step3bPrompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        project_id: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 3b: Define the full supporting cast.

        Returns:
            Tuple of (success, artifact, message).
        """
        if not project_id:
            project_id = str(uuid.uuid4())

        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.5,
                "seed": 42,
            }

        prompt_data = self.prompt_generator.generate_prompt(
            step_1_artifact, step_2_artifact, step_3_artifact, snowflake_artifacts
        )

        try:
            artifact_content = self.generator.generate_with_validation(
                prompt_data, self.validator, model_config
            )
        except Exception as e:
            return False, {}, f"AI generation failed: {e}"

        artifact = self._add_metadata(
            artifact_content, project_id, prompt_data["prompt_hash"], model_config
        )

        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "SUPPORTING CAST VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            self.save_artifact(artifact, project_id)
            return False, artifact, error_message

        save_path = self.save_artifact(artifact, project_id)
        char_count = len(artifact.get("characters", []))
        return True, artifact, f"Step 3b Supporting Cast ({char_count} characters) saved to {save_path}"

    def _add_metadata(
        self, content: Dict[str, Any], project_id: str,
        prompt_hash: str, model_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": "sp_3b",
            "step_name": "Supporting Cast",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.5),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
        }
        return artifact

    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        artifact_path = project_path / "sp_step_3b_supporting_cast.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        readable_path = project_path / "sp_step_3b_supporting_cast.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("SCREENPLAY STEP 3b: SUPPORTING CAST\n")
            f.write("=" * 40 + "\n\n")
            characters = artifact.get("characters", [])
            for char in characters:
                if isinstance(char, dict):
                    f.write(f"  {char.get('name', '?')} ({char.get('role', '?')})\n")
                    f.write(f"    Relationship: {char.get('relationship_to_hero', '')}\n")
                    f.write(f"    Trait: {char.get('distinctive_trait', '')}\n")
                    f.write(f"    Voice: {char.get('voice_profile', '')}\n")
                    f.write(f"    First appears: {char.get('first_appearance_beat', '')}\n")
                    arc = char.get('arc_summary', '')
                    if arc:
                        f.write(f"    Arc: {arc}\n")
                    f.write("\n")
            f.write(f"Speaking roles: {artifact.get('total_speaking_roles', '?')}\n")
            f.write(f"Non-speaking: {artifact.get('total_non_speaking', '?')}\n")

        return artifact_path

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        artifact_path = self.project_dir / project_id / "sp_step_3b_supporting_cast.json"
        if not artifact_path.exists():
            return None
        with open(artifact_path, 'r', encoding='utf-8') as f:
            return json.load(f)
