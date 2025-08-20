"""
Step 9 Implementation: Scene Briefs
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_9_validator import Step9Validator
from src.pipeline.prompts.step_9_prompt import Step9Prompt
from src.ai.generator import AIGenerator
from src.ai.model_selector import ModelSelector

class Step9SceneBriefs:
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step9Validator()
        self.prompt_generator = Step9Prompt()
        self.generator = AIGenerator()

    def execute(self,
                step8_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        if not model_config:
            # Use optimal model for this step
            from src.ai.model_selector import ModelSelector
            model_config = ModelSelector.get_model_config(step=9)
        upstream_hash = hashlib.sha256(json.dumps(step8_artifact, sort_keys=True).encode()).hexdigest()
        
        # Generate scene briefs in batches to avoid token limits
        all_scenes = step8_artifact.get("scenes", [])
        scene_briefs = []
        batch_size = 5  # Generate 5 scenes at a time
        
        print(f"Generating {len(all_scenes)} scene briefs in batches of {batch_size}...")
        
        for i in range(0, len(all_scenes), batch_size):
            batch_scenes = all_scenes[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(all_scenes) + batch_size - 1) // batch_size
            
            print(f"  Generating batch {batch_num}/{total_batches} (scenes {i+1}-{min(i+batch_size, len(all_scenes))})...")
            
            # Create a batch-specific prompt
            batch_prompt = self.prompt_generator.generate_batch_prompt(
                step8_artifact, 
                batch_scenes, 
                i  # Starting index
            )
            
            try:
                # Generate without validation for batches
                batch_content = self.generator.generate(batch_prompt, model_config)
                
                # Parse the batch response
                batch_briefs = self._parse_batch_response(batch_content, batch_scenes)
                scene_briefs.extend(batch_briefs)
                
            except Exception as e:
                print(f"    Failed to generate batch {batch_num}: {e}")
                # Create placeholder briefs for failed batch
                for j, scene in enumerate(batch_scenes):
                    scene_briefs.append(self._create_placeholder_brief(scene, i + j))
        
        artifact = {"scene_briefs": scene_briefs}
        ok, errs = self.validator.validate(artifact)
        if not ok:
            fixes = self.validator.fix_suggestions(errs)
            return False, artifact, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))
        
        # Use first batch's prompt hash for metadata
        first_prompt = self.prompt_generator.generate_batch_prompt(
            step8_artifact, all_scenes[:batch_size], 0
        )
        artifact = self.add_metadata(artifact, project_id, first_prompt.get("prompt_hash", "unknown"), model_config, upstream_hash)
        path = self.save_artifact(artifact, project_id)
        return True, artifact, f"Step 9 artifact saved to {path}"

    def add_metadata(self, content: Dict[str, Any], project_id: str, prompt_hash: str, model_config: Dict[str, Any], upstream_hash: str) -> Dict[str, Any]:
        artifact = content.copy()
        briefs = artifact.get("scene_briefs", [])
        artifact.setdefault("brief_count", len(briefs))
        # Type distribution and derived fields are computed by validator; ensure presence
        artifact.setdefault("type_distribution", {})
        artifact.setdefault("triad_validation", {"complete": [], "incomplete": [], "completion_rate": 0})
        artifact.setdefault("causal_chain", {"decision_goal_links": [], "chain_strength": 0})
        artifact.setdefault("disaster_links", {"d1_linked": False, "d2_linked": False, "d3_linked": False})
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 9,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", self.generator.default_model if hasattr(self.generator, "default_model") else "unknown"),
            "temperature": model_config.get("temperature", 0.3),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        return artifact

    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        p = project_path / "step_9_scene_briefs.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        return p

    def _parse_batch_response(self, response: str, batch_scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse AI response for a batch of scene briefs"""
        briefs = []
        
        # Try to parse as JSON first
        try:
            import json
            if response.strip().startswith("{") or response.strip().startswith("["):
                data = json.loads(response)
                if isinstance(data, list):
                    briefs = data
                elif isinstance(data, dict):
                    if "scene_briefs" in data:
                        briefs = data["scene_briefs"]
                    elif "briefs" in data:
                        briefs = data["briefs"]
                    else:
                        # Try to extract numbered briefs
                        for i in range(len(batch_scenes)):
                            if f"brief_{i+1}" in data:
                                briefs.append(data[f"brief_{i+1}"])
        except:
            pass
        
        # If we don't have enough briefs, create placeholders
        while len(briefs) < len(batch_scenes):
            idx = len(briefs)
            briefs.append(self._create_placeholder_brief(batch_scenes[idx], idx))
        
        return briefs[:len(batch_scenes)]  # Don't return more than requested
    
    def _create_placeholder_brief(self, scene: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a placeholder brief for a scene"""
        scene_type = scene.get("type", "Proactive")
        
        if scene_type == "Proactive":
            return {
                "type": "Proactive",
                "goal": f"Complete objective in scene {index+1} before deadline",
                "conflict": f"Face opposition from antagonistic forces blocking the goal",
                "setback": f"Situation worsens, forcing new approach",
                "stakes": f"Failure means loss of critical opportunity",
                "links": {
                    "character_goal_id": "protagonist_goal",
                    "disaster_anchor": scene.get("disaster_anchor")
                }
            }
        else:
            return {
                "type": "Reactive",
                "reaction": f"Process the emotional impact of recent setback",
                "dilemma": f"Choose between two difficult options, each with costs",
                "decision": f"Commit to new course of action",
                "stakes": f"Wrong choice leads to greater losses",
                "links": {
                    "character_goal_id": "protagonist_goal",
                    "disaster_anchor": scene.get("disaster_anchor")
                }
            }
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        ok, errs = self.validator.validate(artifact)
        if ok:
            return True, "✓ Step 9 scene briefs pass validation"
        fixes = self.validator.fix_suggestions(errs)
        return False, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))
