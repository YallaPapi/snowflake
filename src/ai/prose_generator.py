"""
Reliable Prose Generator with Guaranteed Length
Ensures minimum word counts through chunked generation
"""

from typing import Dict, Any, List
from src.ai.generator import AIGenerator

class ProseGenerator:
    """
    Generates prose with guaranteed minimum length
    Uses chunked approach to ensure reliability
    """
    
    def __init__(self, generator: AIGenerator):
        self.generator = generator
    
    def generate_guaranteed_scene(self, 
                                 scene_brief: Dict[str, Any],
                                 character_bible: Dict[str, Any],
                                 word_target: int,
                                 min_words: int = None) -> str:
        """
        Generate scene prose with guaranteed minimum length
        
        Args:
            scene_brief: Scene brief with triad elements
            character_bible: Character details
            word_target: Desired word count
            min_words: Minimum acceptable word count (default: word_target // 2)
            
        Returns:
            Scene prose meeting minimum length
        """
        if min_words is None:
            min_words = max(word_target // 2, 500)  # At least 500 words
        
        # Try full generation first
        prose = self._generate_full_scene(scene_brief, character_bible, word_target)
        
        # Check if meets minimum
        word_count = len(prose.split())
        if word_count >= min_words:
            return prose
        
        # If too short, use chunked approach
        print(f"    Scene too short ({word_count} words), using chunked generation...")
        return self._generate_chunked_scene(scene_brief, character_bible, word_target, min_words)
    
    def _generate_full_scene(self,
                            scene_brief: Dict[str, Any],
                            character_bible: Dict[str, Any],
                            word_target: int) -> str:
        """Generate complete scene in one pass"""
        scene_type = scene_brief.get("type", "Proactive")
        pov_character = scene_brief.get("pov", "Unknown")
        
        if scene_type == "Proactive":
            system_prompt = f"""You are a professional novelist. Write a complete {word_target}-word scene.

CRITICAL: This must be AT LEAST {word_target} words of actual prose, not a summary.

POV: {pov_character} (deep third person limited)
Type: Proactive Scene

Structure this scene with three clear beats:
1. GOAL: {scene_brief.get('goal', 'character pursues objective')}
2. CONFLICT: {scene_brief.get('conflict', 'obstacles arise')}  
3. SETBACK: {scene_brief.get('setback', 'situation worsens')}

Stakes: {scene_brief.get('stakes', 'significant consequences')}

Write with:
- Vivid sensory details and concrete imagery
- Natural dialogue that reveals character
- Internal thoughts showing emotions
- Action sequences that build tension
- Smooth transitions between story beats

IMPORTANT: Do not write a summary or outline. Write the actual scene with full prose, dialogue, and description."""

        else:
            system_prompt = f"""You are a professional novelist. Write a complete {word_target}-word scene.

CRITICAL: This must be AT LEAST {word_target} words of actual prose, not a summary.

POV: {pov_character} (deep third person limited)
Type: Reactive Scene (Sequel)

Structure this scene with three clear beats:
1. REACTION: {scene_brief.get('reaction', 'emotional response')}
2. DILEMMA: {scene_brief.get('dilemma', 'difficult choice')}
3. DECISION: {scene_brief.get('decision', 'character chooses path')}

Stakes: {scene_brief.get('stakes', 'significant consequences')}

Write with:
- Deep emotional interiority and vulnerability  
- Physical sensations of stress/emotion
- Internal debate and moral reasoning
- Quiet character moments and reflection
- Clear resolution leading to action

IMPORTANT: Do not write a summary or outline. Write the actual scene with full prose and emotional depth."""

        user_prompt = f"""Scene Details:
Setting: {scene_brief.get('location', 'appropriate location')} at {scene_brief.get('time', 'appropriate time')}
Context: {scene_brief.get('summary', '')}
Previous: {scene_brief.get('inbound_hook', 'scene follows naturally')}
Next: {scene_brief.get('outbound_hook', 'scene leads forward')}

Character: {pov_character}
Traits: {character_bible.get('personality', {})}
Voice: {character_bible.get('voice_notes', ['consistent character voice'])}

REQUIREMENTS:
1. Write EXACTLY {word_target} words (count carefully)
2. Use {pov_character}'s unique voice throughout
3. Include substantial dialogue (at least 30% of scene)
4. Show don't tell - use concrete details
5. End with clear transition to next scene

Write the complete scene now:"""

        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        model_config = {
            "temperature": 0.8,
            "max_tokens": min(word_target * 4, 8000)  # Large buffer
        }
        
        return self.generator.generate(prompt_data, model_config)
    
    def _generate_chunked_scene(self,
                               scene_brief: Dict[str, Any],
                               character_bible: Dict[str, Any],
                               word_target: int,
                               min_words: int) -> str:
        """Generate scene in chunks to guarantee length"""
        scene_type = scene_brief.get("type", "Proactive")
        chunks = []
        
        # Define chunks based on scene type
        if scene_type == "Proactive":
            chunk_prompts = [
                ("Opening", f"Write the opening of the scene where {scene_brief.get('pov')} begins pursuing: {scene_brief.get('goal')}"),
                ("Conflict", f"Continue the scene as {scene_brief.get('pov')} encounters this obstacle: {scene_brief.get('conflict')}"),
                ("Setback", f"Complete the scene as the situation worsens: {scene_brief.get('setback')}")
            ]
        else:
            chunk_prompts = [
                ("Reaction", f"Write the opening showing {scene_brief.get('pov')}'s reaction: {scene_brief.get('reaction')}"),
                ("Dilemma", f"Continue as {scene_brief.get('pov')} faces this dilemma: {scene_brief.get('dilemma')}"),
                ("Decision", f"Complete the scene with {scene_brief.get('pov')}'s decision: {scene_brief.get('decision')}")
            ]
        
        target_per_chunk = word_target // 3
        
        for chunk_name, chunk_description in chunk_prompts:
            chunk_prose = self._generate_chunk(
                chunk_name,
                chunk_description,
                scene_brief,
                character_bible,
                target_per_chunk,
                len(chunks)  # Chunk index for context
            )
            chunks.append(chunk_prose)
        
        # Combine chunks
        full_scene = "\n\n".join(chunks)
        
        # If still too short, add padding
        final_word_count = len(full_scene.split())
        if final_word_count < min_words:
            padding_needed = min_words - final_word_count
            padding = self._generate_scene_extension(scene_brief, character_bible, padding_needed)
            full_scene += "\n\n" + padding
        
        return full_scene
    
    def _generate_chunk(self,
                       chunk_name: str,
                       chunk_description: str,
                       scene_brief: Dict[str, Any],
                       character_bible: Dict[str, Any],
                       target_words: int,
                       chunk_index: int) -> str:
        """Generate a single chunk of the scene"""
        
        context = ""
        if chunk_index > 0:
            context = "Continue the scene naturally from the previous section. "
        
        system_prompt = f"""You are writing part of a novel scene. Write {target_words} words of high-quality prose.

{context}{chunk_description}

POV: {scene_brief.get('pov')} (third person limited)
Setting: {scene_brief.get('location')} at {scene_brief.get('time')}

Write with:
- Vivid sensory details
- Natural dialogue 
- Internal thoughts
- Smooth narrative flow

Write exactly {target_words} words of prose:"""

        user_prompt = f"""Character: {scene_brief.get('pov')}
Voice: {character_bible.get('voice_notes', ['natural'])}
Personality: {character_bible.get('personality', {})}

{chunk_description}

Stakes: {scene_brief.get('stakes', 'important consequences')}

Write {target_words} words now:"""

        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        model_config = {
            "temperature": 0.8,
            "max_tokens": target_words * 3
        }
        
        return self.generator.generate(prompt_data, model_config)
    
    def _generate_scene_extension(self,
                                 scene_brief: Dict[str, Any],
                                 character_bible: Dict[str, Any],
                                 words_needed: int) -> str:
        """Generate additional content to reach minimum length"""
        
        system_prompt = f"""Add {words_needed} words to extend this scene naturally.

POV: {scene_brief.get('pov')}
Add more:
- Sensory details and atmosphere
- Internal thoughts and emotions  
- Character interactions
- Environmental description

Write {words_needed} additional words:"""

        user_prompt = f"""The scene needs {words_needed} more words. 

Add natural content like:
- More dialogue
- Character thoughts
- Environmental details
- Emotional responses

Character: {scene_brief.get('pov')}
Setting: {scene_brief.get('location')}

Write {words_needed} words of additional content:"""

        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        model_config = {
            "temperature": 0.7,
            "max_tokens": words_needed * 2
        }
        
        return self.generator.generate(prompt_data, model_config)