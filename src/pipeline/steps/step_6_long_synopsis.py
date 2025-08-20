"""
Step 6 Implementation: Long Synopsis
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.pipeline.validators.step_6_validator import Step6Validator
from src.pipeline.prompts.step_6_prompt import Step6Prompt
from src.ai.generator import AIGenerator
from src.ai.model_selector import ModelSelector

class Step6LongSynopsis:
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step6Validator()
        self.prompt_generator = Step6Prompt()
        self.generator = AIGenerator()

    def execute(self,
                step4_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        if not model_config:
            model_config = {
                "temperature": 0.4,
                "max_tokens": 4000  # Need more tokens for long synopsis
            }
        upstream_hash = hashlib.sha256(json.dumps(step4_artifact, sort_keys=True).encode()).hexdigest()
        prompt = self.prompt_generator.generate_prompt(step4_artifact)
        try:
            content = self.generator.generate_with_validation(prompt, self.validator, model_config)
        except Exception as e:
            return False, {}, f"AI generation failed: {e}"
        
        # Extract long synopsis from various possible formats
        if isinstance(content, str):
            long_synopsis = content
        elif "long_synopsis" in content:
            long_synopsis = content["long_synopsis"]
        elif "synopsis" in content:
            long_synopsis = content["synopsis"]
        elif "content" in content:
            long_synopsis = content["content"]
        elif "text" in content:
            long_synopsis = content["text"]
        elif "output" in content:
            long_synopsis = content["output"]
        else:
            # Try to get any string value from the dict
            for key, value in content.items():
                if isinstance(value, str) and len(value) > 100:
                    long_synopsis = value
                    break
            else:
                long_synopsis = str(content)
        
        artifact = {"long_synopsis": long_synopsis}
        artifact = self.add_metadata(artifact, project_id, prompt["prompt_hash"], model_config, upstream_hash)
        ok, errs = self.validator.validate(artifact)
        if not ok:
            fixes = self.validator.fix_suggestions(errs)
            return False, artifact, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))
        path = self.save_artifact(artifact, project_id)
        return True, artifact, f"Step 6 artifact saved to {path}"

    def add_metadata(self, content: Dict[str, Any], project_id: str, prompt_hash: str, model_config: Dict[str, Any], upstream_hash: str) -> Dict[str, Any]:
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 6,
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
        p = project_path / "step_6_long_synopsis.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        return p

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        ok, errs = self.validator.validate(artifact)
        if ok:
            return True, "✓ Step 6 long synopsis passes validation"
        fixes = self.validator.fix_suggestions(errs)
        return False, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))
