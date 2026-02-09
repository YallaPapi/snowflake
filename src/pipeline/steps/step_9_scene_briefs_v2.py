"""
Step 9 Implementation V2: Scene Briefs with Better Generation
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from src.pipeline.validators.step_9_validator import Step9Validator
from src.ai.generator import AIGenerator
from src.ai.model_selector import ModelSelector
from src.ai.bulletproof_generator import get_bulletproof_generator

class Step9SceneBriefsV2:
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step9Validator()
        self.generator = AIGenerator()
        self.bulletproof_generator = get_bulletproof_generator()

    def execute(self,
                step8_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        if not model_config:
            model_config = {"temperature": 0.5, "max_tokens": 3000}
        
        upstream_hash = hashlib.sha256(json.dumps(step8_artifact, sort_keys=True).encode()).hexdigest()
        
        # Get all scenes
        all_scenes = step8_artifact.get("scenes", [])
        scene_briefs = []
        
        print(f"Generating {len(all_scenes)} scene briefs individually...")
        
        # Import progress tracker
        try:
            from src.ui.progress_tracker import get_global_tracker
            tracker = get_global_tracker()
        except ImportError:
            tracker = None
        
        # Generate each brief individually for better quality
        for i, scene in enumerate(all_scenes):
            scene_num = i + 1
            
            # Update progress
            if tracker:
                tracker.update_step_progress(i, len(all_scenes), f"Scene {scene_num}: {scene.get('summary', 'No summary')[:50]}...")
            else:
                print(f"  Generating brief {scene_num}/{len(all_scenes)}...", end="")
            
            # Generate brief for this specific scene
            brief = self._generate_single_brief(scene, scene_num, step8_artifact, model_config)
            scene_briefs.append(brief)
            
            if not tracker:
                print(" done")
        
        # Final progress update
        if tracker:
            tracker.update_step_progress(len(all_scenes), len(all_scenes), "All scene briefs generated")
        
        # Create artifact
        artifact = {"scene_briefs": scene_briefs}
        
        # Validate
        ok, errs = self.validator.validate(artifact)
        
        # Add metadata even if validation fails
        artifact = self.add_metadata(artifact, project_id, "step9_v2", model_config, upstream_hash)
        path = self.save_artifact(artifact, project_id)
        
        if not ok:
            # Save anyway but report validation issues
            fixes = self.validator.fix_suggestions(errs)
            error_summary = f"Generated {len(scene_briefs)} briefs with {len(errs)} validation warnings"
            return True, artifact, f"{error_summary}. Saved to {path}"
        
        return True, artifact, f"Step 9 artifact saved to {path}"
    
    def _generate_single_brief(self, 
                              scene: Dict[str, Any], 
                              scene_num: int,
                              step8_artifact: Dict[str, Any],
                              model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single scene brief with concrete details"""
        
        scene_type = scene.get("type", "Proactive")
        pov = scene.get("pov", "Unknown")
        summary = scene.get("summary", "")
        location = scene.get("location", "")
        time = scene.get("time", "")
        disaster_anchor = scene.get("disaster_anchor")
        conflict_info = scene.get("conflict", {})
        
        # Build specific prompt for this scene
        if scene_type == "Proactive":
            prompt = self._build_proactive_prompt(
                scene_num, pov, summary, location, time, 
                disaster_anchor, conflict_info
            )
        else:
            prompt = self._build_reactive_prompt(
                scene_num, pov, summary, location, time,
                disaster_anchor, conflict_info  
            )
        
        # Generate with bulletproof reliability
        response = self.bulletproof_generator.generate_guaranteed(prompt, model_config)
        
        # Parse response
        brief = self._parse_brief_response(response, scene_type)
        
        # Ensure required fields
        brief["type"] = scene_type
        if "links" not in brief:
            brief["links"] = {}
        brief["links"]["character_goal_id"] = f"{pov.replace(' ', '_')}_goal"
        if disaster_anchor:
            brief["links"]["disaster_anchor"] = disaster_anchor
        
        return brief
    
    def _build_proactive_prompt(self, scene_num: int, pov: str, summary: str, 
                                location: str, time: str, disaster_anchor: str,
                                conflict_info: Dict[str, Any]) -> Dict[str, str]:
        """Build prompt for Proactive scene"""
        
        system = """Generate a CONCRETE Proactive scene brief with specific, measurable elements.
REQUIREMENTS:
- Goal: Action verb + specific object + deadline
- Conflict: Named obstacles with specifics
- Setback: Clear worsening of situation
- Stakes: What specifically dies/fails/ends"""

        user = f"""Scene {scene_num} (Proactive)
POV: {pov}
Summary: {summary}
Location: {location}
Time: {time}
{"Disaster Anchor: " + disaster_anchor if disaster_anchor else ""}

Generate a Proactive brief with:
1. GOAL: What {pov} must achieve RIGHT NOW with a deadline
2. CONFLICT: Specific obstacles blocking the goal (name people/things)
3. SETBACK: How the situation gets WORSE (doors close, options narrow)
4. STAKES: What DIES/FAILS if unsuccessful

Example format:
{{
  "goal": "steal the evidence files from the locked vault before midnight shift change",
  "conflict": "corrupt sergeant Martinez guards the vault while security cameras record everything",
  "setback": "silent alarm triggers, exits seal, SWAT team arrives in 3 minutes",
  "stakes": "key witness Chen dies in prison if evidence not retrieved tonight"
}}

Generate the brief now:"""

        return {"system": system, "user": user}
    
    def _build_reactive_prompt(self, scene_num: int, pov: str, summary: str,
                               location: str, time: str, disaster_anchor: str,
                               conflict_info: Dict[str, Any]) -> Dict[str, str]:
        """Build prompt for Reactive scene"""
        
        system = """Generate a CONCRETE Reactive scene brief with visceral, specific elements.
REQUIREMENTS:
- Reaction: Physical/emotional with body responses
- Dilemma: Two bad options that both hurt
- Decision: Active commitment to specific action
- Stakes: Real consequences that matter"""

        user = f"""Scene {scene_num} (Reactive)
POV: {pov}
Summary: {summary}
Location: {location}
Time: {time}
{"Disaster Anchor: " + disaster_anchor if disaster_anchor else ""}

Generate a Reactive brief with:
1. REACTION: {pov}'s PHYSICAL response (trembles/vomits/collapses)
2. DILEMMA: Choose between TWO BAD OPTIONS (both must hurt)
3. DECISION: Commits to SPECIFIC next action
4. STAKES: What gets DESTROYED either way

Example format:
{{
  "reaction": "hands shake uncontrollably, vomits bile into trash can, legs give out",
  "dilemma": "either expose the corruption and watch family die, or stay silent while innocents are murdered",
  "decision": "decides to secretly record the next meeting while pretending compliance",
  "stakes": "family tortured if discovered, three witnesses die if stays silent"
}}

Generate the brief now:"""

        return {"system": system, "user": user}
    
    def _parse_brief_response(self, response: str, scene_type: str) -> Dict[str, Any]:
        """Parse AI response into brief structure with bulletproof fallbacks"""
        
        # Try multiple JSON parsing strategies
        parsed_json = self._extract_json_from_response(response)
        if parsed_json:
            # Validate required fields are present
            if self._validate_brief_fields(parsed_json, scene_type):
                return parsed_json
        
        # Try text extraction
        brief = self._extract_brief_from_text(response, scene_type)
        if self._validate_brief_fields(brief, scene_type):
            return brief
        
        # Emergency fallback - create minimal valid brief
        return self._create_emergency_brief(scene_type)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON with multiple strategies"""
        # Strategy 1: Direct JSON parse
        try:
            if response.strip().startswith("{") and response.strip().endswith("}"):
                return json.loads(response.strip())
        except Exception as e:
            pass

        # Strategy 2: Find JSON in code blocks
        import re
        code_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except Exception as e:
                continue

        # Strategy 3: Find any JSON-like structure
        json_pattern = r'\{[^{}]*"[^"]*"[^{}]*\}'
        matches = re.findall(json_pattern, response)
        for match in matches:
            try:
                return json.loads(match)
            except Exception as e:
                continue

        return None
    
    def _extract_brief_from_text(self, response: str, scene_type: str) -> Dict[str, Any]:
        """Extract brief fields from text response"""
        brief = {"type": scene_type}
        
        # Normalize response for extraction
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        text = " ".join(lines).lower()
        
        if scene_type == "Proactive":
            required_fields = ["goal", "conflict", "setback", "stakes"]
        else:
            required_fields = ["reaction", "dilemma", "decision", "stakes"]
        
        for field in required_fields:
            # Try multiple extraction patterns
            value = self._extract_field_value(text, field, lines)
            if value:
                brief[field] = value
        
        return brief
    
    def _extract_field_value(self, text: str, field: str, lines: List[str]) -> Optional[str]:
        """Extract specific field value with multiple strategies"""
        import re
        
        # Strategy 1: Find "field: value" patterns
        for line in lines:
            lower_line = line.lower()
            if f"{field}:" in lower_line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip().strip('"').strip("'")
        
        # Strategy 2: Find field patterns with regex
        patterns = [
            rf'{field}[:\s]+"([^"]*)"',
            rf'{field}[:\s]+([^.!?]+)[.!?]',
            rf'"{field}"[:\s]*"([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _validate_brief_fields(self, brief: Dict[str, Any], scene_type: str) -> bool:
        """Validate that brief has required fields with content"""
        if scene_type == "Proactive":
            required = ["goal", "conflict", "setback", "stakes"]
        else:
            required = ["reaction", "dilemma", "decision", "stakes"]
        
        for field in required:
            if field not in brief or not isinstance(brief[field], str) or len(brief[field].strip()) < 10:
                return False
        
        return True
    
    def _create_emergency_brief(self, scene_type: str) -> Dict[str, Any]:
        """Create emergency brief when all parsing fails"""
        if scene_type == "Proactive":
            return {
                "type": "Proactive",
                "goal": "complete critical mission objective before the deadline expires",
                "conflict": "hostile forces actively work to prevent success using superior resources",
                "setback": "initial strategy fails completely, situation becomes significantly worse",
                "stakes": "total failure means permanent loss of what matters most",
                "links": {"character_goal_id": "protagonist_goal"}
            }
        else:
            return {
                "type": "Reactive", 
                "reaction": "overwhelming shock and disbelief, physical symptoms of extreme stress",
                "dilemma": "must choose between two terrible options that both cause severe damage",
                "decision": "commits to desperate action despite enormous personal cost and risk",
                "stakes": "either choice leads to devastating consequences for innocent people",
                "links": {"character_goal_id": "protagonist_goal"}
            }
    
    def _create_fallback_brief(self, scene: Dict[str, Any], scene_num: int) -> Dict[str, Any]:
        """Create a concrete fallback brief"""
        scene_type = scene.get("type", "Proactive")
        pov = scene.get("pov", "Character")
        location = scene.get("location", "location")
        
        if scene_type == "Proactive":
            return {
                "type": "Proactive",
                "goal": f"secure critical evidence from {location} before midnight deadline",
                "conflict": f"armed guards and surveillance systems block all access points",
                "setback": f"alarm triggers, exits seal, police surround building in 5 minutes",
                "stakes": f"witness dies in prison if evidence not secured by dawn",
                "links": {
                    "character_goal_id": f"{pov.replace(' ', '_')}_goal",
                    "disaster_anchor": scene.get("disaster_anchor")
                }
            }
        else:
            return {
                "type": "Reactive",
                "reaction": f"collapses to knees, vomits violently, hands shake uncontrollably",
                "dilemma": f"either betray partner and lose everything, or stay loyal and watch family die",
                "decision": f"decides to infiltrate enemy organization alone tonight",
                "stakes": f"family murdered if caught, partner dies if mission fails",
                "links": {
                    "character_goal_id": f"{pov.replace(' ', '_')}_goal",
                    "disaster_anchor": scene.get("disaster_anchor")
                }
            }
    
    def add_metadata(self, content: Dict[str, Any], project_id: str, 
                    prompt_hash: str, model_config: Dict[str, Any], 
                    upstream_hash: str) -> Dict[str, Any]:
        """Add metadata to artifact"""
        artifact = content.copy()
        briefs = artifact.get("scene_briefs", [])
        
        # Run validator to get stats (ignore errors)
        self.validator.validate(artifact)
        
        artifact["metadata"] = {
            "project_id": project_id,
            "step": 9,
            "version": "2.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", 
                self.generator.default_model if hasattr(self.generator, "default_model") else "unknown"),
            "temperature": model_config.get("temperature", 0.5),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        
        return artifact
    
    def save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save artifact to disk"""
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        path = project_path / "step_9_scene_briefs.json"
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        return path
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a scene briefs artifact
        
        Args:
            artifact: Scene briefs artifact to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        ok, errs = self.validator.validate(artifact)
        if ok:
            brief_count = len(artifact.get("scene_briefs", []))
            return True, f"✓ Step 9 scene briefs pass validation ({brief_count} briefs)"
        
        fixes = self.validator.fix_suggestions(errs)
        return False, "VALIDATION FAILED:\n" + "\n".join(f"ERROR: {e} | FIX: {f}" for e,f in zip(errs, fixes))