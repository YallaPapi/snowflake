"""
Step 4 Implementation: One-Page Synopsis
Expands Step 2's five sentences into five causal paragraphs
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.pipeline.validators.step_4_validator import Step4Validator
from src.pipeline.prompts.step_4_prompt import Step4Prompt
from src.ai.generator import AIGenerator

class Step4OnePageSynopsis:
	"""
	Step 4: One-Page Synopsis
	Expands the one-paragraph summary into a one-page synopsis
	"""
	
	def __init__(self, project_dir: str = "artifacts"):
		self.project_dir = Path(project_dir)
		self.project_dir.mkdir(parents=True, exist_ok=True)
		self.validator = Step4Validator()
		self.prompt_generator = Step4Prompt()
		self.generator = AIGenerator()
	
	def execute(self,
				step2_artifact: Dict[str, Any],
				project_id: str,
				model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
		"""
		Generate and validate the five-paragraph synopsis from Step 2
		"""
		if not model_config:
			model_config = {"temperature": 0.3}
		# Upstream hash
		upstream_hash = hashlib.sha256(json.dumps(step2_artifact, sort_keys=True).encode()).hexdigest()
		# Prompt
		prompt_data = self.prompt_generator.generate_prompt(step2_artifact)
		# Generate with validation
		try:
			content = self.generator.generate_with_validation(prompt_data, self.validator, model_config)
		except Exception as e:
			return False, {}, f"AI generation failed: {e}"
		# Ensure structure
		artifact = {"synopsis_paragraphs": content.get("synopsis_paragraphs", {})}
		artifact = self.add_metadata(artifact, project_id, prompt_data["prompt_hash"], model_config, upstream_hash)
		# Validate final
		is_valid, errors = self.validator.validate(artifact)
		if not is_valid:
			fixes = self.validator.fix_suggestions(errors)
			msg = "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes))
			return False, artifact, msg
		# Save
		path = self.save_artifact(artifact, project_id)
		return True, artifact, f"Step 4 artifact saved to {path}"
	
	def add_metadata(self,
					 content: Dict[str, Any],
					 project_id: str,
					 prompt_hash: str,
					 model_config: Dict[str, Any],
					 upstream_hash: str) -> Dict[str, Any]:
		artifact = content.copy()
		artifact["metadata"] = {
			"project_id": project_id,
			"step": 4,
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
		artifact_path = project_path / "step_4_one_page_synopsis.json"
		with open(artifact_path, "w", encoding="utf-8") as f:
			json.dump(artifact, f, indent=2, ensure_ascii=False)
		# Also .md
		readable = project_path / "step_4_one_page_synopsis.md"
		with open(readable, "w", encoding="utf-8") as f:
			for i in range(1, 6):
				f.write(artifact.get("synopsis_paragraphs", {}).get(f"paragraph_{i}", "") + "\n\n")
			f.write(f"---\nGenerated: {artifact['metadata']['created_at']}\n")
			f.write(f"Version: {artifact['metadata']['version']}\n")
		return artifact_path
	
	def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
		is_valid, errors = self.validator.validate(artifact)
		if is_valid:
			return True, "✓ Step 4 synopsis passes all validation checks"
		fixes = self.validator.fix_suggestions(errors)
		msg = "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes))
		return False, msg
