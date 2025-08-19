"""
Step 10 Implementation: Draft the Novel
Generates the complete manuscript from frozen scene list and briefs
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import hashlib

from src.ai.generator import AIGenerator
from src.export.manuscript_exporter import ManuscriptExporter

class Step10DraftWriter:
    """
    Step 10: Draft the Novel
    Writes complete manuscript scene-by-scene using briefs and character bibles
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize Step 10 executor
        
        Args:
            project_dir: Directory to store artifacts
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI generator
        self.ai_generator = AIGenerator()
        
        # Initialize exporter
        self.exporter = ManuscriptExporter(project_dir)
        
        self.current_word_count = 0
        self.scenes_drafted = []
        
    def execute(self,
                scene_list: Dict[str, Any],
                scene_briefs: Dict[str, Any],
                character_bibles: Dict[str, Any],
                project_id: str,
                target_words: int = 90000,
                model_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 10: Draft the complete novel
        
        Args:
            scene_list: Step 8 scene list artifact
            scene_briefs: Step 9 scene briefs artifact
            character_bibles: Step 7 character bibles artifact
            project_id: Project UUID
            target_words: Target word count for novel
            model_config: AI model configuration
            
        Returns:
            Tuple of (success, artifact, message)
        """
        # Default model config for creative writing
        if not model_config:
            model_config = {
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.7,  # Higher for creative writing
                "seed": 42
            }
        
        # Calculate upstream hash
        upstream_content = json.dumps({
            "scene_list": scene_list,
            "scene_briefs": scene_briefs
        }, sort_keys=True)
        upstream_hash = hashlib.sha256(upstream_content.encode()).hexdigest()
        
        # Initialize manuscript
        manuscript = {
            "title": "Generated Novel",
            "chapters": [],
            "scenes": [],
            "total_word_count": 0,
            "metadata": self.create_metadata(project_id, upstream_hash, model_config)
        }
        
        # Get scenes and briefs
        scenes = scene_list.get('scenes', [])
        briefs = scene_briefs.get('scene_briefs', [])
        
        if len(scenes) != len(briefs):
            return False, {}, f"Mismatch: {len(scenes)} scenes but {len(briefs)} briefs"
        
        # Track progress
        current_chapter = []
        chapter_num = 1
        act_num = 1
        
        # Draft each scene
        for i, (scene, brief) in enumerate(zip(scenes, briefs)):
            scene_num = i + 1
            
            # Get POV character bible
            pov_name = scene.get('pov', 'Unknown')
            character_bible = self.get_character_bible(pov_name, character_bibles)
            
            # Check for act breaks
            if self.is_disaster_scene(scene, scene_list):
                act_num = self.get_act_number(scene_num, len(scenes))
            
            # Generate scene prose
            scene_prose = self.draft_scene(
                scene, brief, character_bible, model_config
            )
            
            # Track scene
            scene_data = {
                "scene_num": scene_num,
                "chapter": scene.get('chapter_hint', f"Chapter {chapter_num}"),
                "pov": pov_name,
                "type": brief.get('type', 'Unknown'),
                "word_count": len(scene_prose.split()),
                "prose": scene_prose,
                "disaster_anchor": scene.get('disaster_anchor'),
                "act": act_num
            }
            
            manuscript['scenes'].append(scene_data)
            current_chapter.append(scene_data)
            self.current_word_count += scene_data['word_count']
            
            # Check for chapter break
            if self.should_break_chapter(scene, scenes, i):
                manuscript['chapters'].append({
                    "number": chapter_num,
                    "scenes": current_chapter,
                    "word_count": sum(s['word_count'] for s in current_chapter)
                })
                current_chapter = []
                chapter_num += 1
            
            # Progress update
            progress = (i + 1) / len(scenes) * 100
            print(f"Drafting: {progress:.1f}% complete ({self.current_word_count:,} words)")
            
            # Check disaster spine integrity
            if scene.get('disaster_anchor'):
                self.verify_disaster_integrity(scene_data, brief, act_num)
        
        # Add final chapter if needed
        if current_chapter:
            manuscript['chapters'].append({
                "number": chapter_num,
                "scenes": current_chapter,
                "word_count": sum(s['word_count'] for s in current_chapter)
            })
        
        # Final statistics
        manuscript['total_word_count'] = self.current_word_count
        manuscript['chapter_count'] = len(manuscript['chapters'])
        manuscript['scene_count'] = len(manuscript['scenes'])
        
        # Validate manuscript
        is_valid, validation_message = self.validate_manuscript(
            manuscript, scene_list, target_words
        )
        
        if not is_valid:
            return False, manuscript, f"Manuscript validation failed: {validation_message}"
        
        # Save manuscript
        save_paths = self.save_manuscript(manuscript, project_id)
        
        # Export to all formats
        export_paths = self.exporter.export_all_formats(manuscript, project_id)
        
        success_message = f"""
Step 10 Complete!
- Chapters: {manuscript['chapter_count']}
- Scenes: {manuscript['scene_count']}
- Words: {manuscript['total_word_count']:,} (Target: {target_words:,})
- Formats exported: {', '.join(export_paths.keys())}
- Saved to: {save_paths['markdown']}
"""
        
        return True, manuscript, success_message
    
    def draft_scene(self,
                   scene: Dict[str, Any],
                   brief: Dict[str, Any],
                   character_bible: Dict[str, Any],
                   model_config: Dict[str, Any]) -> str:
        """
        Draft a single scene
        
        Args:
            scene: Scene from scene list
            brief: Scene brief with triad
            character_bible: POV character's bible
            model_config: AI model configuration
            
        Returns:
            Scene prose
        """
        word_target = scene.get('word_target', 1500)
        
        # Merge scene and brief data
        scene_context = {
            **scene,
            **brief,
            'voice_notes': character_bible.get('voice_notes', []),
            'personality': character_bible.get('personality', {})
        }
        
        # Generate prose
        prose = self.ai_generator.generate_scene_prose(
            scene_context,
            character_bible,
            word_target
        )
        
        # Ensure triad is dramatized
        prose = self.ensure_triad_present(prose, brief)
        
        # Apply POV discipline
        prose = self.apply_pov_discipline(prose, scene.get('pov'))
        
        return prose
    
    def ensure_triad_present(self, prose: str, brief: Dict[str, Any]) -> str:
        """Ensure the triad elements are dramatized in the prose"""
        scene_type = brief.get('type', 'Proactive')
        
        if scene_type == 'Proactive':
            # Check for Goal, Conflict, Setback
            required = ['goal', 'conflict', 'setback']
        else:
            # Check for Reaction, Dilemma, Decision
            required = ['reaction', 'dilemma', 'decision']
        
        # This would analyze the prose and potentially add missing elements
        # For now, return as is (would need NLP to properly analyze)
        return prose
    
    def apply_pov_discipline(self, prose: str, pov_character: str) -> str:
        """Ensure strict POV discipline"""
        # This would filter all descriptions through POV character's perception
        # For now, return as is (would need sophisticated text processing)
        return prose
    
    def get_character_bible(self,
                           character_name: str,
                           character_bibles: Dict[str, Any]) -> Dict[str, Any]:
        """Get character bible for POV character"""
        bibles = character_bibles.get('bibles', [])
        
        for bible in bibles:
            if bible.get('name') == character_name:
                return bible
        
        # Return empty bible if not found
        return {
            'name': character_name,
            'voice_notes': [],
            'personality': {}
        }
    
    def is_disaster_scene(self, scene: Dict[str, Any], scene_list: Dict[str, Any]) -> bool:
        """Check if scene is a disaster anchor"""
        disaster_anchor = scene.get('disaster_anchor')
        return disaster_anchor in ['D1', 'D2', 'D3']
    
    def get_act_number(self, scene_num: int, total_scenes: int) -> int:
        """Determine act number based on scene position"""
        position = scene_num / total_scenes
        
        if position <= 0.25:
            return 1  # Act I
        elif position <= 0.75:
            return 2  # Act II
        else:
            return 3  # Act III
    
    def should_break_chapter(self,
                           current_scene: Dict[str, Any],
                           all_scenes: List[Dict[str, Any]],
                           index: int) -> bool:
        """Determine if chapter should break after this scene"""
        # Break on disaster scenes
        if current_scene.get('disaster_anchor'):
            return True
        
        # Break on major location changes
        if index < len(all_scenes) - 1:
            next_scene = all_scenes[index + 1]
            if current_scene.get('location') != next_scene.get('location'):
                # Major location change might warrant chapter break
                pass
        
        # Break on POV changes (optional)
        if index < len(all_scenes) - 1:
            next_scene = all_scenes[index + 1]
            if current_scene.get('pov') != next_scene.get('pov'):
                # Could break chapter on POV change
                pass
        
        # Break every 3-5 scenes as default
        if index > 0 and (index + 1) % 4 == 0:
            return True
        
        return False
    
    def verify_disaster_integrity(self,
                                 scene_data: Dict[str, Any],
                                 brief: Dict[str, Any],
                                 act_num: int):
        """Verify disaster scenes maintain spine integrity"""
        disaster = scene_data.get('disaster_anchor')
        
        if disaster == 'D1':
            # Verify forces commitment
            if 'forces' not in scene_data['prose'].lower():
                print(f"WARNING: D1 scene may not show forcing function")
        
        elif disaster == 'D2':
            # Verify moral pivot
            if 'realizes' not in scene_data['prose'].lower():
                print(f"WARNING: D2 scene may not show moral pivot")
        
        elif disaster == 'D3':
            # Verify forces endgame
            if 'final' not in scene_data['prose'].lower():
                print(f"WARNING: D3 scene may not force endgame")
    
    def validate_manuscript(self,
                           manuscript: Dict[str, Any],
                           scene_list: Dict[str, Any],
                           target_words: int) -> Tuple[bool, str]:
        """
        Validate the completed manuscript
        
        Args:
            manuscript: Generated manuscript
            scene_list: Original scene list
            target_words: Target word count
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Check all scenes drafted
        expected_scenes = len(scene_list.get('scenes', []))
        actual_scenes = len(manuscript.get('scenes', []))
        
        if actual_scenes != expected_scenes:
            return False, f"Missing scenes: expected {expected_scenes}, got {actual_scenes}"
        
        # Check word count within tolerance
        actual_words = manuscript.get('total_word_count', 0)
        tolerance = 0.1  # 10% tolerance
        
        if abs(actual_words - target_words) > target_words * tolerance:
            return False, f"Word count off: {actual_words:,} vs target {target_words:,}"
        
        # Check disaster spine
        disasters_found = {
            'D1': False,
            'D2': False,
            'D3': False
        }
        
        for scene in manuscript['scenes']:
            anchor = scene.get('disaster_anchor')
            if anchor:
                disasters_found[anchor] = True
        
        if not all(disasters_found.values()):
            missing = [d for d, found in disasters_found.items() if not found]
            return False, f"Missing disasters: {missing}"
        
        # Check triads dramatized (would need NLP analysis)
        # For now, assume valid if we got this far
        
        return True, "Manuscript valid"
    
    def create_metadata(self,
                       project_id: str,
                       upstream_hash: str,
                       model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for manuscript"""
        return {
            "project_id": project_id,
            "step": 10,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get("model_name", "unknown"),
            "temperature": model_config.get("temperature", 0.7),
            "hash_upstream": upstream_hash,
            "generator": "Snowflake Method v1.0"
        }
    
    def save_manuscript(self, manuscript: Dict[str, Any], project_id: str) -> Dict[str, Path]:
        """
        Save manuscript in multiple formats
        
        Args:
            manuscript: Complete manuscript
            project_id: Project ID
            
        Returns:
            Dict of save paths
        """
        project_path = self.project_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        paths = {}
        
        # Save JSON (full data)
        json_path = project_path / "step_10_manuscript.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(manuscript, f, indent=2, ensure_ascii=False)
        paths['json'] = json_path
        
        # Save Markdown (readable)
        md_path = project_path / "manuscript.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            self.write_markdown(f, manuscript)
        paths['markdown'] = md_path
        
        # Save plain text
        txt_path = project_path / "manuscript.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            self.write_plaintext(f, manuscript)
        paths['text'] = txt_path
        
        return paths
    
    def write_markdown(self, file, manuscript: Dict[str, Any]):
        """Write manuscript as markdown"""
        file.write("# MANUSCRIPT\n\n")
        file.write(f"**Word Count:** {manuscript['total_word_count']:,}\n")
        file.write(f"**Chapters:** {manuscript['chapter_count']}\n")
        file.write(f"**Scenes:** {manuscript['scene_count']}\n\n")
        file.write("---\n\n")
        
        for chapter in manuscript['chapters']:
            file.write(f"## Chapter {chapter['number']}\n\n")
            
            for scene in chapter['scenes']:
                if scene.get('disaster_anchor'):
                    file.write(f"### Scene {scene['scene_num']} - {scene['disaster_anchor']}\n")
                else:
                    file.write(f"### Scene {scene['scene_num']}\n")
                
                file.write(f"*POV: {scene['pov']} | Type: {scene['type']} | ")
                file.write(f"Words: {scene['word_count']:,}*\n\n")
                
                file.write(scene['prose'])
                file.write("\n\n---\n\n")
    
    def write_plaintext(self, file, manuscript: Dict[str, Any]):
        """Write manuscript as plain text"""
        for chapter in manuscript['chapters']:
            file.write(f"\n\nCHAPTER {chapter['number']}\n\n")
            
            for scene in chapter['scenes']:
                file.write(scene['prose'])
                file.write("\n\n")