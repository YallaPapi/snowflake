"""
Step 10 Implementation: First Draft
Generate the complete manuscript from scene briefs
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_10_validator import Step10Validator
from src.ai.generator import AIGenerator
from src.ai.model_selector import ModelSelector
from src.ai.prose_generator import ProseGenerator
from src.ai.bulletproof_generator import get_bulletproof_generator
from src.ai.bulletproof_prose_generator import get_bulletproof_prose_generator

class Step10FirstDraft:
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step10Validator()
        self.generator = AIGenerator()
        self.bulletproof_generator = get_bulletproof_generator()
        self.prose_generator = ProseGenerator(self.generator)
        self.bulletproof_prose_generator = get_bulletproof_prose_generator()
    
    def execute(self,
                step9_artifact: Dict[str, Any],
                step7_artifact: Dict[str, Any],
                step8_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 10: Generate first draft
        
        Args:
            step9_artifact: Scene briefs
            step7_artifact: Character bibles
            step8_artifact: Scene list with details
            project_id: Project identifier
            model_config: Model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        if not model_config:
            model_config = {"temperature": 0.7, "max_tokens": 4000}
        
        # Calculate upstream hash
        upstream_data = {
            "step9": step9_artifact,
            "step7": step7_artifact,
            "step8": step8_artifact
        }
        upstream_hash = hashlib.sha256(
            json.dumps(upstream_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Get scenes and briefs
        scenes = step8_artifact.get("scenes", [])
        briefs = step9_artifact.get("scene_briefs", [])
        character_bibles = step7_artifact.get("bibles", [])
        
        # Generate prose for each scene
        chapters = []
        current_chapter = {
            "number": 1,
            "title": "Chapter 1",
            "scenes": []
        }
        
        print(f"Generating prose for {len(scenes)} scenes...")
        
        # Import progress tracker
        try:
            from src.ui.progress_tracker import get_global_tracker
            tracker = get_global_tracker()
        except ImportError:
            tracker = None
        
        for i, (scene, brief) in enumerate(zip(scenes, briefs)):
            scene_num = i + 1
            
            # Check for chapter break
            chapter_hint = scene.get("chapter_hint", "")
            if chapter_hint and i > 0:
                # Check if this starts a new chapter
                if f"Ch{len(chapters)+1}" in chapter_hint:
                    chapters.append(current_chapter)
                    current_chapter = {
                        "number": len(chapters) + 1,
                        "title": f"Chapter {len(chapters) + 1}",
                        "scenes": []
                    }
            
            # Get POV character bible
            pov_name = scene.get("pov", "Unknown")
            pov_bible = self._get_character_bible(pov_name, character_bibles)
            
            # Generate scene prose with guaranteed length
            word_target = scene.get("word_target", 2500)
            scene_summary = scene.get("summary", "Scene description")[:40]
            
            # Update progress
            if tracker:
                tracker.update_step_progress(i, len(scenes), f"Ch{len(chapters)+1} Scene {scene_num}: {scene_summary}... ({word_target}w)")
            else:
                print(f"  Generating scene {scene_num}/{len(scenes)} ({pov_name} POV, target: {word_target} words)...")
            
            # Combine scene and brief data
            scene_context = {**scene, **brief}
            
            # Use bulletproof prose generator - NEVER fails
            prose = self.bulletproof_prose_generator.generate_guaranteed_scene(
                scene_context,
                pov_bible,
                word_target,
                min_words=max(word_target // 2, 500)  # At least 500 words minimum
            )
            
            actual_words = len(prose.split())
            if not tracker:
                print(f"    Generated {actual_words} words")
            
            scene_data = {
                "scene_number": scene_num,
                "pov": pov_name,
                "type": brief.get("type", "Unknown"),
                "summary": scene.get("summary", ""),
                "prose": prose,
                "word_count": len(prose.split())
            }
            
            current_chapter["scenes"].append(scene_data)
        
        # Add final chapter
        if current_chapter["scenes"]:
            chapters.append(current_chapter)
        
        # Final progress update
        if tracker:
            total_words = sum(scene["word_count"] for ch in chapters for scene in ch["scenes"])
            tracker.update_step_progress(len(scenes), len(scenes), f"Complete! {len(chapters)} chapters, {total_words:,} words")
        
        # Create manuscript artifact
        artifact = {
            "manuscript": {
                "chapters": chapters,
                "total_chapters": len(chapters),
                "total_scenes": sum(len(ch["scenes"]) for ch in chapters),
                "total_word_count": sum(
                    scene["word_count"] 
                    for ch in chapters 
                    for scene in ch["scenes"]
                )
            }
        }
        
        # Validate
        ok, errs = self.validator.validate(artifact)
        if not ok:
            fixes = self.validator.fix_suggestions(errs)
            return False, artifact, "VALIDATION FAILED:\n" + "\n".join(
                f"ERROR: {e} | FIX: {f}" for e, f in zip(errs, fixes)
            )
        
        # Add metadata
        artifact = self.add_metadata(
            artifact, project_id, "step10_v1", model_config, upstream_hash
        )
        
        # Save artifact
        path = self.save_artifact(artifact, project_id)
        
        # Also save as markdown
        self._save_as_markdown(artifact, project_id)
        
        return True, artifact, f"Step 10 manuscript saved to {path}"
    
    def _get_character_bible(self, 
                            character_name: str, 
                            bibles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get character bible by name"""
        for bible in bibles:
            if bible.get("name") == character_name:
                return bible
        
        # Return default if not found
        return {
            "name": character_name,
            "voice_notes": ["Natural voice"],
            "personality": {"traits": ["determined"]}
        }
    
    def _save_as_markdown(self, artifact: Dict[str, Any], project_id: str):
        """Save manuscript as markdown file"""
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        md_path = project_path / "manuscript.md"
        
        with open(md_path, "w", encoding="utf-8") as f:
            manuscript = artifact.get("manuscript", {})
            
            f.write(f"# Manuscript\n\n")
            f.write(f"Total Word Count: {manuscript.get('total_word_count', 0):,}\n\n")
            f.write("---\n\n")
            
            for chapter in manuscript.get("chapters", []):
                f.write(f"## Chapter {chapter['number']}\n\n")
                
                for scene in chapter.get("scenes", []):
                    f.write(f"### Scene {scene['scene_number']}\n\n")
                    f.write(f"*POV: {scene['pov']} | Type: {scene['type']}*\n\n")
                    f.write(scene.get("prose", ""))
                    f.write("\n\n---\n\n")
    
    def add_metadata(self, 
                    content: Dict[str, Any], 
                    project_id: str, 
                    prompt_hash: str,
                    model_config: Dict[str, Any], 
                    upstream_hash: str) -> Dict[str, Any]:
        """Add metadata to artifact"""
        artifact = content.copy()
        
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 10,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", 
                self.generator.default_model if hasattr(self.generator, "default_model") else "unknown"),
            "temperature": model_config.get("temperature", 0.7),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        
        return artifact
    
    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk"""
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        path = project_path / "step_10_manuscript.json"
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        return path
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate artifact without generation"""
        ok, errs = self.validator.validate(artifact)
        
        if ok:
            return True, "✓ Step 10 manuscript passes validation"
        
        fixes = self.validator.fix_suggestions(errs)
        return False, "VALIDATION FAILED:\n" + "\n".join(
            f"ERROR: {e} | FIX: {f}" for e, f in zip(errs, fixes)
        )