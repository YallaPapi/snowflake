"""
Step 1 Implementation: One Sentence Summary (Logline)
Executes Step 1 of the Snowflake Method to create the logline
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_1_validator import Step1Validator
from src.pipeline.prompts.step_1_prompt import Step1Prompt
from src.ai.generator import AIGenerator

class Step1OneSentenceSummary:
    """
    Step 1: One Sentence Summary (Logline)
    Creates a single sentence naming 1-2 leads and their external story goal
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 1 executor
        
        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = Step1Validator()
        self.prompt_generator = Step1Prompt()
        self.generator = AIGenerator()
        
    def execute(self,
                step_0_artifact: Dict[str, Any],
                story_brief: str,
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 1: Generate One Sentence Summary (Logline)
        """
        # Default model config
        if not model_config:
            model_config = {
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.2,  # Lower for more focused output
                "seed": 42
            }
        
        # Calculate upstream hash
        upstream_content = json.dumps(step_0_artifact, sort_keys=True)
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()
        
        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(step_0_artifact, story_brief)
        
        # Call AI generator to produce a raw logline (text)
        try:
            raw_output = self.generator.generate(prompt_data, model_config)
        except Exception as e:
            return False, {}, f"AI generation failed: {e}"
        
        # Create artifact from raw output
        logline = raw_output.strip().strip('"')
        artifact = {
            "logline": logline,
            "word_count": len(logline.split())
        }
        
        # Add metadata
        artifact = self.add_metadata(
            artifact,
            project_id,
            prompt_data["prompt_hash"],
            model_config,
            upstream_hash
        )
        
        # Validate artifact
        is_valid, errors = self.validator.validate(artifact)
        
        if not is_valid:
            # Try compression if too long
            if any("TOO LONG" in e for e in errors) and artifact['word_count'] > 25:
                compressed = self.compress_logline(logline, step_0_artifact, model_config)
                artifact['logline'] = compressed
                artifact['word_count'] = len(compressed.split())
                # Re-validate
                is_valid, errors = self.validator.validate(artifact)
        
        if not is_valid:
            # Get fix suggestions
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "VALIDATION FAILED:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            return False, artifact, error_message
        
        # Save artifact
        save_path = self.save_artifact(artifact, project_id)
        
        return True, artifact, f"Step 1 artifact saved to {save_path}"
    
    def compress_logline(self,
                        draft_logline: str,
                        step_0_artifact: Dict[str, Any],
                        model_config: Dict[str, Any]) -> str:
        """
        Compress an overlong logline to ≤25 words
        
        Args:
            draft_logline: The current draft
            step_0_artifact: Step 0 context
            model_config: AI model configuration
            
        Returns:
            Compressed logline
        """
        word_count = len(draft_logline.split())
        prompt_data = self.prompt_generator.generate_compression_prompt(draft_logline, word_count)
        
        # Here we would call AI model for compression
        # compressed = self.call_ai_model(prompt_data, model_config)
        
        # For now, use the validator's compression helper
        compressed = self.validator.compress_logline(draft_logline)
        
        return compressed
    
    def revise(self,
               project_id: str,
               validation_errors: List[str],
               model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise existing Step 1 artifact based on validation errors
        
        Args:
            project_id: Project UUID
            validation_errors: List of validation errors to fix
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact and Step 0
        current_artifact = self.load_artifact(project_id, 1)
        step_0_artifact = self.load_artifact(project_id, 0)
        
        if not current_artifact or not step_0_artifact:
            return False, {}, "Missing required artifacts"
        
        # Snapshot current version
        self.snapshot_artifact(current_artifact, project_id)
        
        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact['logline'],
            validation_errors,
            step_0_artifact
        )
        
        # Here we would call AI for revision
        # revised_logline = self.call_ai_model(prompt_data, model_config)
        
        # For demonstration
        revised_logline = current_artifact['logline']
        
        # Update artifact
        current_artifact['logline'] = revised_logline
        current_artifact['word_count'] = len(revised_logline.split())
        
        # Update version
        old_version = current_artifact['metadata']['version']
        major, minor, patch = map(int, old_version.split('.'))
        current_artifact['metadata']['version'] = f"{major}.{minor + 1}.0"
        
        # Re-validate
        is_valid, errors = self.validator.validate(current_artifact)
        
        if not is_valid:
            suggestions = self.validator.fix_suggestions(errors)
            error_message = "REVISION STILL FAILING:\n"
            for error, suggestion in zip(errors, suggestions):
                error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            return False, current_artifact, error_message
        
        # Save revised artifact
        save_path = self.save_artifact(current_artifact, project_id)
        
        return True, current_artifact, f"Step 1 artifact revised and saved to {save_path}"
    
    def add_metadata(self,
                     content: Dict[str, Any],
                     project_id: str,
                     prompt_hash: str,
                     model_config: Dict[str, Any],
                     upstream_hash: str) -> Dict[str, Any]:
        """Add required metadata to artifact"""
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 1,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.2),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash
        }
        return artifact
    
    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk"""
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        # Save JSON artifact
        artifact_path = project_path / "step_1_one_sentence_summary.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        # Save human-readable version
        readable_path = project_path / "step_1_one_sentence_summary.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("STEP 1: ONE SENTENCE SUMMARY (LOGLINE)\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"LOGLINE: {artifact.get('logline', 'ERROR: MISSING')}\n\n")
            f.write(f"Word Count: {artifact.get('word_count', 0)}/25\n")
            f.write(f"Named Leads: {artifact.get('lead_count', 0)}/2\n")
            
            if 'components' in artifact:
                f.write("\nPARSED COMPONENTS:\n")
                for key, value in artifact['components'].items():
                    f.write(f"  {key}: {value}\n")
            
            f.write(f"\nGenerated: {artifact['metadata']['created_at']}\n")
            f.write(f"Version: {artifact['metadata']['version']}\n")
        
        return artifact_path
    
    def load_artifact(self, project_id: str, step: int) -> Optional[Dict[str, Any]]:
        """Load existing artifact"""
        step_files = {
            0: "step_0_first_things_first.json",
            1: "step_1_one_sentence_summary.json"
        }
        
        artifact_path = self.project_dir / project_id / step_files.get(step, "")
        if not artifact_path.exists():
            return None
        
        with open(artifact_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def snapshot_artifact(self, artifact: Dict[str, Any], project_id: str):
        """Save snapshot of current artifact before revision"""
        project_path = self.project_dir / project_id / "snapshots"
        project_path.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version = artifact.get("metadata", {}).get("version", "unknown")
        snapshot_path = project_path / f"step_1_v{version}_{timestamp}.json"
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate an artifact without executing generation
        
        Args:
            artifact: The artifact to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        is_valid, errors = self.validator.validate(artifact)
        
        if is_valid:
            word_count = artifact.get('word_count', 0)
            lead_count = artifact.get('lead_count', 0)
            return True, f"✓ Step 1 logline passes all checks ({word_count} words, {lead_count} leads)"
        
        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
        
        return False, error_message