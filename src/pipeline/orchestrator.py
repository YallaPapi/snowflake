"""
Snowflake Pipeline Orchestrator
Manages the execution of all 11 Snowflake Method steps
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
from src.pipeline.steps.step_2_one_paragraph_summary import Step2OneParagraphSummary
from src.pipeline.steps.step_3_character_summaries import Step3CharacterSummaries
from src.pipeline.steps.step_4_one_page_synopsis import Step4OnePageSynopsis
from src.pipeline.steps.step_5_character_synopses import Step5CharacterSynopses
from src.pipeline.steps.step_6_long_synopsis import Step6LongSynopsis
from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles
from src.pipeline.steps.step_8_scene_list import Step8SceneList
from src.pipeline.steps.step_9_scene_briefs_v2 import Step9SceneBriefsV2 as Step9SceneBriefs
from src.pipeline.steps.step_10_first_draft import Step10FirstDraft
from src.observability.events import emit_event
from src.pipeline.progress_tracker import ProgressTracker

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
        self.step4 = Step4OnePageSynopsis(project_dir)
        self.step5 = Step5CharacterSynopses(project_dir)
        self.step6 = Step6LongSynopsis(project_dir)
        self.step7 = Step7CharacterBibles(project_dir)
        self.step8 = Step8SceneList(project_dir)
        self.step9 = Step9SceneBriefs(project_dir)
        self.step10 = Step10FirstDraft(project_dir)
        
        # Progress tracking
        self.progress_tracker = ProgressTracker(project_dir)
        
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
        emit_event(project_id, "project_created", {"project_name": project_name, "current_step": 0})
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
        emit_event(project_id, "project_loaded", {"project_name": project_meta.get('project_name'), "current_step": project_meta.get('current_step')})
        return project_meta
    
    def execute_step_0(self, brief: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 0: First Things First
        
        Args:
            brief: The user's story idea/brief
            
        Returns:
            Tuple of (success, artifact, message)
        """
        if not self.current_project_id:
            return False, {}, "No project loaded. Create or load a project first."
        
        emit_event(self.current_project_id, "step_start", {"step": 0, "step_key": "step_0"})
        success, artifact, message = self.step0.execute(brief, self.current_project_id)
        
        if success:
            self._update_project_state(0, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 0, "step_key": "step_0", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 0, "step_key": "step_0", "message": message})
        
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
        
        emit_event(self.current_project_id, "step_start", {"step": 1, "step_key": "step_1"})
        success, artifact, message = self.step1.execute(
            step0_artifact, story_brief, self.current_project_id
        )
        
        if success:
            self._update_project_state(1, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 1, "step_key": "step_1", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 1, "step_key": "step_1", "message": message})
        
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
        
        emit_event(self.current_project_id, "step_start", {"step": 2, "step_key": "step_2"})
        success, artifact, message = self.step2.execute(
            step0_artifact, step1_artifact, self.current_project_id
        )
        
        if success:
            self._update_project_state(2, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 2, "step_key": "step_2", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 2, "step_key": "step_2", "message": message})
        
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
        
        emit_event(self.current_project_id, "step_start", {"step": 3, "step_key": "step_3"})
        success, artifact, message = self.step3.execute(
            step0_artifact, step1_artifact, step2_artifact, self.current_project_id
        )
        
        if success:
            self._update_project_state(3, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 3, "step_key": "step_3", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 3, "step_key": "step_3", "message": message})
        
        return success, artifact, message
    
    def execute_step_4(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 4: One-Page Synopsis
        """
        step2_artifact = self._load_step_artifact(2)
        if not step2_artifact:
            return False, {}, "Steps 0-3 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 4, "step_key": "step_4"})
        success, artifact, message = self.step4.execute(
            step2_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(4, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 4, "step_key": "step_4", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 4, "step_key": "step_4", "message": message})
        return success, artifact, message
    
    def execute_step_5(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 5: Character Synopses
        """
        step3_artifact = self._load_step_artifact(3)
        if not step3_artifact:
            return False, {}, "Steps 0-4 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 5, "step_key": "step_5"})
        success, artifact, message = self.step5.execute(
            step3_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(5, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 5, "step_key": "step_5", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 5, "step_key": "step_5", "message": message})
        return success, artifact, message

    def execute_step_6(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 6: Long Synopsis
        """
        step4_artifact = self._load_step_artifact(4)
        if not step4_artifact:
            return False, {}, "Steps 0-5 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 6, "step_key": "step_6"})
        success, artifact, message = self.step6.execute(
            step4_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(6, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 6, "step_key": "step_6", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 6, "step_key": "step_6", "message": message})
        return success, artifact, message

    def execute_step_7(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 7: Character Bibles
        """
        step5_artifact = self._load_step_artifact(5)
        if not step5_artifact:
            return False, {}, "Steps 0-6 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 7, "step_key": "step_7"})
        success, artifact, message = self.step7.execute(
            step5_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(7, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 7, "step_key": "step_7", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 7, "step_key": "step_7", "message": message})
        return success, artifact, message

    def execute_step_8(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 8: Scene List
        """
        step6_artifact = self._load_step_artifact(6)
        step7_artifact = self._load_step_artifact(7)
        if not all([step6_artifact, step7_artifact]):
            return False, {}, "Steps 0-7 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 8, "step_key": "step_8"})
        success, artifact, message = self.step8.execute(
            step6_artifact, step7_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(8, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 8, "step_key": "step_8", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 8, "step_key": "step_8", "message": message})
        return success, artifact, message

    def execute_step_9(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 9: Scene Briefs
        """
        step8_artifact = self._load_step_artifact(8)
        if not step8_artifact:
            return False, {}, "Steps 0-8 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 9, "step_key": "step_9"})
        success, artifact, message = self.step9.execute(
            step8_artifact, self.current_project_id
        )
        if success:
            self._update_project_state(9, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 9, "step_key": "step_9", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 9, "step_key": "step_9", "message": message})
        return success, artifact, message

    def execute_step_10(self, target_words: int = 90000) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 10: Draft Writer
        """
        step7_artifact = self._load_step_artifact(7)
        step8_artifact = self._load_step_artifact(8)
        step9_artifact = self._load_step_artifact(9)
        if not all([step7_artifact, step8_artifact, step9_artifact]):
            return False, {}, "Steps 7, 8, and 9 must be completed first"
        emit_event(self.current_project_id, "step_start", {"step": 10, "step_key": "step_10"})
        success, artifact, message = self.step10.execute(
            step9_artifact,
            step7_artifact,
            step8_artifact,
            self.current_project_id
        )
        if success:
            self._update_project_state(10, artifact)
            emit_event(self.current_project_id, "step_complete", {"step": 10, "step_key": "step_10", "valid": True})
        else:
            emit_event(self.current_project_id, "step_failed", {"step": 10, "step_key": "step_10", "message": message})
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
            4: self.step4.validate_only,
            5: self.step5.validate_only,
            6: self.step6.validate_only,
            7: self.step7.validate_only,
            8: self.step8.validate_only,
            9: self.step9.validate_only,
            # Step 10 has no validator; skip
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
            8: "step_8_scene_list.json",
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
        emit_event(self.current_project_id, "state_updated", {"current_step": project_meta['current_step'], "step_key": f"step_{step_number}"})
        
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

if __name__ == "__main__":
    pipeline = SnowflakePipeline()
    project_name = "MyNewNovel"
    project_id = pipeline.create_project(project_name)
    print(f"Created project: {project_id}")
    
    project_meta = pipeline.load_project(project_id)
    print(f"Current step for {project_meta['project_name']}: {project_meta['current_step']}")