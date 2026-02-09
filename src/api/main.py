"""
Production API Server for Snowflake Novel Generation Engine
FastAPI-based REST API for novel generation
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from src.pipeline.orchestrator import SnowflakePipeline
from src.export.manuscript_exporter import ManuscriptExporter
from src.observability.events import emit_event


# Pydantic models for API
class NovelBrief(BaseModel):
    """Initial brief for novel generation"""
    project_name: str = Field(..., description="Name for the novel project")
    brief: str = Field(..., description="One-line story concept")
    target_words: int = Field(90000, description="Target word count")
    model_provider: Optional[str] = Field(None, description="AI provider (anthropic/openai)")
    

class StepExecutionRequest(BaseModel):
    """Request to execute a specific step"""
    project_id: str
    step_number: int
    additional_params: Optional[Dict[str, Any]] = {}


class ProjectStatus(BaseModel):
    """Project status response"""
    project_id: str
    project_name: str
    current_step: int
    steps_completed: List[int]
    is_complete: bool
    total_word_count: Optional[int]
    created_at: str
    last_updated: Optional[str]


class ExportRequest(BaseModel):
    """Request to export manuscript"""
    project_id: str
    formats: List[str] = Field(["docx", "epub", "markdown"])


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("Starting Snowflake Novel Generation API...")
    app.state.pipeline = SnowflakePipeline()
    app.state.exporter = ManuscriptExporter()
    app.state.active_generations = {}
    
    # Check for API keys
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        print("WARNING: No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
    
    yield
    
    # Shutdown
    print("Shutting down Snowflake Novel Generation API...")
    # Cancel any active generations
    for task_id, task in app.state.active_generations.items():
        task.cancel()


# Create FastAPI app
app = FastAPI(
    title="Snowflake Novel Generation API",
    description="Generate complete novels using the Snowflake Method",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Project management endpoints
@app.post("/projects", response_model=ProjectStatus)
async def create_project(brief: NovelBrief):
    """Create a new novel project"""
    try:
        pipeline = app.state.pipeline
        project_id = pipeline.create_project(brief.project_name)
        
        # Store brief for later use
        project_path = Path("artifacts") / project_id
        brief_path = project_path / "initial_brief.json"
        try:
            with open(brief_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(brief.dict(), f, indent=2)
        except PermissionError:
            raise HTTPException(status_code=500, detail=f"Cannot write brief to {brief_path}. File may be locked by another process.")

        # Get status
        project_meta = pipeline.load_project(project_id)
        
        return ProjectStatus(
            project_id=project_id,
            project_name=brief.project_name,
            current_step=0,
            steps_completed=[],
            is_complete=False,
            total_word_count=None,
            created_at=project_meta['created_at'],
            last_updated=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects")
async def list_projects():
    """List all projects"""
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists():
        return []
    
    projects = []
    for project_dir in artifacts_dir.iterdir():
        if project_dir.is_dir():
            try:
                meta_path = project_dir / "project.json"
                if meta_path.exists():
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        import json
                        meta = json.load(f)
                        projects.append({
                            "project_id": project_dir.name,
                            "project_name": meta.get('project_name', 'Unknown'),
                            "created_at": meta.get('created_at'),
                            "current_step": meta.get('current_step', 0),
                            "steps_completed": meta.get('steps_completed', [])
                        })
            except Exception:
                continue
    
    return sorted(projects, key=lambda x: x['created_at'], reverse=True)


@app.get("/projects/{project_id}", response_model=ProjectStatus)
async def get_project_status(project_id: str):
    """Get status of a specific project"""
    try:
        pipeline = app.state.pipeline
        pipeline.load_project(project_id)
        status = pipeline.get_pipeline_status()
        
        # Check if manuscript exists for word count
        manuscript_path = Path("artifacts") / project_id / "step_10_manuscript.json"
        total_words = None
        if manuscript_path.exists():
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                import json
                manuscript = json.load(f)
                total_words = manuscript.get('total_word_count')
        
        return ProjectStatus(
            project_id=project_id,
            project_name=status.get('project_name', 'Unknown'),
            current_step=status.get('current_step', 0),
            steps_completed=status.get('steps_completed', []),
            is_complete=status.get('ready_for_draft', False) and total_words is not None,
            total_word_count=total_words,
            created_at=status.get('created_at'),
            last_updated=datetime.utcnow().isoformat()
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Step execution endpoints
@app.post("/execute/step/{step_number}")
async def execute_step(
    step_number: int,
    request: StepExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Execute a specific pipeline step"""
    if step_number < 0 or step_number > 10:
        raise HTTPException(status_code=400, detail="Invalid step number (0-10)")
    
    try:
        pipeline = app.state.pipeline
        pipeline.load_project(request.project_id)
        
        # Get initial brief if needed
        brief = None
        if step_number in [0, 1]:
            brief_path = Path("artifacts") / request.project_id / "initial_brief.json"
            if brief_path.exists():
                with open(brief_path, 'r', encoding='utf-8') as f:
                    import json
                    brief_data = json.load(f)
                    brief = brief_data.get('brief', '')
        
        # Execute step based on number
        if step_number == 0:
            success, artifact, message = pipeline.execute_step_0(brief or "A story")
        elif step_number == 1:
            success, artifact, message = pipeline.execute_step_1(brief or "A story")
        elif step_number == 2:
            success, artifact, message = pipeline.execute_step_2()
        elif step_number == 3:
            success, artifact, message = pipeline.execute_step_3()
        elif step_number == 4:
            success, artifact, message = pipeline.execute_step_4()
        elif step_number == 5:
            success, artifact, message = pipeline.execute_step_5()
        elif step_number == 6:
            success, artifact, message = pipeline.execute_step_6()
        elif step_number == 7:
            success, artifact, message = pipeline.execute_step_7()
        elif step_number == 8:
            success, artifact, message = pipeline.execute_step_8()
        elif step_number == 9:
            success, artifact, message = pipeline.execute_step_9()
        elif step_number == 10:
            target_words = request.additional_params.get('target_words', 90000)
            success, artifact, message = pipeline.execute_step_10(target_words)
        
        if not success:
            raise HTTPException(status_code=422, detail=message)
        
        return {
            "success": success,
            "message": message,
            "step": step_number,
            "project_id": request.project_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/full")
async def generate_full_novel(
    brief: NovelBrief,
    background_tasks: BackgroundTasks
):
    """Generate a complete novel from brief to manuscript (async)"""
    try:
        pipeline = app.state.pipeline
        project_id = pipeline.create_project(brief.project_name)
        
        # Start generation in background
        task_id = f"{project_id}_full"
        
        async def generate_novel():
            try:
                # Store brief
                project_path = Path("artifacts") / project_id
                brief_path = project_path / "initial_brief.json"
                try:
                    with open(brief_path, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(brief.dict(), f, indent=2)
                except PermissionError:
                    raise RuntimeError(f"Cannot write brief to {brief_path}. File may be locked by another process.")
                
                # Execute all steps
                steps = [
                    lambda: pipeline.execute_step_0(brief.brief),
                    lambda: pipeline.execute_step_1(brief.brief),
                    pipeline.execute_step_2,
                    pipeline.execute_step_3,
                    pipeline.execute_step_4,
                    pipeline.execute_step_5,
                    pipeline.execute_step_6,
                    pipeline.execute_step_7,
                    pipeline.execute_step_8,
                    pipeline.execute_step_9,
                    lambda: pipeline.execute_step_10(brief.target_words)
                ]
                
                for i, step_func in enumerate(steps):
                    emit_event(project_id, "generation_progress", {
                        "step": i,
                        "total_steps": 11,
                        "status": "executing"
                    })
                    
                    success, _, message = step_func()
                    if not success:
                        emit_event(project_id, "generation_failed", {
                            "step": i,
                            "error": message
                        })
                        return
                
                emit_event(project_id, "generation_complete", {
                    "project_id": project_id,
                    "success": True
                })
                
            except Exception as e:
                emit_event(project_id, "generation_error", {
                    "error": str(e)
                })
        
        # Schedule generation via FastAPI BackgroundTasks (safe on Windows)
        background_tasks.add_task(generate_novel)

        return {
            "project_id": project_id,
            "task_id": task_id,
            "status": "started",
            "message": "Novel generation started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export endpoints
@app.post("/export")
async def export_manuscript(request: ExportRequest):
    """Export manuscript in various formats"""
    try:
        # Load manuscript
        manuscript_path = Path("artifacts") / request.project_id / "step_10_manuscript.json"
        if not manuscript_path.exists():
            raise HTTPException(status_code=404, detail="Manuscript not found. Complete Step 10 first.")
        
        try:
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                import json
                manuscript = json.load(f)
        except PermissionError:
            raise HTTPException(status_code=500, detail=f"Cannot read manuscript at {manuscript_path}. File may be locked by another process.")

        exporter = app.state.exporter
        export_paths = {}
        
        for format in request.formats:
            if format == "docx":
                path = exporter.export_docx(manuscript, project_id=request.project_id)
                export_paths["docx"] = str(path)
            elif format == "epub":
                path = exporter.export_epub(manuscript, project_id=request.project_id)
                export_paths["epub"] = str(path)
            elif format == "markdown":
                path = Path("artifacts") / request.project_id / "manuscript.md"
                if path.exists():
                    export_paths["markdown"] = str(path)
        
        return {
            "project_id": request.project_id,
            "exports": export_paths,
            "message": f"Exported to {len(export_paths)} formats"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{project_id}/{format}")
async def download_manuscript(project_id: str, format: str):
    """Download manuscript in specified format"""
    format_to_file = {
        "docx": "manuscript.docx",
        "epub": "manuscript.epub",
        "markdown": "manuscript.md",
        "json": "step_10_manuscript.json",
        "text": "manuscript.txt"
    }
    
    if format not in format_to_file:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
    
    file_path = Path("artifacts") / project_id / format_to_file[format]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"{format.upper()} file not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{project_id}_{format_to_file[format]}",
        media_type="application/octet-stream"
    )


# Validation endpoints
@app.get("/validate/{project_id}/step/{step_number}")
async def validate_step(project_id: str, step_number: int):
    """Validate a specific step's artifact"""
    try:
        pipeline = app.state.pipeline
        pipeline.load_project(project_id)
        is_valid, message = pipeline.validate_step(step_number)
        
        return {
            "project_id": project_id,
            "step": step_number,
            "is_valid": is_valid,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "src.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )