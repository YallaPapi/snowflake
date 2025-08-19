"""
Progress Tracking and Resumption for Snowflake Pipeline
Allows pipeline to save state and resume from failures
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class ProgressTracker:
    """
    Track pipeline progress and enable resumption
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize progress tracker
        
        Args:
            project_dir: Directory to store progress files
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, 
                       project_id: str,
                       step: int,
                       status: str,
                       artifact: Optional[Dict[str, Any]] = None,
                       error: Optional[str] = None) -> Path:
        """
        Save a checkpoint for the current step
        
        Args:
            project_id: Project identifier
            step: Current step number (0-10)
            status: Status of step ('started', 'completed', 'failed')
            artifact: Optional artifact data
            error: Optional error message
            
        Returns:
            Path to checkpoint file
        """
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        checkpoint_file = project_path / "checkpoint.json"
        
        # Load existing checkpoint if exists
        if checkpoint_file.exists():
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
        else:
            checkpoint = {
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "steps": {}
            }
        
        # Update checkpoint
        checkpoint["last_updated"] = datetime.utcnow().isoformat()
        checkpoint["current_step"] = step
        checkpoint["steps"][f"step_{step}"] = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "artifact_saved": artifact is not None,
            "error": error
        }
        
        # Save checkpoint
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)
        
        return checkpoint_file
    
    def load_checkpoint(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint for a project
        
        Args:
            project_id: Project identifier
            
        Returns:
            Checkpoint data or None if not found
        """
        checkpoint_file = self.project_dir / project_id / "checkpoint.json"
        
        if not checkpoint_file.exists():
            return None
        
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_resume_point(self, project_id: str) -> Optional[int]:
        """
        Get the step number to resume from
        
        Args:
            project_id: Project identifier
            
        Returns:
            Step number to resume from, or None if no checkpoint
        """
        checkpoint = self.load_checkpoint(project_id)
        
        if not checkpoint:
            return None
        
        # Find last completed step
        last_completed = -1
        for step_key, step_data in checkpoint.get("steps", {}).items():
            if step_data["status"] == "completed":
                step_num = int(step_key.split("_")[1])
                last_completed = max(last_completed, step_num)
        
        # Resume from next step after last completed
        if last_completed >= 0:
            return last_completed + 1
        
        return 0
    
    def get_completed_steps(self, project_id: str) -> List[int]:
        """
        Get list of completed steps
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of completed step numbers
        """
        checkpoint = self.load_checkpoint(project_id)
        
        if not checkpoint:
            return []
        
        completed = []
        for step_key, step_data in checkpoint.get("steps", {}).items():
            if step_data["status"] == "completed":
                step_num = int(step_key.split("_")[1])
                completed.append(step_num)
        
        return sorted(completed)
    
    def create_progress_report(self, project_id: str) -> str:
        """
        Create a human-readable progress report
        
        Args:
            project_id: Project identifier
            
        Returns:
            Progress report string
        """
        checkpoint = self.load_checkpoint(project_id)
        
        if not checkpoint:
            return f"No progress found for project {project_id}"
        
        report = []
        report.append(f"Progress Report for {project_id}")
        report.append("=" * 50)
        report.append(f"Created: {checkpoint.get('created_at', 'Unknown')}")
        report.append(f"Last Updated: {checkpoint.get('last_updated', 'Unknown')}")
        report.append(f"Current Step: {checkpoint.get('current_step', 'Unknown')}")
        report.append("")
        report.append("Step Status:")
        
        for i in range(11):
            step_key = f"step_{i}"
            if step_key in checkpoint.get("steps", {}):
                step_data = checkpoint["steps"][step_key]
                status = step_data["status"]
                timestamp = step_data.get("timestamp", "")
                
                if status == "completed":
                    status_icon = "✓"
                elif status == "failed":
                    status_icon = "✗"
                else:
                    status_icon = "→"
                
                report.append(f"  {status_icon} Step {i}: {status}")
                
                if step_data.get("error"):
                    report.append(f"      Error: {step_data['error'][:100]}")
            else:
                report.append(f"  - Step {i}: Not started")
        
        completed = self.get_completed_steps(project_id)
        completion_pct = (len(completed) / 11) * 100
        
        report.append("")
        report.append(f"Completion: {len(completed)}/11 steps ({completion_pct:.0f}%)")
        
        resume_point = self.get_resume_point(project_id)
        if resume_point is not None and resume_point < 11:
            report.append(f"Resume from: Step {resume_point}")
        
        return "\n".join(report)
    
    def estimate_time_remaining(self, 
                               project_id: str,
                               avg_step_time: float = 30.0) -> float:
        """
        Estimate time remaining based on completed steps
        
        Args:
            project_id: Project identifier
            avg_step_time: Average time per step in seconds
            
        Returns:
            Estimated seconds remaining
        """
        completed = self.get_completed_steps(project_id)
        remaining_steps = 11 - len(completed)
        
        # Steps 9 and 10 typically take longer
        time_estimate = 0
        for step in range(11):
            if step not in completed:
                if step == 9:
                    time_estimate += avg_step_time * 2  # Step 9 takes longer
                elif step == 10:
                    time_estimate += avg_step_time * 3  # Step 10 takes much longer
                else:
                    time_estimate += avg_step_time
        
        return time_estimate