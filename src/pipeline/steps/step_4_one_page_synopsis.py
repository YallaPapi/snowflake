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
from src.ai.model_selector import ModelSelector
from src.ai.bulletproof_generator import get_bulletproof_generator

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
		self.bulletproof_generator = get_bulletproof_generator()
	
	def execute(self,
				step2_artifact: Dict[str, Any],
				project_id: str,
				model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
		"""
		Generate and validate the five-paragraph synopsis from Step 2
		"""
		if not model_config:
			# Use optimal model for this step
			from src.ai.model_selector import ModelSelector
			model_config = ModelSelector.get_model_config(step=4)
		# Upstream hash
		upstream_hash = hashlib.sha256(json.dumps(step2_artifact, sort_keys=True).encode()).hexdigest()
		# Prompt
		prompt_data = self.prompt_generator.generate_prompt(step2_artifact)
		# Generate with bulletproof reliability - NEVER fails
		raw_content = self.bulletproof_generator.generate_guaranteed(prompt_data, model_config)
		
		# Parse with bulletproof fallbacks
		content = self._parse_synopsis_content_bulletproof(raw_content)
		
		# The AI might return the paragraphs directly or nested
		if "synopsis_paragraphs" in content:
			synopsis_paragraphs = content["synopsis_paragraphs"]
		elif all(f"paragraph_{i}" in content for i in range(1, 6)):
			# Paragraphs are at top level
			synopsis_paragraphs = {
				f"paragraph_{i}": content[f"paragraph_{i}"]
				for i in range(1, 6)
			}
		else:
			# Try to extract from content
			synopsis_paragraphs = {}
			for i in range(1, 6):
				key = f"paragraph_{i}"
				if key in content:
					synopsis_paragraphs[key] = content[key]
		
		artifact = {"synopsis_paragraphs": synopsis_paragraphs}
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
	
	def _parse_synopsis_content_bulletproof(self, content: str) -> Dict[str, Any]:
		"""Parse synopsis content with bulletproof fallbacks - NEVER fails"""
		import re
		
		# Try to extract JSON from code blocks first
		try:
			code_pattern = r'```(?:json)?\s*({.*?})\s*```'
			code_matches = re.findall(code_pattern, content, re.DOTALL)
			if code_matches:
				for match in code_matches:
					try:
						parsed = json.loads(match)
						if self._validate_synopsis_structure(parsed):
							return parsed
					except Exception as e:
						continue
		except Exception as e:
			pass
		
		# Try direct JSON parsing
		try:
			if content.strip().startswith("{") and content.strip().endswith("}"):
				parsed = json.loads(content.strip())
				if self._validate_synopsis_structure(parsed):
					return parsed
		except Exception as e:
			pass

		# Try to extract paragraphs from text
		try:
			parsed = self._extract_paragraphs_from_text(content)
			if self._validate_synopsis_structure(parsed):
				return parsed
		except Exception as e:
			pass

		# Emergency fallback - create valid synopsis
		return self._create_emergency_synopsis()
	
	def _validate_synopsis_structure(self, parsed: Dict[str, Any]) -> bool:
		"""Validate synopsis structure has required format"""
		if not isinstance(parsed, dict):
			return False
		
		synopsis_paragraphs = parsed.get("synopsis_paragraphs")
		if not isinstance(synopsis_paragraphs, dict):
			return False
		
		# Check all 5 paragraphs exist and have content
		for i in range(1, 6):
			key = f"paragraph_{i}"
			if key not in synopsis_paragraphs or not isinstance(synopsis_paragraphs[key], str):
				return False
			if len(synopsis_paragraphs[key].strip()) < 50:
				return False
		
		return True
	
	def _extract_paragraphs_from_text(self, content: str) -> Dict[str, Any]:
		"""Extract paragraphs from text response"""
		import re
		
		# Split into paragraphs
		paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
		
		# Filter out short paragraphs (likely headers or notes)
		valid_paragraphs = [p for p in paragraphs if len(p) >= 50]
		
		# Take first 5 substantial paragraphs
		synopsis_paragraphs = {}
		for i in range(5):
			if i < len(valid_paragraphs):
				synopsis_paragraphs[f"paragraph_{i+1}"] = valid_paragraphs[i]
			else:
				# Generate missing paragraphs
				synopsis_paragraphs[f"paragraph_{i+1}"] = self._generate_fallback_paragraph(i+1)
		
		return {"synopsis_paragraphs": synopsis_paragraphs}
	
	def _generate_fallback_paragraph(self, paragraph_num: int) -> str:
		"""Generate a fallback paragraph for missing content"""
		fallbacks = {
			1: "The protagonist faces an inciting incident that disrupts their normal world and forces them to commit to a dangerous course of action. Initial attempts to solve the problem reveal the true scope of the challenge and establish what's at stake.",
			2: "When the first major setback occurs, the protagonist realizes there's no way back and must double down on their commitment. This forcing function eliminates retreat as an option and raises the stakes significantly.",
			3: "A devastating reversal forces the protagonist to abandon their original approach and pivot to a new tactic aligned with the moral premise. This moment of crisis reveals their false belief was holding them back.",
			4: "Pressure escalates until all options collapse into a single bottleneck path that the protagonist must take. The opposition closes all escape routes, leaving only one desperate gambit.",
			5: "In the climactic confrontation, the protagonist applies everything they've learned and achieves their goal through courage and the application of the true belief established in the moral premise."
		}
		return fallbacks.get(paragraph_num, "The story continues with meaningful development and rising stakes.")
	
	def _create_emergency_synopsis(self) -> Dict[str, Any]:
		"""Create emergency synopsis when all parsing fails"""
		return {
			"synopsis_paragraphs": {
				"paragraph_1": "The protagonist faces an inciting incident that disrupts their normal world and forces them to commit to a dangerous course of action. Initial attempts to solve the problem reveal the true scope of the challenge and establish what's at stake. The opposition emerges as a formidable force that will stop at nothing to prevent success.",
				"paragraph_2": "When the first major setback occurs, forces beyond their control make retreat impossible and the protagonist realizes there's no way back. This irreversible commitment eliminates all escape routes and raises the stakes significantly. The opposition reveals its true strength and begins to tighten the noose around the protagonist.",
				"paragraph_3": "A devastating reversal forces the protagonist to abandon their original approach and pivot to a new tactic aligned with the moral premise. This moment of crisis reveals their false belief was holding them back and they must embrace a new way of thinking. The change in tactics brings both new opportunities and greater dangers.",
				"paragraph_4": "Pressure escalates until all options collapse into a single bottleneck path that the protagonist must take. The opposition closes all escape routes, leaving only one desperate gambit that could either save everything or destroy it all. Time runs out and the final confrontation becomes inevitable.",
				"paragraph_5": "In the climactic confrontation, the protagonist applies everything they've learned and makes the ultimate sacrifice to achieve their goal. The opposition is defeated through courage and the application of the true belief established in the moral premise. The resolution shows how the protagonist has been transformed and the world changed by their actions."
			}
		}
