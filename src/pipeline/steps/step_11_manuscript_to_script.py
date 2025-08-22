"""
Step 11 Implementation: Manuscript to Comic Script Converter
Converts Step 10 manuscript into comic book script format following industry standards
"""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from src.pipeline.validators.step_11_validator import Step11Validator
from src.ai.generator import AIGenerator
from src.ai.bulletproof_generator import get_bulletproof_generator

class Step11ManuscriptToScript:
    """
    Converts Step 10 manuscript into comic script format
    
    Based on PRD research:
    - Full Script (DC Style) format
    - 5-7 panels per page (max 9)
    - Max 50 words per panel dialogue
    - Panel transition types from Scott McCloud
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step11Validator()
        self.generator = AIGenerator()
        self.bulletproof_generator = get_bulletproof_generator()
        
        # Panel transition types from Scott McCloud (per PRD)
        self.transition_types = [
            "moment_to_moment",     # Small changes, slow pacing
            "action_to_action",     # Shows motion steps  
            "subject_to_subject",   # Changing focus within scene
            "scene_to_scene",       # Location/time change
            "aspect_to_aspect",     # Different aspects of scene
            "non_sequitur"          # No logical progression
        ]
        
        # Panel composition guidelines (per PRD)
        self.panel_guidelines = {
            "min_panels_per_page": 3,
            "standard_panels_per_page": 5,  # 5-7 standard
            "max_panels_per_page": 9,       # Max 9 to avoid clutter
            "max_words_per_panel": 50,      # Max 50 words per panel
            "max_words_per_balloon": 35,    # Max 20-35 per balloon
            "max_balloons_per_panel": 3     # Max 2-3 balloons per panel
        }
    
    def execute(self, 
                step10_artifact: Dict[str, Any], 
                step7_artifact: Dict[str, Any],
                step8_artifact: Dict[str, Any],
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 11: Convert manuscript to comic script
        
        Args:
            step10_artifact: Step 10 manuscript data
            step7_artifact: Step 7 character bibles for visual consistency
            step8_artifact: Step 8 scene list for structure reference
            project_id: Project identifier
            model_config: Model configuration for AI generation
            
        Returns:
            Tuple of (success, comic_script_artifact, message)
        """
        if not model_config:
            model_config = {"temperature": 0.7, "max_tokens": 2000}
            
        try:
            # Calculate upstream hash for traceability
            upstream_data = {
                "step10": step10_artifact,
                "step7": step7_artifact,
                "step8": step8_artifact
            }
            upstream_hash = hashlib.sha256(
                json.dumps(upstream_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Extract required data from artifacts
            manuscript_content = self._extract_manuscript_content(step10_artifact)
            character_bibles = step7_artifact.get('bibles', [])
            scene_list = step8_artifact.get('scenes', [])
            
            # Parse manuscript into visual scenes
            scenes = self._parse_manuscript_into_scenes(manuscript_content, scene_list)
            
            # Progress tracking
            try:
                from src.ui.progress_tracker import get_global_tracker
                tracker = get_global_tracker()
            except ImportError:
                tracker = None
            
            # Convert scenes to comic pages
            comic_pages = self._convert_scenes_to_pages(
                scenes, character_bibles, project_id, model_config, tracker
            )
            
            # Create comic script artifact
            comic_script_artifact = self._create_artifact(
                comic_pages, character_bibles, project_id, upstream_hash
            )
            
            # Validate the comic script
            is_valid, validation_message = self.validator.validate(comic_script_artifact)
            if not is_valid:
                return False, {}, f"Comic script validation failed: {validation_message}"
            
            # Save artifact
            artifact_path = self._save_artifact(comic_script_artifact, project_id)
            
            return True, comic_script_artifact, f"Step 11 artifact saved to {artifact_path}"
            
        except Exception as e:
            return False, {}, f"Error in Step 11 execution: {str(e)}"
    
    def _extract_manuscript_content(self, step10_artifact: Dict[str, Any]) -> str:
        """Extract manuscript content from Step 10 artifact"""
        # Try different possible field names for manuscript content
        content_fields = ['content', 'manuscript_text', 'text', 'chapters']
        
        for field in content_fields:
            if field in step10_artifact and step10_artifact[field]:
                content = step10_artifact[field]
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # If chapters is a list, join them
                    return '\n\n'.join(str(chapter) for chapter in content)
        
        raise ValueError("No manuscript content found in Step 10 artifact")
    
    def _parse_manuscript_into_scenes(self, manuscript: str, scene_list: List[Dict]) -> List[Dict]:
        """
        Parse manuscript content into discrete scenes using scene list as guide
        """
        if not manuscript.strip():
            raise ValueError("Manuscript content is empty")
        
        scenes = []
        
        # Split manuscript by common scene/chapter separators
        separators = [
            r'\n\s*Chapter \d+[^\n]*\n',
            r'\n\s*Scene \d+[^\n]*\n', 
            r'\n\s*---+\s*\n',
            r'\n\s*\*\s*\*\s*\*\s*\n',
            r'\n\s*#{3,}\s*\n'
        ]
        
        # Try each separator pattern
        scene_breaks = [manuscript]  # Start with whole manuscript
        for pattern in separators:
            new_breaks = []
            for section in scene_breaks:
                new_breaks.extend(re.split(pattern, section))
            scene_breaks = new_breaks
        
        # Create scene objects
        for i, scene_content in enumerate(scene_breaks):
            if not scene_content.strip():
                continue
                
            # Match with scene list metadata if available
            scene_meta = scene_list[i] if i < len(scene_list) else {}
            
            scenes.append({
                "scene_index": i,
                "content": scene_content.strip(),
                "pov": scene_meta.get('pov', 'unknown'),
                "location": scene_meta.get('location', 'unknown'),
                "summary": scene_meta.get('summary', ''),
                "type": scene_meta.get('type', 'proactive'),
                "word_count": len(scene_content.split())
            })
        
        if not scenes:
            # Fallback: treat whole manuscript as single scene
            scenes = [{
                "scene_index": 0,
                "content": manuscript.strip(),
                "pov": "unknown",
                "location": "unknown", 
                "summary": "Full manuscript",
                "type": "proactive",
                "word_count": len(manuscript.split())
            }]
        
        return scenes
    
    def _convert_scenes_to_pages(self, scenes: List[Dict], character_bibles: List[Dict], 
                                project_id: str, model_config: Dict[str, Any], 
                                tracker=None) -> List[Dict]:
        """Convert all scenes to comic pages with progress tracking"""
        comic_pages = []
        page_number = 1
        
        print(f"Converting {len(scenes)} scenes to comic pages...")
        
        for scene_idx, scene in enumerate(scenes):
            # Update progress
            if tracker:
                scene_summary = scene.get('summary', f"Scene {scene_idx + 1}")
                tracker.update_step_progress(scene_idx, len(scenes), 
                                           f"Converting scene: {scene_summary[:50]}...")
            else:
                print(f"  Converting scene {scene_idx + 1}/{len(scenes)}...")
            
            # Convert scene to pages
            scene_pages, page_number = self._convert_single_scene_to_pages(
                scene, scene_idx, page_number, character_bibles, project_id, model_config
            )
            comic_pages.extend(scene_pages)
        
        # Final progress update
        if tracker:
            tracker.update_step_progress(len(scenes), len(scenes), 
                                       f"Generated {len(comic_pages)} comic pages")
        
        return comic_pages
    
    def _convert_single_scene_to_pages(self, scene: Dict, scene_idx: int, start_page: int, 
                                      character_bibles: List[Dict], project_id: str,
                                      model_config: Dict[str, Any]) -> Tuple[List[Dict], int]:
        """
        Convert a single scene into comic pages following PRD guidelines
        """
        try:
            scene_content = scene['content']
            
            # Extract visual beats using AI
            beats = self._extract_visual_beats(scene_content, scene, model_config)
            
            if not beats:
                # Fallback: create simple panel from scene summary
                beats = [{
                    "beat_type": "establishing",
                    "description": scene.get('summary', 'Scene content'),
                    "dialogue": [],
                    "characters_present": [],
                    "action": scene_content[:200] + "..." if len(scene_content) > 200 else scene_content,
                    "emotion": "neutral",
                    "transition_type": "scene_to_scene"
                }]
            
            # Group beats into pages (5-7 panels standard)
            pages = []
            current_page = start_page
            current_panels = []
            
            for beat_idx, beat in enumerate(beats):
                # Convert beat to panel
                panel = self._create_panel_from_beat(beat, beat_idx, scene, character_bibles)
                current_panels.append(panel)
                
                # Check if page is full (standard 5-7 panels, max 9)
                if len(current_panels) >= self.panel_guidelines["standard_panels_per_page"]:
                    # Create page
                    pages.append(self._create_page(current_page, scene_idx, current_panels))
                    current_page += 1
                    current_panels = []
            
            # Handle remaining panels
            if current_panels:
                pages.append(self._create_page(current_page, scene_idx, current_panels))
                current_page += 1
            
            return pages, current_page
            
        except Exception as e:
            # Fallback: create a single page with simple panel
            fallback_page = self._create_fallback_page(scene, scene_idx, start_page)
            return [fallback_page], start_page + 1
    
    def _extract_visual_beats(self, scene_content: str, scene: Dict[str, Any], 
                             model_config: Dict[str, Any]) -> List[Dict]:
        """
        Extract visual beats from prose using AI generation with better error handling
        """
        pov = scene.get('pov', 'unknown')
        location = scene.get('location', 'unknown')
        scene_type = scene.get('type', 'proactive')
        
        prompt = f"""Convert this prose scene into discrete visual beats for a comic book.
Each beat should be a single moment that can be shown in one panel.

Scene Context:
- POV Character: {pov}
- Location: {location}
- Scene Type: {scene_type}

Guidelines:
- One major action or dialogue exchange per beat
- Limit to 5-9 beats total (panels per scene)
- Consider visual storytelling over exposition
- Include specific character actions and expressions

Scene content:
{scene_content}

Return as JSON array:
[
    {{
        "beat_type": "action|dialogue|reaction|establishing",
        "description": "Visual description for artist",
        "dialogue": ["Character: Text"],
        "characters_present": ["character1"],
        "action": "Brief action description",
        "emotion": "neutral|happy|tense|dramatic",
        "transition_type": "action_to_action"
    }}
]"""
        
        try:
            # Use bulletproof generator for better reliability
            response = self.bulletproof_generator.generate(
                prompt, 
                temperature=model_config.get('temperature', 0.7),
                max_tokens=model_config.get('max_tokens', 2000)
            )
            
            # Clean and parse JSON response
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:-3]
            
            beats_data = json.loads(clean_response)
            
            if isinstance(beats_data, list) and beats_data:
                return beats_data[:9]  # Limit to max 9 beats per scene
            else:
                return self._create_fallback_beats(scene_content, scene)
                
        except Exception as e:
            print(f"  Warning: AI beat extraction failed ({str(e)}), using fallback")
            return self._create_fallback_beats(scene_content, scene)
    
    def _create_fallback_beats(self, scene_content: str, scene: Dict[str, Any]) -> List[Dict]:
        """Create fallback beats when AI generation fails"""
        paragraphs = [p.strip() for p in scene_content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [scene_content[:500]]  # Use first 500 chars as fallback
        
        beats = []
        for i, para in enumerate(paragraphs[:7]):  # Limit to 7 beats max
            beats.append({
                "beat_type": "mixed",
                "description": f"Panel showing: {para[:150]}...",
                "dialogue": [],
                "characters_present": [scene.get('pov', 'unknown')],
                "action": para,
                "emotion": "neutral",
                "transition_type": "action_to_action"
            })
        
        return beats
    
    def _create_panel_from_beat(self, beat: Dict, panel_idx: int, scene: Dict[str, Any], 
                               character_bibles: List[Dict]) -> Dict:
        """
        Create a comic panel from a visual beat
        Following Full Script (DC Style) format from PRD
        """
        # Extract dialogue and format for comics
        dialogue_entries = []
        for dialogue in beat.get('dialogue', []):
            if ':' in dialogue:
                character, text = dialogue.split(':', 1)
                character = character.strip()
                text = text.strip().strip('"')
                
                # Ensure dialogue fits panel limits (max 35 words per balloon)
                words = text.split()
                if len(words) > self.panel_guidelines["max_words_per_balloon"]:
                    # Split into multiple balloons
                    mid_point = len(words) // 2
                    text1 = ' '.join(words[:mid_point])
                    text2 = ' '.join(words[mid_point:])
                    dialogue_entries.extend([
                        {"character": character, "type": "balloon", "text": text1},
                        {"character": character, "type": "balloon", "text": text2}
                    ])
                else:
                    dialogue_entries.append({
                        "character": character, 
                        "type": "balloon", 
                        "text": text
                    })
        
        # Create panel description for artists
        panel_description = self._create_panel_description(beat, scene, character_bibles)
        
        return {
            "panel_number": panel_idx + 1,
            "description": panel_description,
            "dialogue": dialogue_entries,
            "transition_type": beat.get('transition_type', 'action_to_action'),
            "characters": beat.get('characters_present', []),
            "shot_type": self._determine_shot_type(beat),
            "mood": beat.get('emotion', 'neutral'),
            "word_count": sum(len(d['text'].split()) for d in dialogue_entries)
        }
    
    def _create_panel_description(self, beat: Dict, scene: Dict, character_bibles: List[Dict]) -> str:
        """Create artist-friendly panel description using art direction terminology"""
        description_parts = []
        
        # Shot type and framing
        shot_type = self._determine_shot_type(beat)
        description_parts.append(f"{shot_type.upper()}:")
        
        # Location context
        if scene.get('location') and scene['location'] != 'unknown':
            description_parts.append(f"Location: {scene['location']}.")
        
        # Character positions and actions
        if beat.get('characters_present'):
            char_names = [name for name in beat['characters_present'] if name.lower() != 'unknown']
            if char_names:
                description_parts.append(f"Characters: {', '.join(char_names)}.")
        
        # Main visual description from beat
        if beat.get('description'):
            description_parts.append(beat['description'])
        elif beat.get('action'):
            description_parts.append(beat['action'])
        
        # Mood and atmosphere
        emotion = beat.get('emotion', 'neutral')
        if emotion and emotion != 'neutral':
            description_parts.append(f"Mood: {emotion}.")
        
        return ' '.join(description_parts)
    
    def _create_page(self, page_number: int, scene_index: int, panels: List[Dict]) -> Dict:
        """Create a comic page object"""
        return {
            "page_number": page_number,
            "scene_index": scene_index,
            "panel_count": len(panels),
            "panels": panels
        }
    
    def _create_fallback_page(self, scene: Dict, scene_idx: int, page_number: int) -> Dict:
        """Create a fallback page when scene conversion fails"""
        fallback_panel = {
            "panel_number": 1,
            "description": f"WIDE SHOT: {scene.get('summary', 'Scene content')}. Location: {scene.get('location', 'Unknown')}.",
            "dialogue": [],
            "transition_type": "scene_to_scene",
            "characters": [scene.get('pov', 'unknown')] if scene.get('pov') != 'unknown' else [],
            "shot_type": "wide_shot",
            "mood": "neutral",
            "word_count": 0
        }
        
        return {
            "page_number": page_number,
            "scene_index": scene_idx,
            "panel_count": 1,
            "panels": [fallback_panel]
        }
    
    def _determine_shot_type(self, beat: Dict) -> str:
        """
        Determine appropriate shot type based on beat content
        Using standard comic terminology from PRD
        """
        beat_type = beat.get('beat_type', 'mixed')
        action = beat.get('action', '').lower()
        
        if 'close' in action or 'whisper' in action or 'emotion' in action:
            return "close_up"
        elif 'establishing' in beat_type or 'location' in action:
            return "wide_shot"  
        elif 'group' in action or 'crowd' in action:
            return "wide_shot"
        else:
            return "medium_shot"
    
    def _create_artifact(self, comic_pages: List[Dict], character_bibles: List[Dict],
                        project_id: str, upstream_hash: str) -> Dict[str, Any]:
        """Create the Step 11 comic script artifact"""
        character_designs = self._extract_character_designs(character_bibles)
        panel_stats = self._calculate_panel_stats(comic_pages)
        
        return {
            "metadata": {
                "step": 11,
                "step_name": "manuscript_to_script",
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "source_step": 10,
                "format": "full_script_dc_style",
                "upstream_hash": upstream_hash
            },
            "script_format": "full_script",  # Full Script (DC Style) per PRD
            "total_pages": len(comic_pages),
            "total_panels": sum(len(page.get('panels', [])) for page in comic_pages),
            "pages": comic_pages,
            "character_designs": character_designs,
            "panel_statistics": panel_stats
        }
    
    def _extract_character_designs(self, character_bibles: List[Dict]) -> Dict:
        """Extract character design information from Step 7 bibles for visual consistency"""
        designs = {}
        
        # Handle both list and dict formats for character bibles
        if isinstance(character_bibles, dict):
            character_bibles = [character_bibles]
        
        for bible_entry in character_bibles:
            if isinstance(bible_entry, dict):
                # Extract character name and physical details
                char_name = bible_entry.get('name', 'unknown')
                physical = bible_entry.get('physical', {})
                
                designs[char_name] = {
                    "description": physical.get('description', bible_entry.get('description', '')),
                    "height": physical.get('height', ''),
                    "build": physical.get('build', ''),
                    "hair": physical.get('hair', ''),
                    "eyes": physical.get('eyes', ''),
                    "distinguishing_features": physical.get('distinguishing_features', ''),
                    "typical_clothing": physical.get('clothing', ''),
                    "color_palette": physical.get('color_notes', '')
                }
        
        return designs
    
    def _calculate_panel_stats(self, pages: List[Dict]) -> Dict:
        """
        Calculate panel statistics for validation
        """
        total_panels = sum(len(page.get('panels', [])) for page in pages)
        
        panel_counts_per_page = [len(page.get('panels', [])) for page in pages]
        avg_panels_per_page = sum(panel_counts_per_page) / len(panel_counts_per_page) if panel_counts_per_page else 0
        
        word_counts = []
        for page in pages:
            for panel in page.get('panels', []):
                word_counts.append(panel.get('word_count', 0))
        
        avg_words_per_panel = sum(word_counts) / len(word_counts) if word_counts else 0
        
        return {
            "total_panels": total_panels,
            "total_pages": len(pages),
            "avg_panels_per_page": round(avg_panels_per_page, 1),
            "max_panels_per_page": max(panel_counts_per_page) if panel_counts_per_page else 0,
            "min_panels_per_page": min(panel_counts_per_page) if panel_counts_per_page else 0,
            "avg_words_per_panel": round(avg_words_per_panel, 1),
            "max_words_per_panel": max(word_counts) if word_counts else 0
        }
    
    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> str:
        """Save the comic script artifact following Snowflake patterns"""
        # Ensure project directory exists
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON artifact
        artifact_path = project_path / "step_11_comic_script.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        # Save human-readable version
        readable_path = project_path / "step_11_comic_script.txt"
        self._save_readable_script(artifact, readable_path)
        
        return str(artifact_path)
    
    def _save_readable_script(self, artifact: Dict[str, Any], filepath: Path):
        """
        Save human-readable comic script in Full Script format
        Following DC Style formatting from PRD
        """
        with open(filepath, 'w') as f:
            f.write(f"COMIC SCRIPT - {artifact['metadata']['project_id'].upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Format: {artifact.get('script_format', 'Full Script').title()}\n")
            f.write(f"Total Pages: {artifact.get('total_pages', 0)}\n")
            f.write(f"Total Panels: {artifact.get('total_panels', 0)}\n\n")
            
            # Character designs section
            f.write("CHARACTER DESIGNS\n")
            f.write("-" * 20 + "\n")
            for char_name, design in artifact.get('character_designs', {}).items():
                f.write(f"{char_name.upper()}:\n")
                f.write(f"  Description: {design.get('description', 'N/A')}\n")
                f.write(f"  Build: {design.get('height', 'N/A')} / {design.get('build', 'N/A')}\n")
                f.write(f"  Hair/Eyes: {design.get('hair', 'N/A')} / {design.get('eyes', 'N/A')}\n")
                f.write("\n")
            
            # Script pages
            f.write("\nSCRIPT\n")
            f.write("=" * 20 + "\n\n")
            
            for page in artifact.get('pages', []):
                f.write(f"PAGE {page['page_number']} ({page['panel_count']} panels)\n")
                f.write("-" * 30 + "\n")
                
                for panel in page.get('panels', []):
                    f.write(f"PANEL {panel['panel_number']}: {panel['description']}\n")
                    
                    # Dialogue
                    for dialogue in panel.get('dialogue', []):
                        char_name = dialogue['character'].upper()
                        balloon_type = dialogue['type'].upper()
                        text = dialogue['text']
                        f.write(f"  {char_name} ({balloon_type}): \"{text}\"\n")
                    
                    f.write("\n")
                
                f.write("\n")

if __name__ == "__main__":
    # Test execution
    step11 = Step11ManuscriptToScript("test_artifacts")
    print("Step 11: Manuscript to Script Converter initialized")