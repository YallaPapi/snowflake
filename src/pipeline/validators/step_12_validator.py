"""
Step 12 Validator: Comic Script Formatting Validation
Validates formatted comic script artifacts for professional output compliance
"""

from typing import Dict, Any, Tuple, List
import json

class Step12Validator:
    """
    Validates Step 12 formatted comic script artifacts
    
    Ensures compliance with professional formatting standards:
    - DC Style Full Script format compliance
    - Character design sheet completeness
    - Production notes accuracy
    - Export format validation
    """
    
    def __init__(self):
        self.required_fields = [
            "metadata",
            "format_options", 
            "formatted_outputs",
            "export_info"
        ]
        
        self.valid_script_formats = [
            "dc_style",
            "marvel_method",
            "indie"
        ]
        
        self.valid_export_formats = [
            "txt", "pdf", "docx", "fountain"
        ]
        
        self.required_formatted_outputs = [
            "professional_script",
            "production_notes"
        ]
        
        self.optional_formatted_outputs = [
            "character_sheets",
            "panel_layouts"
        ]
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate complete formatted comic script artifact
        
        Args:
            artifact: Formatted comic script artifact to validate
            
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
            
            # Validate format options
            is_valid, message = self._validate_format_options(artifact.get('format_options', {}))
            if not is_valid:
                return False, f"Format options validation failed: {message}"
            
            # Validate formatted outputs
            is_valid, message = self._validate_formatted_outputs(artifact.get('formatted_outputs', {}))
            if not is_valid:
                return False, f"Formatted outputs validation failed: {message}"
            
            # Validate export info
            is_valid, message = self._validate_export_info(artifact.get('export_info', {}))
            if not is_valid:
                return False, f"Export info validation failed: {message}"
            
            # Validate professional script formatting
            is_valid, message = self._validate_professional_script_format(
                artifact.get('formatted_outputs', {}).get('professional_script', {})
            )
            if not is_valid:
                return False, f"Professional script format validation failed: {message}"
            
            return True, "Formatted comic script artifact validation passed"
            
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
            "version", "source_step", "format_type"
        ]
        
        for field in required_meta_fields:
            if field not in metadata:
                return False, f"Missing metadata field: {field}"
        
        # Check step number
        if metadata.get('step') != 12:
            return False, f"Invalid step number: {metadata.get('step')}, expected 12"
        
        # Check source step  
        if metadata.get('source_step') != 11:
            return False, f"Invalid source step: {metadata.get('source_step')}, expected 11"
        
        # Check format type is valid
        format_type = metadata.get('format_type')
        if format_type not in self.valid_script_formats:
            return False, f"Invalid format type: {format_type}, must be one of {self.valid_script_formats}"
        
        return True, "Metadata validation passed"
    
    def _validate_format_options(self, format_options: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate format options"""
        required_options = ["script_format"]
        
        for option in required_options:
            if option not in format_options:
                return False, f"Missing format option: {option}"
        
        # Validate script format
        script_format = format_options.get('script_format')
        if script_format not in self.valid_script_formats:
            return False, f"Invalid script format: {script_format}, must be one of {self.valid_script_formats}"
        
        # Validate export formats if present
        if 'export_formats' in format_options:
            export_formats = format_options['export_formats']
            if not isinstance(export_formats, list):
                return False, "Export formats must be a list"
            
            for fmt in export_formats:
                if fmt not in self.valid_export_formats:
                    return False, f"Invalid export format: {fmt}, must be one of {self.valid_export_formats}"
        
        return True, "Format options validation passed"
    
    def _validate_formatted_outputs(self, formatted_outputs: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate formatted outputs structure"""
        # Check required outputs
        for required_output in self.required_formatted_outputs:
            if required_output not in formatted_outputs:
                return False, f"Missing required formatted output: {required_output}"
        
        # Validate professional script
        professional_script = formatted_outputs.get('professional_script', {})
        if not isinstance(professional_script, dict):
            return False, "Professional script must be a dictionary"
        
        required_script_fields = ["format_name", "description", "script_content"]
        for field in required_script_fields:
            if field not in professional_script:
                return False, f"Professional script missing field: {field}"
        
        # Validate script content
        script_content = professional_script.get('script_content', [])
        if not isinstance(script_content, list):
            return False, "Script content must be a list of strings"
        
        if len(script_content) == 0:
            return False, "Script content cannot be empty"
        
        # Validate character sheets if present
        if 'character_sheets' in formatted_outputs:
            is_valid, message = self._validate_character_sheets(formatted_outputs['character_sheets'])
            if not is_valid:
                return False, f"Character sheets validation failed: {message}"
        
        # Validate panel layouts if present
        if 'panel_layouts' in formatted_outputs:
            is_valid, message = self._validate_panel_layouts(formatted_outputs['panel_layouts'])
            if not is_valid:
                return False, f"Panel layouts validation failed: {message}"
        
        # Validate production notes
        is_valid, message = self._validate_production_notes(formatted_outputs.get('production_notes', {}))
        if not is_valid:
            return False, f"Production notes validation failed: {message}"
        
        return True, "Formatted outputs validation passed"
    
    def _validate_character_sheets(self, character_sheets: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate character design sheets"""
        required_fields = ["format_name", "description", "characters"]
        
        for field in required_fields:
            if field not in character_sheets:
                return False, f"Character sheets missing field: {field}"
        
        characters = character_sheets.get('characters', {})
        if not isinstance(characters, dict):
            return False, "Characters must be a dictionary"
        
        if len(characters) == 0:
            return False, "At least one character design sheet is required"
        
        # Validate individual character sheets
        for char_name, char_sheet in characters.items():
            required_char_fields = ["character_name", "design_notes", "art_requirements"]
            
            for field in required_char_fields:
                if field not in char_sheet:
                    return False, f"Character {char_name} missing field: {field}"
            
            # Validate design notes
            design_notes = char_sheet.get('design_notes', {})
            if not isinstance(design_notes, dict):
                return False, f"Design notes for {char_name} must be a dictionary"
            
            # Validate art requirements  
            art_requirements = char_sheet.get('art_requirements', [])
            if not isinstance(art_requirements, list) or len(art_requirements) == 0:
                return False, f"Art requirements for {char_name} must be a non-empty list"
        
        return True, "Character sheets validation passed"
    
    def _validate_panel_layouts(self, panel_layouts: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate panel layout guides"""
        required_fields = ["format_name", "description", "pages"]
        
        for field in required_fields:
            if field not in panel_layouts:
                return False, f"Panel layouts missing field: {field}"
        
        pages = panel_layouts.get('pages', [])
        if not isinstance(pages, list):
            return False, "Panel layout pages must be a list"
        
        if len(pages) == 0:
            return False, "At least one page layout guide is required"
        
        # Validate individual page guides
        for page_idx, page_guide in enumerate(pages):
            required_page_fields = ["page_number", "panel_count", "layout_recommendation"]
            
            for field in required_page_fields:
                if field not in page_guide:
                    return False, f"Page guide {page_idx + 1} missing field: {field}"
            
            # Validate page number
            page_number = page_guide.get('page_number')
            if not isinstance(page_number, int) or page_number < 1:
                return False, f"Invalid page number in page guide {page_idx + 1}: {page_number}"
            
            # Validate panel count
            panel_count = page_guide.get('panel_count')
            if not isinstance(panel_count, int) or panel_count < 1:
                return False, f"Invalid panel count in page guide {page_idx + 1}: {panel_count}"
        
        return True, "Panel layouts validation passed"
    
    def _validate_production_notes(self, production_notes: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate production notes"""
        required_fields = ["format_name", "description", "script_statistics", "industry_compliance"]
        
        for field in required_fields:
            if field not in production_notes:
                return False, f"Production notes missing field: {field}"
        
        # Validate script statistics
        script_stats = production_notes.get('script_statistics', {})
        required_stats = ["total_pages", "total_panels"]
        
        for stat in required_stats:
            if stat not in script_stats:
                return False, f"Script statistics missing field: {stat}"
            
            if not isinstance(script_stats[stat], (int, float)) or script_stats[stat] < 0:
                return False, f"Invalid script statistic {stat}: {script_stats[stat]}"
        
        # Validate industry compliance
        compliance = production_notes.get('industry_compliance', {})
        required_compliance = ["panel_density", "word_density", "format_standard"]
        
        for comp in required_compliance:
            if comp not in compliance:
                return False, f"Industry compliance missing field: {comp}"
        
        # Validate compliance values
        panel_density = compliance.get('panel_density')
        if panel_density not in ["PASS", "REVIEW NEEDED"]:
            return False, f"Invalid panel density value: {panel_density}"
        
        word_density = compliance.get('word_density')
        if word_density not in ["PASS", "REVIEW NEEDED"]:
            return False, f"Invalid word density value: {word_density}"
        
        return True, "Production notes validation passed"
    
    def _validate_export_info(self, export_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate export information"""
        required_fields = ["formats_generated", "template_style", "total_pages", "total_panels"]
        
        for field in required_fields:
            if field not in export_info:
                return False, f"Export info missing field: {field}"
        
        # Validate formats generated
        formats_generated = export_info.get('formats_generated', [])
        if not isinstance(formats_generated, list):
            return False, "Formats generated must be a list"
        
        for fmt in formats_generated:
            if fmt not in self.valid_export_formats:
                return False, f"Invalid format generated: {fmt}, must be one of {self.valid_export_formats}"
        
        # Validate numeric fields
        numeric_fields = ["total_pages", "total_panels"]
        for field in numeric_fields:
            value = export_info.get(field)
            if not isinstance(value, (int, float)) or value < 0:
                return False, f"Invalid export info {field}: {value}"
        
        return True, "Export info validation passed"
    
    def _validate_professional_script_format(self, professional_script: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate professional script format compliance
        Check for DC Style Full Script format elements
        """
        if not professional_script:
            return False, "Professional script is empty"
        
        script_content = professional_script.get('script_content', [])
        
        if not script_content:
            return False, "Script content is empty"
        
        # Join content for pattern checking
        full_script = "\n".join(script_content)
        
        # Check for DC Style format elements
        format_checks = {
            "has_page_headers": "PAGE " in full_script,
            "has_panel_descriptions": "PANEL " in full_script,
            "has_character_dialogue": "(" in full_script and ")" in full_script,
            "has_character_reference": "CHARACTER" in full_script.upper()
        }
        
        failed_checks = []
        for check_name, passed in format_checks.items():
            if not passed:
                failed_checks.append(check_name.replace('_', ' ').title())
        
        if failed_checks:
            return False, f"DC Style format validation failed: missing {', '.join(failed_checks)}"
        
        # Check script length (should not be empty or too short)
        if len(full_script) < 100:
            return False, "Script content appears too short for a complete comic script"
        
        return True, "Professional script format validation passed"
    
    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Convenience method for validation-only calls
        (Compatible with orchestrator validation pattern)
        """
        return self.validate(artifact)
    
    def get_validation_suggestions(self, artifact: Dict[str, Any]) -> List[str]:
        """
        Get specific suggestions for improving the formatted comic script
        """
        suggestions = []
        
        # Check format options
        format_options = artifact.get('format_options', {})
        if not format_options.get('include_character_sheets', True):
            suggestions.append("Consider including character design sheets for artist reference")
        
        if not format_options.get('include_panel_layouts', True):
            suggestions.append("Consider including panel layout guides for better page composition")
        
        # Check export formats
        export_formats = format_options.get('export_formats', [])
        if 'pdf' not in export_formats:
            suggestions.append("Consider adding PDF export for professional distribution")
        
        # Check production notes
        formatted_outputs = artifact.get('formatted_outputs', {})
        if 'production_notes' in formatted_outputs:
            prod_notes = formatted_outputs['production_notes']
            compliance = prod_notes.get('industry_compliance', {})
            
            if compliance.get('panel_density') == 'REVIEW NEEDED':
                suggestions.append("Review panel density - some pages may be too crowded")
            
            if compliance.get('word_density') == 'REVIEW NEEDED':
                suggestions.append("Review dialogue density - some panels may have too much text")
        
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
    validator = Step12Validator()
    
    # Test with minimal valid artifact
    test_artifact = {
        "metadata": {
            "step": 12,
            "step_name": "comic_formatter", 
            "project_id": "test",
            "created_at": "2025-01-01T00:00:00",
            "version": "1.0.0",
            "source_step": 11,
            "format_type": "dc_style"
        },
        "format_options": {
            "script_format": "dc_style",
            "export_formats": ["txt"]
        },
        "formatted_outputs": {
            "professional_script": {
                "format_name": "Full Script (DC Style)",
                "description": "Test script",
                "script_content": [
                    "CHARACTER REFERENCE:",
                    "PAGE 1 (3 panels)",
                    "PANEL 1: Wide shot of city",
                    "  HERO (BALLOON): \"Test dialogue\""
                ]
            },
            "production_notes": {
                "format_name": "Production Notes",
                "description": "Test notes",
                "script_statistics": {
                    "total_pages": 1,
                    "total_panels": 1
                },
                "industry_compliance": {
                    "panel_density": "PASS",
                    "word_density": "PASS",
                    "format_standard": "DC_STYLE"
                }
            }
        },
        "export_info": {
            "formats_generated": ["txt"],
            "template_style": "professional",
            "total_pages": 1,
            "total_panels": 1
        }
    }
    
    is_valid, message = validator.validate(test_artifact)
    print(f"Validation result: {is_valid}")
    print(f"Message: {message}")