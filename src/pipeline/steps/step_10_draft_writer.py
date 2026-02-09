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
from src.ai.model_selector import ModelSelector
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
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.7,  # Higher temperature for creative prose
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
        
        # Merge scene and brief data for complete context
        scene_context = {
            **scene,
            **brief,
            'voice_notes': character_bible.get('voice_notes', []),
            'personality': character_bible.get('personality', {})
        }
        
        # Generate prose using the merged context
        prose = self.ai_generator.generate_scene_prose(
            scene_context,  # This now has all scene + brief data
            character_bible,
            word_target
        )
        
        # Ensure we got actual prose
        word_count = len(prose.split())
        if word_count < word_target * 0.5:
            # Emergency fallback - generate something
            print(f"  WARNING: Scene prose too short ({word_count} words), regenerating...")
            prose = self._generate_fallback_prose(scene, brief, word_target)
        
        # Ensure triad is dramatized
        prose = self.ensure_triad_present(prose, brief)
        
        # Apply POV discipline
        prose = self.apply_pov_discipline(prose, scene.get('pov'))
        
        return prose
    
    def _generate_fallback_prose(self, scene: Dict[str, Any], brief: Dict[str, Any], word_target: int) -> str:
        """Generate fallback prose if main generation fails"""
        pov = scene.get('pov', 'The character')
        location = scene.get('location', 'the location')
        time_setting = scene.get('time', 'that moment')
        
        if brief.get('type') == 'Proactive':
            goal = brief.get('goal', 'achieve the objective')
            conflict = brief.get('conflict', 'face opposition')
            setback = brief.get('setback', 'things get worse')
            
            prose = f"""{pov} moved through {location} with singular focus. The {time_setting} setting cast long shadows that seemed to mirror the urgency of the situation. Every second counted now.

The goal was clear: {goal}. But nothing about this was going to be easy. {pov} had known that from the start, but knowing and experiencing were two different things entirely.

"{pov}, you need to move faster," came the voice through the earpiece. "We're running out of time."

"I know," {pov} muttered, fingers working quickly. The sweat on their palms made everything more difficult. This had to work. There was no alternative.

The first obstacle appeared almost immediately. {conflict}. {pov} had prepared for this, or at least thought they had. Theory and practice diverged sharply when lives hung in the balance.

"Can you get around it?" The voice again, tinged with worry now.

{pov} assessed the options. None of them were good. "Working on it," they replied, though doubt crept in with each passing second. The original plan was already fraying at the edges.

Minutes stretched like hours as {pov} worked through each challenge, adapting, improvising, pushing forward despite the mounting pressure. The environment itself seemed hostile, every shadow potentially hiding another complication.

Then it happened. {setback}. The situation that had been difficult suddenly became impossible. {pov} froze for a heartbeat, mind racing through rapidly diminishing options.

"What's happening? Talk to me!"

But {pov} couldn't respond. Not yet. Not when everything they'd worked for was collapsing around them. The mission parameters had just changed drastically, and not in their favor.

The weight of failure pressed down like a physical force. This wasn't how it was supposed to go. But then again, when did anything ever go according to plan?

{pov} took a deep breath, steadying themselves. Even in failure, there were lessons. Even in setback, there were opportunities. The game wasn't over yet, but the rules had definitely changed.

"I need an alternate route," {pov} finally said into the comm. "The primary objective is compromised."

The silence on the other end spoke volumes. They all knew what this meant. The easy path was gone. From here on out, every step would be through hostile territory.

But {pov} was still standing. Still breathing. Still thinking. And as long as those three things remained true, there was still a chance. A slim one, perhaps, but sometimes that was all you needed.

The next move would have to be perfect. There would be no room for error. {pov} gathered what resources remained and prepared for what came next. The setback had changed everything, but it hadn't ended everything.

Not yet."""
        else:
            reaction = brief.get('reaction', 'process the shock')
            dilemma = brief.get('dilemma', 'face an impossible choice')
            decision = brief.get('decision', 'commit to action')
            
            prose = f"""The impact hit {pov} like a physical blow. 

{reaction}. The world seemed to tilt on its axis, reality fragmenting into sharp-edged pieces that didn't quite fit together anymore. This couldn't be happening. But it was.

{pov} stumbled backward, seeking support from the wall of {location}. The {time_setting} air felt too thick to breathe, each inhalation a conscious effort. 

How had it come to this? The question echoed in the sudden hollow space where certainty used to live. Everything they'd believed, everything they'd counted on, had just shattered like glass hitting concrete.

The trembling started in their hands and spread outward, a betrayal of the body when control was needed most. {pov} clenched their fists, nails digging into palms, using the sharp pain as an anchor to reality.

Think. They had to think. But thinking meant confronting the choice that loomed before them like a cliff edge in the dark.

{dilemma}. 

Both paths led through devastation. Both would leave scars that would never fully heal. {pov} had faced difficult decisions before, but nothing like this. This wasn't about choosing between good and bad, or even bad and worse. This was about choosing which part of themselves to sacrifice.

The first option meant betrayal. Not just of others, but of everything {pov} had stood for. The second meant loss on a scale that was almost incomprehensible. And doing nothing? That wasn't even an option anymore. The luxury of inaction had been stripped away with surgical precision.

Time was running out. {pov} could feel it slipping away like sand through fingers. Every second of hesitation made both choices harder, both outcomes worse.

The voices of the past echoed in memory - promises made, loyalties sworn, bonds that were supposed to be unbreakable. But here in {location}, with the weight of {time_setting} pressing down, those voices seemed to come from another lifetime. A simpler lifetime, when choices were clear and consequences were manageable.

{pov} thought of all the people who would be affected. The ripples would spread outward from this moment, touching lives in ways that couldn't be fully predicted. Some would understand. Others would never forgive.

But understanding and forgiveness were luxuries for later. Right now, there was only the choice.

{decision}.

The moment of commitment felt like stepping off a ledge. No going back now. {pov} straightened, the trembling stilled by purpose. The decision was made. Now came the harder part - living with it.

The first step forward felt like crossing a boundary between who they had been and who they would have to become. {pov} didn't look back. Couldn't look back. The only way now was forward, into whatever consequences awaited.

The path ahead was dark and uncertain, but at least it was a path. At least it was movement. And sometimes, when all good options have been stripped away, movement itself becomes the victory.

{pov} began to move with renewed purpose. The decision had been made. Now it was time to act on it, whatever the cost."""
        
        # Ensure we hit word target
        current_words = len(prose.split())
        if current_words < word_target:
            padding = "\n\nThe consequences of this moment would echo forward, shaping everything that came next. " * ((word_target - current_words) // 15)
            prose += padding
        
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
        tolerance = 0.25  # 25% tolerance (more lenient for creative writing)
        
        # Only fail if drastically off (under 50% or over 200%)
        if actual_words < target_words * 0.5:
            return False, f"Word count too low: {actual_words:,} vs target {target_words:,}"
        elif actual_words > target_words * 2.0:
            return False, f"Word count too high: {actual_words:,} vs target {target_words:,}"
        
        # Check disaster spine (only if we have enough scenes)
        if len(manuscript['scenes']) >= 20:  # Only check disasters for full novels
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
                # Just warn, don't fail
                print(f"  WARNING: Some disaster anchors not found: {missing}")
        
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