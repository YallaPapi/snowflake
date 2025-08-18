"""
Step 0 Implementation: First Things First
Executes Step 0 of the Snowflake Method to establish Story Market Position
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.pipeline.validators.step_0_validator import Step0Validator
from src.pipeline.prompts.step_0_prompt import Step0Prompt

class Step0FirstThingsFirst:
    """
    Step 0: First Things First
    Locks the STORY MARKET POSITION before any plotting
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 0 executor
        
        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = Step0Validator()
        self.prompt_generator = Step0Prompt()
        
    def execute(self, 
                brief: str,
                project_id: Optional[str] = None,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 0: Generate First Things First artifact
        
        Args:
            brief: The user's story idea/brief
            project_id: Optional project UUID (will generate if not provided)
            model_config: AI model configuration (name, temperature, seed)
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Generate project ID if not provided
        if not project_id:
            project_id = str(uuid.uuid4())
            
        # Default model config
        if not model_config:
            model_config = {
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.3,
                "seed": 42
            }
            
        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(brief)
        
        # Here we would call the AI model - for now, return template
        # In production, this would be:
        # artifact_content = self.call_ai_model(prompt_data, model_config)
        
        # For demonstration, create a sample artifact
        artifact_content = {
            "category": "TODO: Generate via AI",
            "story_kind": "TODO: Generate via AI",
            "audience_delight": "TODO: Generate via AI"
        }
        
        # Add metadata
        artifact = self.add_metadata(
            artifact_content,
            project_id,
            prompt_data["prompt_hash"],
            model_config
        )
        
        # Validate artifact
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
        
        return True, artifact, f"Step 0 artifact saved to {save_path}"
    
    def revise(self,
               project_id: str,
               revision_reason: str,
               model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise existing Step 0 artifact due to downstream conflicts
        
        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 0 artifact found for project {project_id}"
        
        # Snapshot current version
        self.snapshot_artifact(current_artifact, project_id)
        
        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact,
            revision_reason
        )
        
        # Here we would call the AI model for revision
        # artifact_content = self.call_ai_model(prompt_data, model_config)
        
        # For demonstration
        artifact_content = current_artifact.copy()
        artifact_content["_revision_note"] = revision_reason
        
        # Update version
        old_version = current_artifact.get("metadata", {}).get("version", "1.0.0")
        major, minor, patch = map(int, old_version.split("."))
        new_version = f"{major}.{minor + 1}.0"
        
        # Add updated metadata
        artifact = self.add_metadata(
            artifact_content,
            project_id,
            prompt_data["prompt_hash"],
            model_config or {"model_name": "claude-3-5-sonnet-20241022", "temperature": 0.3}
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
        self.log_change(project_id, revision_reason, old_version, new_version)
        
        return True, artifact, f"Step 0 artifact revised and saved to {save_path}"
    
    def add_metadata(self, 
                     content: Dict[str, Any],
                     project_id: str,
                     prompt_hash: str,
                     model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add required metadata to artifact"""
        artifact = content.copy()
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 0,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION
        }
        return artifact
    
    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk"""
        # Create project directory
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        # Save JSON artifact
        artifact_path = project_path / "step_0_first_things_first.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
            
        # Also save human-readable version
        readable_path = project_path / "step_0_first_things_first.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("STEP 0: FIRST THINGS FIRST\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Category: {artifact.get('category', 'ERROR: MISSING')}\n")
            f.write(f"Story Kind: {artifact.get('story_kind', 'ERROR: MISSING')}\n")
            f.write(f"Audience Delight: {artifact.get('audience_delight', 'ERROR: MISSING')}\n")
            f.write(f"\nGenerated: {artifact['metadata']['created_at']}\n")
            f.write(f"Version: {artifact['metadata']['version']}\n")
            
        return artifact_path
    
    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing artifact"""
        artifact_path = self.project_dir / project_id / "step_0_first_things_first.json"
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
        snapshot_path = project_path / f"step_0_v{version}_{timestamp}.json"
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
    
    def log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes"""
        log_path = self.project_dir / project_id / "change_log.txt"
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.utcnow().isoformat()} - Step 0 revised from v{old_version} to v{new_version}\n")
            f.write(f"  Reason: {reason}\n\n")
    
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
            return True, "✓ Step 0 artifact passes all validation checks"
        
        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
            
        return False, error_message