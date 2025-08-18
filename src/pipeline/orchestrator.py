"""
Snowflake Pipeline Orchestrator
Manages the execution of all 11 Snowflake Method steps
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
from src.pipeline.steps.step_2_one_paragraph_summary import Step2OneParagraphSummary
from src.pipeline.steps.step_3_character_summaries import Step3CharacterSummaries

class SnowflakePipeline:
    """
    Main orchestrator for the Snowflake Method pipeline
    Manages all 11 steps from initial concept to complete manuscript
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize the pipeline
        
        Args:
            project_dir: Directory to store all artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all step executors
        self.step0 = Step0FirstThingsFirst(project_dir)
        self.step1 = Step1OneSentenceSummary(project_dir)
        self.step2 = Step2OneParagraphSummary(project_dir)
        self.step3 = Step3CharacterSummaries(project_dir)
        # Steps 4-10 to be added as implemented
        
        self.current_project_id = None
        self.pipeline_state = {}
    
    def create_project(self, project_name: str) -> str:
        """
        Create a new project
        
        Args:
            project_name: Name for the project
            
        Returns:
            Project ID
        """
        # Generate project ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        project_id = f"{project_name.lower().replace(' ', '_')}_{timestamp}"
        
        # Create project directory
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        # Initialize project metadata
        project_meta = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.utcnow().isoformat(),
            "current_step": 0,
            "steps_completed": [],
            "pipeline_version": "1.0.0"
        }
        
        # Save project metadata
        meta_path = project_path / "project.json"
        with open(meta_path, 'w') as f:
            json.dump(project_meta, f, indent=2)
        
        self.current_project_id = project_id
        return project_id
    
    def load_project(self, project_id: str) -> Dict[str, Any]:
        """
        Load existing project
        
        Args:
            project_id: Project ID to load
            
        Returns:
            Project metadata
        """
        project_path = self.project_dir / project_id / "project.json"
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        
        with open(project_path, 'r') as f:
            project_meta = json.load(f)
        
        self.current_project_id = project_id
        return project_meta
    
    def execute_step_0(self, user_input: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 0: First Things First
        
        Args:
            user_input: User selections for category, tropes, satisfiers
            
        Returns:
            Tuple of (success, artifact, message)
        """
        if not self.current_project_id:
            return False, {}, "No project loaded. Create or load a project first."
        
        success, artifact, message = self.step0.execute(user_input, self.current_project_id)
        
        if success:
            self._update_project_state(0, artifact)
        
        return success, artifact, message
    
    def execute_step_1(self, story_brief: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 1: One Sentence Summary
        
        Args:
            story_brief: User's story concept
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load Step 0 artifact
        step0_artifact = self._load_step_artifact(0)
        if not step0_artifact:
            return False, {}, "Step 0 must be completed first"
        
        success, artifact, message = self.step1.execute(
            step0_artifact, story_brief, self.current_project_id
        )
        
        if success:
            self._update_project_state(1, artifact)
        
        return success, artifact, message
    
    def execute_step_2(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 2: One Paragraph Summary
        
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load required artifacts
        step0_artifact = self._load_step_artifact(0)
        step1_artifact = self._load_step_artifact(1)
        
        if not all([step0_artifact, step1_artifact]):
            return False, {}, "Steps 0 and 1 must be completed first"
        
        success, artifact, message = self.step2.execute(
            step0_artifact, step1_artifact, self.current_project_id
        )
        
        if success:
            self._update_project_state(2, artifact)
        
        return success, artifact, message
    
    def execute_step_3(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 3: Character Summaries
        
        Returns:
            Tuple of (success, artifact, message)
        """
        # Load required artifacts
        step0_artifact = self._load_step_artifact(0)
        step1_artifact = self._load_step_artifact(1)
        step2_artifact = self._load_step_artifact(2)
        
        if not all([step0_artifact, step1_artifact, step2_artifact]):
            return False, {}, "Steps 0, 1, and 2 must be completed first"
        
        success, artifact, message = self.step3.execute(
            step0_artifact, step1_artifact, step2_artifact, self.current_project_id
        )
        
        if success:
            self._update_project_state(3, artifact)
        
        return success, artifact, message
    
    def validate_step(self, step_number: int) -> Tuple[bool, str]:
        """
        Validate a specific step's artifact
        
        Args:
            step_number: Step to validate (0-10)
            
        Returns:
            Tuple of (is_valid, message)
        """
        artifact = self._load_step_artifact(step_number)
        
        if not artifact:
            return False, f"Step {step_number} artifact not found"
        
        # Route to appropriate validator
        validators = {
            0: self.step0.validate_only,
            1: self.step1.validate_only,
            2: self.step2.validate_only,
            3: self.step3.validate_only,
            # Add more as implemented
        }
        
        if step_number not in validators:
            return False, f"Validator for step {step_number} not implemented"
        
        return validators[step_number](artifact)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status
        
        Returns:
            Status dictionary with completion info
        """
        if not self.current_project_id:
            return {"error": "No project loaded"}
        
        project_meta = self.load_project(self.current_project_id)
        
        # Check each step
        step_status = {}
        for step_num in range(11):
            artifact = self._load_step_artifact(step_num)
            if artifact:
                is_valid, message = self.validate_step(step_num)
                step_status[f"step_{step_num}"] = {
                    "completed": True,
                    "valid": is_valid,
                    "message": message,
                    "version": artifact.get('metadata', {}).get('version', 'unknown')
                }
            else:
                step_status[f"step_{step_num}"] = {
                    "completed": False,
                    "valid": False,
                    "message": "Not started"
                }
        
        return {
            "project_id": self.current_project_id,
            "project_name": project_meta.get('project_name'),
            "created_at": project_meta.get('created_at'),
            "current_step": project_meta.get('current_step'),
            "steps": step_status,
            "ready_for_draft": all(
                step_status[f"step_{i}"]["completed"] and step_status[f"step_{i}"]["valid"]
                for i in range(10)
            )
        }
    
    def regenerate_downstream(self, from_step: int) -> List[str]:
        """
        Regenerate all downstream artifacts after a change
        
        Args:
            from_step: Step number that changed
            
        Returns:
            List of regenerated steps
        """
        regenerated = []
        
        # Map of dependencies
        dependencies = {
            1: [0],           # Step 1 depends on Step 0
            2: [0, 1],        # Step 2 depends on Steps 0 and 1
            3: [0, 1, 2],     # Step 3 depends on Steps 0, 1, and 2
            4: [0, 1, 2],     # Step 4 depends on Steps 0, 1, and 2
            5: [3],           # Step 5 depends on Step 3
            6: [2, 4],        # Step 6 depends on Steps 2 and 4
            7: [3, 5],        # Step 7 depends on Steps 3 and 5
            8: [6, 7],        # Step 8 depends on Steps 6 and 7
            9: [8],           # Step 9 depends on Step 8
            10: [8, 9]        # Step 10 depends on Steps 8 and 9
        }
        
        # Find all steps that need regeneration
        for step, deps in dependencies.items():
            if from_step in deps and step > from_step:
                # This step needs regeneration
                # (Implementation would call appropriate execute method)
                regenerated.append(f"step_{step}")
        
        return regenerated
    
    def _load_step_artifact(self, step_number: int) -> Optional[Dict[str, Any]]:
        """Load artifact for specific step"""
        if not self.current_project_id:
            return None
        
        step_files = {
            0: "step_0_first_things_first.json",
            1: "step_1_one_sentence_summary.json",
            2: "step_2_one_paragraph_summary.json",
            3: "step_3_character_summaries.json",
            4: "step_4_one_page_synopsis.json",
            5: "step_5_character_synopses.json",
            6: "step_6_long_synopsis.json",
            7: "step_7_character_bibles.json",
            8: "step_8_scenes.json",
            9: "step_9_scene_briefs.json",
            10: "step_10_manuscript.json"
        }
        
        artifact_path = self.project_dir / self.current_project_id / step_files.get(step_number, "")
        
        if not artifact_path.exists():
            return None
        
        with open(artifact_path, 'r') as f:
            return json.load(f)
    
    def _update_project_state(self, step_number: int, artifact: Dict[str, Any]):
        """Update project state after step completion"""
        if not self.current_project_id:
            return
        
        project_path = self.project_dir / self.current_project_id / "project.json"
        
        with open(project_path, 'r') as f:
            project_meta = json.load(f)
        
        # Update metadata
        project_meta['current_step'] = max(project_meta.get('current_step', 0), step_number)
        
        steps_completed = project_meta.get('steps_completed', [])
        if step_number not in steps_completed:
            steps_completed.append(step_number)
            steps_completed.sort()
        project_meta['steps_completed'] = steps_completed
        
        project_meta['last_updated'] = datetime.utcnow().isoformat()
        
        # Save updated metadata
        with open(project_path, 'w') as f:
            json.dump(project_meta, f, indent=2)
    
    def export_project(self, format: str = "json") -> Path:
        """
        Export complete project bundle
        
        Args:
            format: Export format (json, markdown, etc.)
            
        Returns:
            Path to exported file
        """
        if not self.current_project_id:
            raise RuntimeError("No project loaded")
        
        project_path = self.project_dir / self.current_project_id
        
        if format == "json":
            # Create complete bundle
            bundle = {
                "project": self.load_project(self.current_project_id),
                "artifacts": {}
            }
            
            # Add all artifacts
            for step in range(11):
                artifact = self._load_step_artifact(step)
                if artifact:
                    bundle["artifacts"][f"step_{step}"] = artifact
            
            # Save bundle
            export_path = project_path / f"{self.current_project_id}_complete.json"
            with open(export_path, 'w') as f:
                json.dump(bundle, f, indent=2)
            
            return export_path
        
        # Add other export formats as needed
        raise ValueError(f"Unsupported export format: {format}")