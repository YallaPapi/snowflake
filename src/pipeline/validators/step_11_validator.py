"""
Step 11 Validator: Comic Script Format Validation
Validates comic script artifacts against industry standards from PRD research
"""

from typing import Dict, Any, Tuple, List
import json

class Step11Validator:
    """
    Validates Step 11 comic script artifacts
    
    Based on PRD research standards:
    - 5-7 panels per page (max 9)
    - Max 50 words per panel
    - Max 20-35 words per balloon
    - Full Script (DC Style) format compliance
    """
    
    def __init__(self):
        # Panel guidelines from PRD research
        self.panel_guidelines = {
            "min_panels_per_page": 3,
            "standard_panels_per_page": 7,    # 5-7 standard range
            "max_panels_per_page": 9,         # Max 9 to avoid clutter
            "max_words_per_panel": 50,        # Max 50 words per panel
            "max_words_per_balloon": 35,      # Max 20-35 per balloon
            "max_balloons_per_panel": 3       # Max 2-3 balloons per panel
        }
        
        self.required_fields = [
            "metadata",
            "script_format", 
            "total_pages",
            "total_panels",
            "pages",
            "character_designs",
            "panel_statistics"
        ]
        
        self.valid_transition_types = [
            "moment_to_moment",
            "action_to_action", 
            "subject_to_subject",
            "scene_to_scene",
            "aspect_to_aspect",
            "non_sequitur"
        ]
        
        self.valid_shot_types = [
            "close_up",
            "medium_shot", 
            "wide_shot",
            "extreme_close_up",
            "establishing_shot"
        ]
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate complete comic script artifact
        
        Args:
            artifact: Comic script artifact to validate
            
        Returns:
            Tuple of (is_valid, validation_message)
        """
        try:
            # Check required top-level fields
            is_valid, message = self._validate_required_fields(artifact)
            if not is_valid:
                return False, message
            
            # Validate metadata
            is_valid, message = self._validate_metadata(artifact.get('metadata', {}))
            if not is_valid:
                return False, f"Metadata validation failed: {message}"
            
            # Validate script format
            is_valid, message = self._validate_script_format(artifact)
            if not is_valid:
                return False, f"Script format validation failed: {message}"
            
            # Validate pages structure
            is_valid, message = self._validate_pages(artifact.get('pages', []))
            if not is_valid:
                return False, f"Pages validation failed: {message}"
            
            # Validate character designs
            is_valid, message = self._validate_character_designs(artifact.get('character_designs', {}))
            if not is_valid:
                return False, f"Character designs validation failed: {message}"
            
            # Validate panel statistics against guidelines
            is_valid, message = self._validate_panel_statistics(artifact.get('panel_statistics', {}))
            if not is_valid:
                return False, f"Panel statistics validation failed: {message}"
            
            # Industry standards compliance check
            is_valid, message = self._validate_industry_compliance(artifact)
            if not is_valid:
                return False, f"Industry standards compliance failed: {message}"
            
            return True, "Comic script artifact validation passed"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_required_fields(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate all required fields are present"""
        for field in self.required_fields:
            if field not in artifact:
                return False, f"Missing required field: {field}"
            
            if artifact[field] is None:
                return False, f"Required field is None: {field}"
        
        return True, "Required fields validation passed"
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate metadata structure"""
        required_meta_fields = [
            "step", "step_name", "project_id", "created_at", 
            "version", "source_step", "format"
        ]
        
        for field in required_meta_fields:
            if field not in metadata:
                return False, f"Missing metadata field: {field}"
        
        # Check step number
        if metadata.get('step') != 11:
            return False, f"Invalid step number: {metadata.get('step')}, expected 11"
        
        # Check source step  
        if metadata.get('source_step') != 10:
            return False, f"Invalid source step: {metadata.get('source_step')}, expected 10"
        
        return True, "Metadata validation passed"
    
    def _validate_script_format(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate script format compliance"""
        script_format = artifact.get('script_format')
        
        # Must be Full Script format per PRD
        if script_format != 'full_script':
            return False, f"Invalid script format: {script_format}, expected 'full_script'"
        
        # Check format consistency in metadata
        meta_format = artifact.get('metadata', {}).get('format')
        if meta_format != 'full_script_dc_style':
            return False, f"Format mismatch in metadata: {meta_format}"
        
        return True, "Script format validation passed"
    
    def _validate_pages(self, pages: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate pages structure and content"""
        if not pages:
            return False, "No pages found in script"
        
        for page_idx, page in enumerate(pages):
            # Required page fields
            page_fields = ["page_number", "panel_count", "panels"]
            for field in page_fields:
                if field not in page:
                    return False, f"Page {page_idx + 1} missing field: {field}"
            
            # Validate page number sequence
            expected_page_num = page_idx + 1
            if page.get('page_number') != expected_page_num:
                return False, f"Page number mismatch: got {page.get('page_number')}, expected {expected_page_num}"
            
            # Validate panel count per page (5-7 standard, max 9 per PRD)
            panel_count = page.get('panel_count', 0)
            if panel_count > self.panel_guidelines['max_panels_per_page']:
                return False, f"Page {page['page_number']} has {panel_count} panels, max allowed is {self.panel_guidelines['max_panels_per_page']}"
            
            if panel_count < self.panel_guidelines['min_panels_per_page']:
                return False, f"Page {page['page_number']} has {panel_count} panels, minimum is {self.panel_guidelines['min_panels_per_page']}"
            
            # Validate panels
            is_valid, message = self._validate_panels(page.get('panels', []), page['page_number'])
            if not is_valid:
                return False, message
        
        return True, "Pages validation passed"
    
    def _validate_panels(self, panels: List[Dict[str, Any]], page_number: int) -> Tuple[bool, str]:
        """Validate individual panels"""
        if not panels:
            return False, f"Page {page_number} has no panels"
        
        for panel_idx, panel in enumerate(panels):
            # Required panel fields
            panel_fields = ["panel_number", "description", "dialogue", "transition_type"]
            for field in panel_fields:
                if field not in panel:
                    return False, f"Page {page_number}, Panel {panel_idx + 1} missing field: {field}"
            
            # Validate panel number sequence
            expected_panel_num = panel_idx + 1
            if panel.get('panel_number') != expected_panel_num:
                return False, f"Panel number mismatch on page {page_number}: got {panel.get('panel_number')}, expected {expected_panel_num}"
            
            # Validate panel description
            description = panel.get('description', '')
            if not description or len(description.strip()) < 10:
                return False, f"Page {page_number}, Panel {panel['panel_number']} has insufficient description"
            
            # Validate transition type
            transition = panel.get('transition_type')
            if transition not in self.valid_transition_types:
                return False, f"Page {page_number}, Panel {panel['panel_number']} has invalid transition type: {transition}"
            
            # Validate shot type if present
            shot_type = panel.get('shot_type')
            if shot_type and shot_type not in self.valid_shot_types:
                return False, f"Page {page_number}, Panel {panel['panel_number']} has invalid shot type: {shot_type}"
            
            # Validate dialogue
            is_valid, message = self._validate_panel_dialogue(panel.get('dialogue', []), page_number, panel['panel_number'])
            if not is_valid:
                return False, message
        
        return True, f"Panels validation passed for page {page_number}"
    
    def _validate_panel_dialogue(self, dialogue: List[Dict[str, Any]], 
                                page_number: int, panel_number: int) -> Tuple[bool, str]:
        """Validate dialogue within a panel"""
        if not dialogue:
            return True, "No dialogue to validate"  # Dialogue is optional
        
        # Check balloon count per panel (max 2-3 per PRD)
        if len(dialogue) > self.panel_guidelines['max_balloons_per_panel']:
            return False, f"Page {page_number}, Panel {panel_number} has {len(dialogue)} balloons, max allowed is {self.panel_guidelines['max_balloons_per_panel']}"
        
        total_words = 0
        
        for dialogue_idx, dialogue_entry in enumerate(dialogue):
            # Required dialogue fields
            dialogue_fields = ["character", "type", "text"]
            for field in dialogue_fields:
                if field not in dialogue_entry:
                    return False, f"Page {page_number}, Panel {panel_number}, Dialogue {dialogue_idx + 1} missing field: {field}"
            
            # Validate dialogue type
            dialogue_type = dialogue_entry.get('type')
            valid_types = ["balloon", "caption", "thought", "sfx"]
            if dialogue_type not in valid_types:
                return False, f"Invalid dialogue type: {dialogue_type}, must be one of {valid_types}"
            
            # Validate text word count per balloon (max 20-35 per PRD)
            text = dialogue_entry.get('text', '')
            word_count = len(text.split())
            
            if word_count > self.panel_guidelines['max_words_per_balloon']:
                return False, f"Page {page_number}, Panel {panel_number}: dialogue balloon has {word_count} words, max allowed is {self.panel_guidelines['max_words_per_balloon']}"
            
            total_words += word_count
        
        # Validate total words per panel (max 50 per PRD)
        if total_words > self.panel_guidelines['max_words_per_panel']:
            return False, f"Page {page_number}, Panel {panel_number} has {total_words} total words, max allowed is {self.panel_guidelines['max_words_per_panel']}"
        
        return True, "Dialogue validation passed"
    
    def _validate_character_designs(self, character_designs: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate character design information"""
        if not character_designs:
            return False, "No character designs found"
        
        for char_name, design in character_designs.items():
            if not isinstance(design, dict):
                return False, f"Character design for {char_name} must be a dictionary"
            
            # Check for basic design fields
            design_fields = ["description"]  # Minimum required
            for field in design_fields:
                if field not in design or not design[field]:
                    return False, f"Character {char_name} missing design field: {field}"
        
        return True, "Character designs validation passed"
    
    def _validate_panel_statistics(self, stats: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate panel statistics"""
        required_stats = ["total_panels", "total_pages", "avg_panels_per_page", "avg_words_per_panel"]
        
        for stat in required_stats:
            if stat not in stats:
                return False, f"Missing panel statistic: {stat}"
            
            if not isinstance(stats[stat], (int, float)):
                return False, f"Panel statistic {stat} must be numeric"
        
        return True, "Panel statistics validation passed"
    
    def _validate_industry_compliance(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate compliance with comic book industry standards from PRD
        """
        stats = artifact.get('panel_statistics', {})
        
        # Check average panels per page (5-7 standard)
        avg_panels = stats.get('avg_panels_per_page', 0)
        if avg_panels > self.panel_guidelines['max_panels_per_page']:
            return False, f"Average panels per page ({avg_panels}) exceeds industry maximum ({self.panel_guidelines['max_panels_per_page']})"
        
        # Check maximum panels per page
        max_panels = stats.get('max_panels_per_page', 0)
        if max_panels > self.panel_guidelines['max_panels_per_page']:
            return False, f"Maximum panels per page ({max_panels}) exceeds industry limit ({self.panel_guidelines['max_panels_per_page']})"
        
        # Check word density
        avg_words = stats.get('avg_words_per_panel', 0)
        if avg_words > self.panel_guidelines['max_words_per_panel']:
            return False, f"Average words per panel ({avg_words}) exceeds industry maximum ({self.panel_guidelines['max_words_per_panel']})"
        
        max_words = stats.get('max_words_per_panel', 0)
        if max_words > self.panel_guidelines['max_words_per_panel']:
            return False, f"Maximum words per panel ({max_words}) exceeds industry limit ({self.panel_guidelines['max_words_per_panel']})"
        
        return True, "Industry compliance validation passed"
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Convenience method for validation-only calls
        (Compatible with orchestrator validation pattern)
        """
        return self.validate(artifact)
    
    def get_validation_suggestions(self, artifact: Dict[str, Any]) -> List[str]:
        """
        Get specific suggestions for improving the comic script
        """
        suggestions = []
        stats = artifact.get('panel_statistics', {})
        
        # Panel density suggestions
        avg_panels = stats.get('avg_panels_per_page', 0)
        if avg_panels > 7:
            suggestions.append("Consider reducing panel count per page to improve readability")
        
        # Word count suggestions
        max_words = stats.get('max_words_per_panel', 0)
        if max_words > 40:
            suggestions.append("Break up dialogue in high-word-count panels")
        
        # Character design suggestions
        char_designs = artifact.get('character_designs', {})
        if len(char_designs) < 2:
            suggestions.append("Add more detailed character design information")
        
        return suggestions
    
    def validate_with_suggestions(self, artifact: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Enhanced validation that also returns improvement suggestions
        """
        is_valid, message = self.validate(artifact)
        suggestions = self.get_validation_suggestions(artifact)
        return is_valid, message, suggestions

if __name__ == "__main__":
    # Test validator
    validator = Step11Validator()
    
    # Test with minimal valid artifact
    test_artifact = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script", 
            "project_id": "test",
            "created_at": "2025-01-01T00:00:00",
            "version": "1.0.0",
            "source_step": 10,
            "format": "full_script_dc_style"
        },
        "script_format": "full_script",
        "total_pages": 1,
        "total_panels": 5,
        "pages": [{
            "page_number": 1,
            "panel_count": 5,
            "panels": [
                {
                    "panel_number": 1,
                    "description": "Wide shot of city skyline at dawn",
                    "dialogue": [],
                    "transition_type": "establishing_shot"
                }
            ]
        }],
        "character_designs": {
            "hero": {"description": "Tall, athletic build"}
        },
        "panel_statistics": {
            "total_panels": 1,
            "total_pages": 1, 
            "avg_panels_per_page": 1.0,
            "avg_words_per_panel": 0.0,
            "max_panels_per_page": 1,
            "max_words_per_panel": 0
        }
    }
    
    is_valid, message = validator.validate(test_artifact)
    print(f"Validation result: {is_valid}")
    print(f"Message: {message}")