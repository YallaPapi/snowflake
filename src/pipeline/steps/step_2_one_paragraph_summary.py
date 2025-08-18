"""
Step 2 Implementation: One Paragraph Summary (Five Sentences)
Executes Step 2 of the Snowflake Method to create the five-sentence paragraph with moral premise
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_2_validator import Step2Validator
from src.pipeline.prompts.step_2_prompt import Step2Prompt

class Step2OneParagraphSummary:
    """
    Step 2: One Paragraph Summary
    Creates exactly five sentences with three disasters and moral premise
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 2 executor
        
        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = Step2Validator()
        self.prompt_generator = Step2Prompt()
        
    def execute(self,
                step_0_artifact: Dict[str, Any],
                step_1_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 2: Generate One Paragraph Summary
        
        Args:
            step_0_artifact: Validated Step 0 artifact (First Things First)
            step_1_artifact: Validated Step 1 artifact (Logline)
            project_id: Project UUID
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Default model config
        if not model_config:
            model_config = {
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.3,  # Slightly higher for creative disasters
                "seed": 42
            }
        
        # Calculate upstream hash (combines Step 0 and Step 1)
        upstream_content = json.dumps({
            "step_0": step_0_artifact,
            "step_1": step_1_artifact
        }, sort_keys=True)
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()
        
        # First brainstorm disasters
        brainstorm_prompt = self.prompt_generator.generate_disaster_brainstorm(
            step_0_artifact, step_1_artifact
        )
        
        # Here we would call AI for brainstorming
        # disaster_options = self.call_ai_model(brainstorm_prompt, model_config)
        
        # Generate main prompt
        prompt_data = self.prompt_generator.generate_prompt(step_0_artifact, step_1_artifact)
        
        # Here we would call the AI model - for now, return template
        # response = self.call_ai_model(prompt_data, model_config)
        
        # For demonstration, create sample paragraph and moral premise
        sample_paragraph = (
            "In modern-day Seattle, Sarah, a detective, must prove her suspect's innocence "
            "before the mob silences him permanently. "
            "When her own partner is revealed as the mole, she is forced to go rogue or "
            "watch an innocent man die. "
            "After discovering the conspiracy reaches the mayor's office, she realizes that "
            "playing by the rules will fail and must embrace deception to expose the truth. "
            "When the mob kidnaps her daughter as leverage, both Sarah and the crime boss "
            "must commit to a final confrontation that will destroy one of them. "
            "In the ultimate showdown at the docks, Sarah sacrifices her career but saves "
            "both her daughter and the innocent suspect."
        )
        
        sample_moral = (
            "People succeed when they sacrifice personal gain for truth, "
            "and they fail when they protect themselves at the cost of justice."
        )
        
        # Create artifact
        artifact = {
            "paragraph": sample_paragraph,
            "moral_premise": sample_moral,
            "sentence_count": 5  # Will be updated by validator
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
            # Try to fix with revision
            artifact = self.attempt_fixes(
                artifact, errors, step_0_artifact, step_1_artifact, model_config
            )
            
            # Re-validate after fixes
            is_valid, errors = self.validator.validate(artifact)
            
            if not is_valid:
                # Get fix suggestions
                suggestions = self.validator.fix_suggestions(errors)
                error_message = "VALIDATION FAILED:\n"
                for error, suggestion in zip(errors, suggestions):
                    error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
                return False, artifact, error_message
        
        # Save artifacts (both paragraph and moral premise)
        save_path = self.save_artifact(artifact, project_id)
        
        return True, artifact, f"Step 2 artifacts saved to {save_path}"
    
    def attempt_fixes(self,
                     artifact: Dict[str, Any],
                     errors: List[str],
                     step_0_artifact: Dict[str, Any],
                     step_1_artifact: Dict[str, Any],
                     model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to fix validation errors
        
        Args:
            artifact: Current artifact with errors
            errors: List of validation errors
            step_0_artifact: Step 0 context
            step_1_artifact: Step 1 context
            model_config: AI model configuration
            
        Returns:
            Updated artifact
        """
        # Generate revision prompt
        revision_prompt = self.prompt_generator.generate_revision_prompt(
            artifact.get('paragraph', ''),
            artifact.get('moral_premise', ''),
            errors,
            step_0_artifact,
            step_1_artifact
        )
        
        # Here we would call AI for revision
        # revised_response = self.call_ai_model(revision_prompt, model_config)
        
        # For now, return original with minor fixes
        if any("WRONG SENTENCE COUNT" in e for e in errors):
            # Ensure exactly 5 sentences
            sentences = self.validator.parse_sentences(artifact['paragraph'])
            if len(sentences['all']) != 5:
                # Would need AI to fix properly
                pass
        
        if any("INVALID MORAL PREMISE" in e for e in errors):
            # Generate proper moral premise
            moral_prompt = self.prompt_generator.generate_moral_premise_prompt(
                artifact['paragraph'],
                step_0_artifact
            )
            # moral_premise = self.call_ai_model(moral_prompt, model_config)
            # artifact['moral_premise'] = moral_premise
        
        return artifact
    
    def revise(self,
               project_id: str,
               validation_errors: List[str],
               model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise existing Step 2 artifact based on validation errors
        
        Args:
            project_id: Project UUID
            validation_errors: List of validation errors to fix
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifacts
        current_artifact = self.load_artifact(project_id, 2)
        step_0_artifact = self.load_artifact(project_id, 0)
        step_1_artifact = self.load_artifact(project_id, 1)
        
        if not all([current_artifact, step_0_artifact, step_1_artifact]):
            return False, {}, "Missing required artifacts"
        
        # Snapshot current version
        self.snapshot_artifact(current_artifact, project_id)
        
        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            current_artifact['paragraph'],
            current_artifact['moral_premise'],
            validation_errors,
            step_0_artifact,
            step_1_artifact
        )
        
        # Here we would call AI for revision
        # revised = self.call_ai_model(prompt_data, model_config)
        
        # Update artifact
        # current_artifact['paragraph'] = revised['paragraph']
        # current_artifact['moral_premise'] = revised['moral_premise']
        
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
        
        return True, current_artifact, f"Step 2 artifact revised and saved to {save_path}"
    
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
            "step": 2,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.3),
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
        
        # Save main JSON artifact
        artifact_path = project_path / "step_2_one_paragraph_summary.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        # Save moral premise separately for easy access
        moral_path = project_path / "moral_premise.json"
        moral_artifact = {
            "moral_premise": artifact.get('moral_premise', ''),
            "metadata": artifact.get('metadata', {})
        }
        with open(moral_path, 'w', encoding='utf-8') as f:
            json.dump(moral_artifact, f, indent=2, ensure_ascii=False)
        
        # Save human-readable version
        readable_path = project_path / "step_2_one_paragraph_summary.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("STEP 2: ONE PARAGRAPH SUMMARY (FIVE SENTENCES)\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("COMPLETE PARAGRAPH:\n")
            f.write("-" * 40 + "\n")
            f.write(artifact.get('paragraph', 'ERROR: MISSING') + "\n\n")
            
            if 'sentences' in artifact:
                f.write("SENTENCE BREAKDOWN:\n")
                f.write("-" * 40 + "\n")
                f.write(f"1. SETUP: {artifact['sentences'].get('setup', 'Missing')}\n\n")
                f.write(f"2. DISASTER #1: {artifact['sentences'].get('disaster_1', 'Missing')}\n\n")
                f.write(f"3. DISASTER #2 (Moral Pivot): {artifact['sentences'].get('disaster_2', 'Missing')}\n\n")
                f.write(f"4. DISASTER #3: {artifact['sentences'].get('disaster_3', 'Missing')}\n\n")
                f.write(f"5. RESOLUTION: {artifact['sentences'].get('resolution', 'Missing')}\n\n")
            
            f.write("MORAL PREMISE:\n")
            f.write("-" * 40 + "\n")
            f.write(artifact.get('moral_premise', 'ERROR: MISSING') + "\n\n")
            
            if 'moral_pivot' in artifact:
                f.write("MORAL PIVOT ANALYSIS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"False Belief: {artifact['moral_pivot'].get('false_belief', 'Unknown')}\n")
                f.write(f"True Belief: {artifact['moral_pivot'].get('true_belief', 'Unknown')}\n")
                f.write(f"Pivot Shown in D2: {'Yes' if artifact['moral_pivot'].get('pivot_shown') else 'No'}\n\n")
            
            if 'disasters' in artifact:
                f.write("DISASTER VALIDATION:\n")
                f.write("-" * 40 + "\n")
                f.write(f"D1 Present: {'✓' if artifact['disasters'].get('d1_present') else '✗'} ")
                f.write(f"(Type: {artifact['disasters'].get('d1_type', 'unknown')})\n")
                f.write(f"D2 Present: {'✓' if artifact['disasters'].get('d2_present') else '✗'} ")
                f.write(f"(Type: {artifact['disasters'].get('d2_type', 'unknown')})\n")
                f.write(f"D3 Present: {'✓' if artifact['disasters'].get('d3_present') else '✗'} ")
                f.write(f"(Type: {artifact['disasters'].get('d3_type', 'unknown')})\n\n")
            
            f.write(f"Sentence Count: {artifact.get('sentence_count', 0)}/5\n")
            f.write(f"Generated: {artifact['metadata']['created_at']}\n")
            f.write(f"Version: {artifact['metadata']['version']}\n")
        
        return artifact_path
    
    def load_artifact(self, project_id: str, step: int) -> Optional[Dict[str, Any]]:
        """Load existing artifact"""
        step_files = {
            0: "step_0_first_things_first.json",
            1: "step_1_one_sentence_summary.json",
            2: "step_2_one_paragraph_summary.json"
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
        snapshot_path = project_path / f"step_2_v{version}_{timestamp}.json"
        
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
            sentence_count = artifact.get('sentence_count', 0)
            disasters_present = sum([
                artifact.get('disasters', {}).get('d1_present', False),
                artifact.get('disasters', {}).get('d2_present', False),
                artifact.get('disasters', {}).get('d3_present', False)
            ])
            return True, f"✓ Step 2 paragraph passes all checks ({sentence_count} sentences, {disasters_present}/3 disasters, moral premise present)"
        
        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
        
        return False, error_message