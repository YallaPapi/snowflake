"""
Quality Gate Approval Tool for Novel Director Agent

Manages quality gates and approvals throughout the novel creation process.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime


class QualityGateApprovalTool(BaseTool):
    """
    Manage quality gates and approvals for novel creation steps
    """
    
    project_id: str = Field(..., description="Unique project identifier")
    step_number: int = Field(..., description="Snowflake Method step number (0-10)")
    action: str = Field(
        ..., 
        description="Action: 'review', 'approve', 'reject', 'request_revision'"
    )
    quality_score: Optional[float] = Field(
        None, 
        description="Quality score from 0.0 to 1.0 (required for review action)"
    )
    feedback: Optional[str] = Field(
        None, 
        description="Detailed feedback on the work"
    )
    revision_notes: Optional[str] = Field(
        None, 
        description="Specific revision requests (required for request_revision)"
    )
    criteria_met: Optional[List[str]] = Field(
        None, 
        description="List of quality criteria that were met"
    )
    criteria_failed: Optional[List[str]] = Field(
        None, 
        description="List of quality criteria that failed"
    )

    def run(self) -> str:
        """Execute quality gate action"""
        
        if self.action == "review":
            return self._review_step()
        elif self.action == "approve":
            return self._approve_step()
        elif self.action == "reject":
            return self._reject_step()
        elif self.action == "request_revision":
            return self._request_revision()
        else:
            return f"Unknown action: {self.action}"

    def _review_step(self) -> str:
        """Review a step's quality"""
        if self.quality_score is None:
            return "Error: quality_score is required for review action"
        
        # Load project data
        project_data = self._load_project_data()
        if isinstance(project_data, str):  # Error message
            return project_data
        
        step_key = f"step_{self.step_number}"
        
        # Create quality review
        quality_review = {
            "reviewed_at": datetime.now().isoformat(),
            "reviewer": "NovelDirector",
            "quality_score": self.quality_score,
            "feedback": self.feedback or "",
            "criteria_met": self.criteria_met or [],
            "criteria_failed": self.criteria_failed or [],
            "recommendation": self._get_recommendation(self.quality_score)
        }
        
        # Update project data
        if "quality_gates" not in project_data:
            project_data["quality_gates"] = {}
        
        project_data["quality_gates"][step_key] = quality_review
        
        # Save updated project
        self._save_project_data(project_data)
        
        recommendation = quality_review["recommendation"]
        score_pct = self.quality_score * 100
        
        return f"""
🔍 QUALITY REVIEW COMPLETED
===========================
Step {self.step_number}: {self._get_step_name(self.step_number)}
Quality Score: {score_pct:.1f}%
Recommendation: {recommendation}

Criteria Met: {len(self.criteria_met or [])}
Criteria Failed: {len(self.criteria_failed or [])}

Feedback:
{self.feedback or 'No additional feedback provided'}

Next Action: {self._get_next_action(recommendation)}
"""

    def _approve_step(self) -> str:
        """Approve a step"""
        project_data = self._load_project_data()
        if isinstance(project_data, str):
            return project_data
        
        step_key = f"step_{self.step_number}"
        
        # Update step status
        if "steps" in project_data and step_key in project_data["steps"]:
            project_data["steps"][step_key]["status"] = "approved"
            project_data["steps"][step_key]["approved_at"] = datetime.now().isoformat()
            project_data["steps"][step_key]["approved_by"] = "NovelDirector"
        
        # Update quality gate
        if "quality_gates" not in project_data:
            project_data["quality_gates"] = {}
        
        if step_key not in project_data["quality_gates"]:
            project_data["quality_gates"][step_key] = {}
        
        project_data["quality_gates"][step_key].update({
            "approved_at": datetime.now().isoformat(),
            "approved_by": "NovelDirector",
            "status": "approved",
            "approval_notes": self.feedback or "Meets quality standards"
        })
        
        # Advance to next step if this is the current step
        if project_data.get("current_step", 0) == self.step_number:
            project_data["current_step"] = self.step_number + 1
        
        self._save_project_data(project_data)
        
        return f"✅ APPROVED: Step {self.step_number} ({self._get_step_name(self.step_number)}) approved and project advanced to next step."

    def _reject_step(self) -> str:
        """Reject a step"""
        project_data = self._load_project_data()
        if isinstance(project_data, str):
            return project_data
        
        step_key = f"step_{self.step_number}"
        
        # Update step status
        if "steps" in project_data and step_key in project_data["steps"]:
            project_data["steps"][step_key]["status"] = "rejected"
            project_data["steps"][step_key]["rejected_at"] = datetime.now().isoformat()
            project_data["steps"][step_key]["rejected_by"] = "NovelDirector"
        
        # Update quality gate
        if "quality_gates" not in project_data:
            project_data["quality_gates"] = {}
        
        if step_key not in project_data["quality_gates"]:
            project_data["quality_gates"][step_key] = {}
        
        project_data["quality_gates"][step_key].update({
            "rejected_at": datetime.now().isoformat(),
            "rejected_by": "NovelDirector", 
            "status": "rejected",
            "rejection_reason": self.feedback or "Does not meet quality standards"
        })
        
        self._save_project_data(project_data)
        
        return f"❌ REJECTED: Step {self.step_number} ({self._get_step_name(self.step_number)}) rejected. Requires rework before proceeding."

    def _request_revision(self) -> str:
        """Request specific revisions"""
        if not self.revision_notes:
            return "Error: revision_notes are required for request_revision action"
        
        project_data = self._load_project_data()
        if isinstance(project_data, str):
            return project_data
        
        step_key = f"step_{self.step_number}"
        
        # Update step status
        if "steps" in project_data and step_key in project_data["steps"]:
            project_data["steps"][step_key]["status"] = "needs_revision"
            project_data["steps"][step_key]["revision_requested_at"] = datetime.now().isoformat()
            project_data["steps"][step_key]["revision_requested_by"] = "NovelDirector"
        
        # Add revision request to quality gate
        if "quality_gates" not in project_data:
            project_data["quality_gates"] = {}
        
        if step_key not in project_data["quality_gates"]:
            project_data["quality_gates"][step_key] = {}
        
        if "revision_requests" not in project_data["quality_gates"][step_key]:
            project_data["quality_gates"][step_key]["revision_requests"] = []
        
        revision_request = {
            "requested_at": datetime.now().isoformat(),
            "requested_by": "NovelDirector",
            "revision_notes": self.revision_notes,
            "feedback": self.feedback or "",
            "status": "pending"
        }
        
        project_data["quality_gates"][step_key]["revision_requests"].append(revision_request)
        
        self._save_project_data(project_data)
        
        return f"""
🔧 REVISION REQUESTED
====================
Step {self.step_number}: {self._get_step_name(self.step_number)}

Revision Notes:
{self.revision_notes}

Additional Feedback:
{self.feedback or 'No additional feedback'}

Status: Pending agent revision
"""

    def _load_project_data(self) -> Dict[str, Any] or str:
        """Load project data or return error message"""
        project_file = Path("novel_projects") / self.project_id / "project_metadata.json"
        
        if not project_file.exists():
            return f"Error: Project {self.project_id} not found"
        
        try:
            with open(project_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return f"Error loading project data: {str(e)}"

    def _save_project_data(self, project_data: Dict[str, Any]) -> None:
        """Save project data"""
        project_file = Path("novel_projects") / self.project_id / "project_metadata.json"
        
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)

    def _get_recommendation(self, quality_score: float) -> str:
        """Get recommendation based on quality score"""
        if quality_score >= 0.9:
            return "EXCELLENT - Approve immediately"
        elif quality_score >= 0.8:
            return "GOOD - Approve with minor notes"
        elif quality_score >= 0.7:
            return "ACCEPTABLE - Request minor revisions"
        elif quality_score >= 0.6:
            return "NEEDS WORK - Request significant revisions"
        else:
            return "POOR - Reject and restart"

    def _get_next_action(self, recommendation: str) -> str:
        """Get next action based on recommendation"""
        if "Approve immediately" in recommendation:
            return "Ready for approval"
        elif "Approve with" in recommendation:
            return "Approve with feedback notes"
        elif "minor revisions" in recommendation:
            return "Request specific minor revisions"
        elif "significant revisions" in recommendation:
            return "Request major revisions with detailed feedback"
        else:
            return "Reject and request complete rework"

    def _get_step_name(self, step_number: int) -> str:
        """Get human-readable step name"""
        step_names = {
            0: "First Things First",
            1: "One Sentence Summary",
            2: "One Paragraph Summary",
            3: "Character Summaries",
            4: "One Page Synopsis",
            5: "Character Synopses",
            6: "Long Synopsis", 
            7: "Character Bibles",
            8: "Scene List",
            9: "Scene Briefs",
            10: "First Draft"
        }
        
        return step_names.get(step_number, f"Step {step_number}")