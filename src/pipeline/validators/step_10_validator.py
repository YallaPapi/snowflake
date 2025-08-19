"""
Step 10 Validator: First Draft
Validates that manuscript has all required scenes and proper structure
"""

from typing import Dict, Any, Tuple, List

class Step10Validator:
    """
    Validator for Step 10: First Draft
    Ensures manuscript completeness and structure
    """
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 10 artifact
        
        Args:
            artifact: The Step 10 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'manuscript' not in artifact:
            errors.append("MISSING MANUSCRIPT: No manuscript object found")
            return False, errors
        
        manuscript = artifact['manuscript']
        
        # Check for chapters
        if 'chapters' not in manuscript:
            errors.append("MISSING CHAPTERS: No chapters array found")
            return False, errors
        
        chapters = manuscript['chapters']
        
        if len(chapters) == 0:
            errors.append("NO CHAPTERS: Manuscript has no chapters")
        
        # Validate chapter structure
        total_scenes = 0
        total_words = 0
        
        for i, chapter in enumerate(chapters):
            chapter_num = i + 1
            
            if 'number' not in chapter:
                errors.append(f"Chapter {chapter_num} MISSING NUMBER")
            
            if 'scenes' not in chapter:
                errors.append(f"Chapter {chapter_num} MISSING SCENES")
                continue
            
            scenes = chapter['scenes']
            
            if len(scenes) == 0:
                errors.append(f"Chapter {chapter_num} NO SCENES")
            
            # Validate each scene
            for j, scene in enumerate(scenes):
                scene_num = j + 1
                scene_id = f"Ch{chapter_num} Scene{scene_num}"
                
                # Check required scene fields
                if 'prose' not in scene:
                    errors.append(f"{scene_id} MISSING PROSE")
                else:
                    prose = scene['prose']
                    if len(prose) < 100:
                        errors.append(f"{scene_id} PROSE TOO SHORT: Need at least 100 characters")
                    
                    word_count = len(prose.split())
                    if word_count < 100:
                        errors.append(f"{scene_id} TOO FEW WORDS: {word_count} words (min 100)")
                    
                    total_words += word_count
                
                if 'pov' not in scene:
                    errors.append(f"{scene_id} MISSING POV")
                
                if 'type' not in scene:
                    errors.append(f"{scene_id} MISSING TYPE")
                
                total_scenes += 1
        
        # Check totals
        if total_scenes < 10:
            errors.append(f"TOO FEW SCENES: {total_scenes} scenes (min 10)")
        
        if total_words < 5000:
            errors.append(f"TOO SHORT: {total_words} words (min 5000)")
        
        # Store validation results
        manuscript['total_scenes'] = total_scenes
        manuscript['total_word_count'] = total_words
        manuscript['total_chapters'] = len(chapters)
        
        return len(errors) == 0, errors
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "MISSING MANUSCRIPT" in error:
                suggestions.append("Create manuscript object with chapters array")
            elif "MISSING CHAPTERS" in error:
                suggestions.append("Add chapters array to manuscript")
            elif "NO CHAPTERS" in error:
                suggestions.append("Generate at least one chapter")
            elif "MISSING SCENES" in error:
                suggestions.append("Add scenes array to chapter")
            elif "NO SCENES" in error:
                suggestions.append("Generate scenes for chapter")
            elif "MISSING PROSE" in error:
                suggestions.append("Generate prose text for scene")
            elif "PROSE TOO SHORT" in error:
                suggestions.append("Expand scene prose to at least 100 words")
            elif "TOO FEW WORDS" in error:
                suggestions.append("Expand scene to meet word target")
            elif "MISSING POV" in error:
                suggestions.append("Add POV character to scene")
            elif "MISSING TYPE" in error:
                suggestions.append("Add scene type (Proactive/Reactive)")
            elif "TOO FEW SCENES" in error:
                suggestions.append("Generate more scenes to reach minimum")
            elif "TOO SHORT" in error:
                suggestions.append("Expand manuscript to reach minimum word count")
            else:
                suggestions.append("Review Step 10 requirements")
        
        return suggestions