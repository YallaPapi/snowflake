"""
Step 5 Implementation: Character Synopses
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.pipeline.validators.step_5_validator import Step5Validator
from src.pipeline.prompts.step_5_prompt import Step5Prompt
from src.ai.generator import AIGenerator
from src.ai.model_selector import ModelSelector

class Step5CharacterSynopses:
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step5Validator()
        self.prompt_generator = Step5Prompt()
        self.generator = AIGenerator()

    def execute(self,
                step3_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        if not model_config:
            # Use optimal model for this step
            from src.ai.model_selector import ModelSelector
            model_config = ModelSelector.get_model_config(step=5)
        upstream_hash = hashlib.sha256(json.dumps(step3_artifact, sort_keys=True).encode()).hexdigest()
        prompt = self.prompt_generator.generate_prompt(step3_artifact)
        try:
            content = self.generator.generate_with_validation(prompt, self.validator, model_config)
        except Exception as e:
            return False, {}, f"AI generation failed: {e}"
        artifact = {"characters": content.get("characters", [])}
        artifact = self.add_metadata(artifact, project_id, prompt["prompt_hash"], model_config, upstream_hash)
        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            fixes = self.validator.fix_suggestions(errors)
            return False, artifact, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errors, fixes))
        path = self.save_artifact(artifact, project_id)
        return True, artifact, f"Step 5 artifact saved to {path}"

    def add_metadata(self, content: Dict[str, Any], project_id: str, prompt_hash: str, model_config: Dict[str, Any], upstream_hash: str) -> Dict[str, Any]:
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 5,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", self.generator.default_model if hasattr(self.generator, "default_model") else "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        return artifact

    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        p = project_path / "step_5_character_synopses.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        return p

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        ok, errs = self.validator.validate(artifact)
        if ok:
            return True, "✓ Step 5 character synopses pass validation"
        fixes = self.validator.fix_suggestions(errs)
        return False, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))
