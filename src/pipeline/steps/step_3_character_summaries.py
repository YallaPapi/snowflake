"""
Step 3 Implementation: Character Summary Sheets
Executes Step 3 of the Snowflake Method to create character summaries
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_3_validator import Step3Validator
from src.pipeline.prompts.step_3_prompt import Step3Prompt

class Step3CharacterSummaries:
    """
    Step 3: Character Summary Sheets
    Creates complete character sheets for all major characters
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 3 executor
        
        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = Step3Validator()
        self.prompt_generator = Step3Prompt()
        
    def execute(self,
                step_0_artifact: Dict[str, Any],
                step_1_artifact: Dict[str, Any],
                step_2_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 3: Generate Character Summaries
        
        Args:
            step_0_artifact: Validated Step 0 artifact (First Things First)
            step_1_artifact: Validated Step 1 artifact (Logline)
            step_2_artifact: Validated Step 2 artifact (One Paragraph)
            project_id: Project UUID
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Default model config
        if not model_config:
            model_config = {
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.4,  # Higher for character creativity
                "seed": 42
            }
        
        # Calculate upstream hash (combines Steps 0-2)
        upstream_content = json.dumps({
            "step_0": step_0_artifact,
            "step_1": step_1_artifact,
            "step_2": step_2_artifact
        }, sort_keys=True)
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()
        
        # Generate main prompt
        prompt_data = self.prompt_generator.generate_prompt(
            step_0_artifact, step_1_artifact, step_2_artifact
        )
        
        # Here we would call the AI model - for now, create sample characters
        # characters = self.call_ai_model(prompt_data, model_config)
        
        # For demonstration, create sample characters
        sample_characters = [
            {
                "role": "Protagonist",
                "name": "Sarah Chen",
                "goal": "Expose the trafficking ring and save the victims before the FBI raid",
                "ambition": "Justice for the powerless",
                "values": [
                    "Nothing is more important than protecting innocent lives.",
                    "Nothing is more important than keeping my word to victims.",
                    "Nothing is more important than my sister's safety."
                ],
                "conflict": "Captain Morrison controls the police resources and blocks her investigation by reassigning her cases",
                "epiphany": "Realizes that working within a corrupt system enables evil, and true justice sometimes requires sacrifice of position",
                "one_sentence_summary": "A by-the-book detective learns to break rules when the system itself is corrupt.",
                "one_paragraph_summary": "Sarah begins as a respected detective confident in the system. When her partner is murdered (D1), she's forced to investigate alone, discovering the corruption goes to the top. After learning her captain runs the ring (D2), she abandons protocol to gather evidence as a vigilante. When traffickers kidnap her sister (D3), Sarah must choose between her badge and her family, ultimately sacrificing her career to save lives and expose the truth.",
                "interiority": {
                    "motive_history": "Lost her parents to gang violence as a child, joined force to fight crime legally",
                    "justification": "Believes the law exists to protect people, not institutions",
                    "vulnerability": "Her need for official validation blinds her to systemic corruption"
                }
            },
            {
                "role": "Antagonist",
                "name": "Captain Morrison",
                "goal": "Maintain control of the trafficking operation while appearing as exemplary police",
                "ambition": "Power and security for his family",
                "values": [
                    "Nothing is more important than my daughter's medical treatment.",
                    "Nothing is more important than maintaining control.",
                    "Nothing is more important than the appearance of order."
                ],
                "conflict": "Sarah's investigation threatens to expose his operation and destroy everything he's built",
                "epiphany": "NONE",
                "epiphany_justification": "Morrison is too invested in his justifications to change; he'd rather die than admit he became what he once fought",
                "one_sentence_summary": "A corrupt captain who began with noble intentions descends deeper into evil to protect his empire.",
                "one_paragraph_summary": "Morrison started as an idealistic cop but turned when his daughter got sick and insurance wouldn't cover treatment. By D1, he's eliminating threats like Sarah's partner. At D2, his network is exposed but he doubles down, using department resources against Sarah. By D3, he's desperate enough to kidnap civilians, having lost all moral boundaries in pursuit of control.",
                "interiority": {
                    "motive_history": "Daughter diagnosed with rare disease, medical bills exceeded salary, first bribe was 'just once' for medicine",
                    "justification": "The criminals he protects are less evil than the insurance companies that would let his child die",
                    "vulnerability": "His love for his daughter is both his motivation and his weakness"
                }
            },
            {
                "role": "Love Interest",
                "name": "Marcus Torres",
                "goal": "Protect Sarah while maintaining his undercover FBI position",
                "ambition": "Redemption for past failures",
                "values": [
                    "Nothing is more important than completing the mission.",
                    "Nothing is more important than protecting the innocent.",
                    "Nothing is more important than earning back trust."
                ],
                "conflict": "His FBI handlers forbid him from breaking cover even to save Sarah",
                "epiphany": "Learns that strict adherence to orders can be another form of moral cowardice",
                "one_sentence_summary": "An undercover agent must choose between his mission and the woman he loves.",
                "one_paragraph_summary": "Marcus infiltrated the trafficking ring seeking redemption after a botched operation. At D1, he witnesses the partner's murder but can't break cover. By D2, he's torn between FBI orders and helping Sarah. At D3, when Sarah's sister is taken, he finally chooses love over duty, breaking cover to help in the final confrontation."
            }
        ]
        
        # Create artifact
        artifact = {
            "characters": sample_characters,
            "character_count": len(sample_characters)
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
            # Attempt to fix issues
            artifact = self.attempt_fixes(
                artifact, errors, step_0_artifact, step_1_artifact, step_2_artifact, model_config
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
        
        # Enrich antagonist if needed
        antagonist = self.validator.get_character_by_role(artifact['characters'], 'Antagonist')
        if antagonist and 'interiority' not in antagonist:
            self.enrich_antagonist(antagonist, step_1_artifact, step_2_artifact, model_config)
        
        # Save artifact
        save_path = self.save_artifact(artifact, project_id)
        
        return True, artifact, f"Step 3 artifact saved to {save_path}"
    
    def attempt_fixes(self,
                     artifact: Dict[str, Any],
                     errors: List[str],
                     step_0_artifact: Dict[str, Any],
                     step_1_artifact: Dict[str, Any],
                     step_2_artifact: Dict[str, Any],
                     model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to fix validation errors
        
        Args:
            artifact: Current artifact with errors
            errors: List of validation errors
            step_0_artifact: Step 0 context
            step_1_artifact: Step 1 context
            step_2_artifact: Step 2 context
            model_config: AI model configuration
            
        Returns:
            Updated artifact
        """
        # Fix each character with errors
        for i, character in enumerate(artifact.get('characters', [])):
            char_errors = [e for e in errors if f"Character {i+1}" in e]
            
            if char_errors:
                # Generate revision prompt for this character
                revision_prompt = self.prompt_generator.generate_revision_prompt(
                    character, char_errors, step_1_artifact, step_2_artifact
                )
                
                # Here we would call AI for revision
                # revised_character = self.call_ai_model(revision_prompt, model_config)
                # artifact['characters'][i] = revised_character
        
        # Add missing required characters
        if any("MISSING PROTAGONIST" in e for e in errors):
            # Generate protagonist
            pass
        
        if any("MISSING ANTAGONIST" in e for e in errors):
            # Generate antagonist with interiority
            pass
        
        return artifact
    
    def enrich_antagonist(self,
                         antagonist: Dict[str, Any],
                         step_1_artifact: Dict[str, Any],
                         step_2_artifact: Dict[str, Any],
                         model_config: Dict[str, Any]):
        """
        Add depth and interiority to antagonist
        
        Args:
            antagonist: Antagonist character dict (modified in place)
            step_1_artifact: Step 1 context
            step_2_artifact: Step 2 context
            model_config: AI model configuration
        """
        prompt_data = self.prompt_generator.generate_antagonist_depth_prompt(
            antagonist, step_1_artifact, step_2_artifact
        )
        
        # Here we would call AI
        # interiority = self.call_ai_model(prompt_data, model_config)
        # antagonist['interiority'] = interiority
    
    def revise(self,
               project_id: str,
               character_index: int,
               validation_errors: List[str],
               model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise specific character based on validation errors
        
        Args:
            project_id: Project UUID
            character_index: Index of character to revise
            validation_errors: List of validation errors to fix
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifacts
        current_artifact = self.load_artifact(project_id, 3)
        step_1_artifact = self.load_artifact(project_id, 1)
        step_2_artifact = self.load_artifact(project_id, 2)
        
        if not all([current_artifact, step_1_artifact, step_2_artifact]):
            return False, {}, "Missing required artifacts"
        
        if character_index >= len(current_artifact.get('characters', [])):
            return False, {}, f"Character index {character_index} out of range"
        
        # Snapshot current version
        self.snapshot_artifact(current_artifact, project_id)
        
        # Get character to revise
        character = current_artifact['characters'][character_index]
        
        # Generate revision prompt
        prompt_data = self.prompt_generator.generate_revision_prompt(
            character, validation_errors, step_1_artifact, step_2_artifact
        )
        
        # Here we would call AI for revision
        # revised_character = self.call_ai_model(prompt_data, model_config)
        # current_artifact['characters'][character_index] = revised_character
        
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
        
        character_name = character.get('name', 'Unknown')
        return True, current_artifact, f"Character '{character_name}' revised and saved to {save_path}"
    
    def add_character(self,
                     project_id: str,
                     role: str,
                     model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Add a new character to existing artifact
        
        Args:
            project_id: Project UUID
            role: Role of character to add
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifacts
        current_artifact = self.load_artifact(project_id, 3)
        step_0_artifact = self.load_artifact(project_id, 0)
        step_1_artifact = self.load_artifact(project_id, 1)
        step_2_artifact = self.load_artifact(project_id, 2)
        
        if not all([current_artifact, step_0_artifact, step_1_artifact, step_2_artifact]):
            return False, {}, "Missing required artifacts"
        
        # Create context for new character
        context = {
            'logline': step_1_artifact.get('logline'),
            'moral_premise': step_2_artifact.get('moral_premise'),
            'category': step_0_artifact.get('category'),
            'existing_characters': [f"{c['role']}: {c['name']}" for c in current_artifact.get('characters', [])]
        }
        
        # Generate prompt for new character
        prompt_data = self.prompt_generator.generate_character_expansion_prompt(role, context)
        
        # Here we would call AI
        # new_character = self.call_ai_model(prompt_data, model_config)
        # current_artifact['characters'].append(new_character)
        
        # Update count and version
        current_artifact['character_count'] = len(current_artifact['characters'])
        old_version = current_artifact['metadata']['version']
        major, minor, patch = map(int, old_version.split('.'))
        current_artifact['metadata']['version'] = f"{major}.{minor + 1}.0"
        
        # Re-validate
        is_valid, errors = self.validator.validate(current_artifact)
        
        if not is_valid:
            return False, current_artifact, f"New character failed validation: {errors}"
        
        # Save updated artifact
        save_path = self.save_artifact(current_artifact, project_id)
        
        return True, current_artifact, f"Added {role} character, saved to {save_path}"
    
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
            "step": 3,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.4),
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
        artifact_path = project_path / "step_3_character_summaries.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        # Save human-readable version
        readable_path = project_path / "step_3_character_summaries.txt"
        with open(readable_path, 'w', encoding='utf-8') as f:
            f.write("STEP 3: CHARACTER SUMMARY SHEETS\n")
            f.write("=" * 60 + "\n\n")
            
            for i, character in enumerate(artifact.get('characters', [])):
                f.write(f"CHARACTER {i+1}: {character.get('name', 'Unknown')} ({character.get('role', 'Unknown')})\n")
                f.write("-" * 40 + "\n")
                f.write(f"Goal: {character.get('goal', 'MISSING')}\n")
                f.write(f"Ambition: {character.get('ambition', 'MISSING')}\n")
                f.write("\nValues:\n")
                for value in character.get('values', []):
                    f.write(f"  • {value}\n")
                f.write(f"\nConflict: {character.get('conflict', 'MISSING')}\n")
                f.write(f"Epiphany: {character.get('epiphany', 'MISSING')}\n")
                if character.get('epiphany', '').upper() == 'NONE':
                    f.write(f"  Justification: {character.get('epiphany_justification', 'MISSING')}\n")
                f.write(f"\nOne-Sentence Arc: {character.get('one_sentence_summary', 'MISSING')}\n")
                f.write(f"\nOne-Paragraph Arc:\n{character.get('one_paragraph_summary', 'MISSING')}\n")
                
                if 'interiority' in character:
                    f.write("\nInteriority:\n")
                    f.write(f"  Motive: {character['interiority'].get('motive_history', 'MISSING')}\n")
                    f.write(f"  Justification: {character['interiority'].get('justification', 'MISSING')}\n")
                    f.write(f"  Vulnerability: {character['interiority'].get('vulnerability', 'MISSING')}\n")
                
                f.write("\n")
            
            if 'protagonist_antagonist_collision' in artifact:
                f.write("PROTAGONIST-ANTAGONIST COLLISION:\n")
                f.write("-" * 40 + "\n")
                collision = artifact['protagonist_antagonist_collision']
                f.write(f"Verified: {'Yes' if collision.get('collision_verified') else 'No'}\n")
                f.write(f"Collision Point: {collision.get('collision_point', 'Unknown')}\n\n")
            
            if 'disaster_alignment' in artifact:
                f.write("DISASTER ALIGNMENT:\n")
                f.write("-" * 40 + "\n")
                alignment = artifact['disaster_alignment']
                f.write(f"D1 Characters: {', '.join(alignment.get('d1_characters', []))}\n")
                f.write(f"D2 Characters: {', '.join(alignment.get('d2_characters', []))}\n")
                f.write(f"D3 Characters: {', '.join(alignment.get('d3_characters', []))}\n\n")
            
            f.write(f"Total Characters: {artifact.get('character_count', 0)}\n")
            f.write(f"Generated: {artifact['metadata']['created_at']}\n")
            f.write(f"Version: {artifact['metadata']['version']}\n")
        
        return artifact_path
    
    def load_artifact(self, project_id: str, step: int) -> Optional[Dict[str, Any]]:
        """Load existing artifact"""
        step_files = {
            0: "step_0_first_things_first.json",
            1: "step_1_one_sentence_summary.json",
            2: "step_2_one_paragraph_summary.json",
            3: "step_3_character_summaries.json"
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
        snapshot_path = project_path / f"step_3_v{version}_{timestamp}.json"
        
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
            char_count = artifact.get('character_count', 0)
            collision = artifact.get('protagonist_antagonist_collision', {}).get('collision_verified', False)
            return True, f"✓ Step 3 characters pass all checks ({char_count} characters, collision verified: {collision})"
        
        suggestions = self.validator.fix_suggestions(errors)
        error_message = "VALIDATION FAILED:\n"
        for error, suggestion in zip(errors, suggestions):
            error_message += f"  ERROR: {error}\n  FIX: {suggestion}\n"
        
        return False, error_message