"""
Project Management Tool for Novel Director Agent

Manages novel projects, tracks progress, and coordinates agent workflows.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime


class ProjectManagementTool(BaseTool):
    """
    Manage novel projects, track progress, and coordinate agent workflows
    """
    
    action: str = Field(
        ..., 
        description="Action to perform: 'create_project', 'get_status', 'update_progress', 'list_projects'"
    )
    project_name: Optional[str] = Field(
        None, 
        description="Name of the novel project (required for create_project)"
    )
    project_id: Optional[str] = Field(
        None, 
        description="Unique project identifier (auto-generated if not provided)"
    )
    step_number: Optional[int] = Field(
        None, 
        description="Snowflake Method step number (0-10)"
    )
    status: Optional[str] = Field(
        None, 
        description="Status update: 'pending', 'in_progress', 'completed', 'needs_revision'"
    )
    notes: Optional[str] = Field(
        None, 
        description="Project notes or updates"
    )

    def run(self) -> str:
        """Execute the project management action"""
        
        if self.action == "create_project":
            return self._create_project()
        elif self.action == "get_status":
            return self._get_project_status()
        elif self.action == "update_progress":
            return self._update_progress()
        elif self.action == "list_projects":
            return self._list_projects()
        else:
            return f"Unknown action: {self.action}"

    def _create_project(self) -> str:
        """Create a new novel project"""
        if not self.project_name:
            return "Error: project_name is required for create_project action"
        
        # Generate project ID if not provided
        if not self.project_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in self.project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            self.project_id = f"{safe_name}_{timestamp}"
        
        # Create project directory
        project_dir = Path("novel_projects") / self.project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize project metadata
        project_data = {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "current_step": 0,
            "steps": {f"step_{i}": {"status": "pending", "artifacts": []} for i in range(11)},
            "agents_assigned": [],
            "quality_gates": {},
            "notes": self.notes or "Project created by Novel Director"
        }
        
        # Save project file
        project_file = project_dir / "project_metadata.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return f"✅ Created novel project: {self.project_name} (ID: {self.project_id})"

    def _get_project_status(self) -> str:
        """Get current status of a project"""
        if not self.project_id:
            return "Error: project_id is required for get_status action"
        
        project_file = Path("novel_projects") / self.project_id / "project_metadata.json"
        
        if not project_file.exists():
            return f"Error: Project {self.project_id} not found"
        
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        # Create status summary
        current_step = project_data.get("current_step", 0)
        total_steps = len(project_data.get("steps", {}))
        completed_steps = sum(1 for step in project_data.get("steps", {}).values() 
                            if step.get("status") == "completed")
        
        status_report = f"""
📚 PROJECT STATUS REPORT
========================
Project: {project_data.get('project_name')}
ID: {project_data.get('project_id')}
Created: {project_data.get('created_at')}
Status: {project_data.get('status')}

PROGRESS:
Current Step: {current_step}/10 (Snowflake Method)
Completed Steps: {completed_steps}/{total_steps}
Progress: {(completed_steps/total_steps)*100:.1f}%

RECENT ACTIVITY:
{project_data.get('notes', 'No recent activity')}

NEXT ACTIONS NEEDED:
{self._get_next_actions(project_data)}
"""
        
        return status_report

    def _update_progress(self) -> str:
        """Update project progress"""
        if not self.project_id:
            return "Error: project_id is required for update_progress action"
        
        project_file = Path("novel_projects") / self.project_id / "project_metadata.json"
        
        if not project_file.exists():
            return f"Error: Project {self.project_id} not found"
        
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        # Update step status if provided
        if self.step_number is not None and self.status:
            step_key = f"step_{self.step_number}"
            if step_key in project_data["steps"]:
                project_data["steps"][step_key]["status"] = self.status
                project_data["steps"][step_key]["updated_at"] = datetime.now().isoformat()
                
                # Update current step if this step is completed
                if self.status == "completed" and self.step_number >= project_data["current_step"]:
                    project_data["current_step"] = self.step_number + 1
        
        # Add notes if provided
        if self.notes:
            project_data["notes"] = self.notes
            project_data["last_updated"] = datetime.now().isoformat()
        
        # Save updated project
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return f"✅ Updated project {self.project_id}: Step {self.step_number} → {self.status}"

    def _list_projects(self) -> str:
        """List all novel projects"""
        projects_dir = Path("novel_projects")
        
        if not projects_dir.exists():
            return "No novel projects found. Create your first project to get started!"
        
        projects = []
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "project_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        project_data = json.load(f)
                        projects.append(project_data)
        
        if not projects:
            return "No novel projects found."
        
        # Sort by creation date
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        project_list = "📚 NOVEL PROJECTS\n================\n"
        
        for project in projects:
            current_step = project.get("current_step", 0)
            total_steps = 11
            progress = (current_step / total_steps) * 100
            
            project_list += f"""
🎭 {project.get('project_name')}
   ID: {project.get('project_id')}
   Progress: {progress:.0f}% (Step {current_step}/10)
   Status: {project.get('status')}
   Created: {project.get('created_at', '')[:10]}
"""
        
        return project_list

    def _get_next_actions(self, project_data: Dict[str, Any]) -> str:
        """Determine next actions needed for the project"""
        current_step = project_data.get("current_step", 0)
        
        step_names = {
            0: "First Things First (Story Concept)",
            1: "One Sentence Summary (Logline)", 
            2: "One Paragraph Summary (Structure)",
            3: "Character Summaries",
            4: "One Page Synopsis",
            5: "Character Synopses", 
            6: "Long Synopsis",
            7: "Character Bibles",
            8: "Scene List",
            9: "Scene Briefs",
            10: "First Draft"
        }
        
        if current_step <= 10:
            next_step_name = step_names.get(current_step, f"Step {current_step}")
            return f"Ready to begin: {next_step_name}"
        else:
            return "Novel complete! Ready for final review and publishing."