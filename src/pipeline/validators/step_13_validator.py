"""
Step 13 Validator: Panel Art Generation
Validates generated comic panel images and metadata
"""

from typing import Tuple, List, Dict, Any

class Step13Validator:
    """Validator for Step 13: Panel Art Generation"""
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 13 panel art generation artifact
        
        Args:
            artifact: The panel art artifact to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check metadata
        if 'metadata' not in artifact:
            errors.append("MISSING: metadata section required")
        else:
            metadata = artifact['metadata']
            required_meta = ['step', 'step_name', 'project_id', 'created_at']
            for field in required_meta:
                if field not in metadata:
                    errors.append(f"MISSING: metadata.{field} required")
            
            if metadata.get('step') != 13:
                errors.append("INVALID: metadata.step must be 13")
            
            if metadata.get('step_name') != 'panel_art_generation':
                errors.append("INVALID: metadata.step_name must be 'panel_art_generation'")
        
        # Check generation config
        if 'generation_config' not in artifact:
            errors.append("MISSING: generation_config required")
        else:
            config = artifact['generation_config']
            if 'provider' not in config:
                errors.append("MISSING: generation_config.provider required")
            if 'style' not in config:
                errors.append("MISSING: generation_config.style required")
        
        # Check panels
        if 'panels' not in artifact:
            errors.append("MISSING: panels array required")
        else:
            panels = artifact['panels']
            if not isinstance(panels, list):
                errors.append("INVALID: panels must be an array")
            elif len(panels) == 0:
                errors.append("EMPTY: at least one panel must be generated")
            else:
                # Validate each panel
                for idx, panel in enumerate(panels):
                    panel_errors = self._validate_panel(panel, idx)
                    errors.extend(panel_errors)
        
        # Check statistics
        if 'statistics' not in artifact:
            errors.append("MISSING: statistics section required")
        else:
            stats = artifact['statistics']
            if 'total_panels_generated' not in stats:
                errors.append("MISSING: statistics.total_panels_generated required")
            if 'provider_used' not in stats:
                errors.append("MISSING: statistics.provider_used required")
        
        # Check character consistency data
        if 'character_seeds' not in artifact:
            errors.append("MISSING: character_seeds for consistency")
        
        return len(errors) == 0, errors
    
    def _validate_panel(self, panel: Dict[str, Any], idx: int) -> List[str]:
        """Validate individual panel data"""
        errors = []
        
        # Required fields
        required_fields = ['page', 'panel', 'prompt', 'image_data']
        for field in required_fields:
            if field not in panel:
                errors.append(f"MISSING: panels[{idx}].{field} required")
        
        # Validate image_data
        if 'image_data' in panel:
            image_data = panel['image_data']
            
            if not isinstance(image_data, dict):
                errors.append(f"INVALID: panels[{idx}].image_data must be a dictionary")
            else:
                # Check for required image data fields
                if 'type' not in image_data:
                    errors.append(f"MISSING: panels[{idx}].image_data.type required")
                
                if 'provider' not in image_data:
                    errors.append(f"MISSING: panels[{idx}].image_data.provider required")
                
                if 'format' not in image_data:
                    errors.append(f"MISSING: panels[{idx}].image_data.format required")
                
                # Must have either base64 or url or file_path
                if not any(k in image_data for k in ['base64', 'url', 'file_path']):
                    errors.append(f"MISSING: panels[{idx}].image_data must have base64, url, or file_path")
        
        # Validate metadata if present
        if 'metadata' in panel:
            meta = panel['metadata']
            if not isinstance(meta, dict):
                errors.append(f"INVALID: panels[{idx}].metadata must be a dictionary")
        
        # Validate prompt
        if 'prompt' in panel:
            if not isinstance(panel['prompt'], str) or len(panel['prompt']) < 10:
                errors.append(f"INVALID: panels[{idx}].prompt must be a descriptive string")
        
        return errors
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Generate fix suggestions for validation errors
        
        Args:
            errors: List of validation errors
            
        Returns:
            List of suggested fixes
        """
        suggestions = []
        
        for error in errors:
            if "metadata" in error:
                suggestions.append("Add required metadata fields with step=13")
            elif "generation_config" in error:
                suggestions.append("Include generation_config with provider and style")
            elif "panels" in error and "array" in error:
                suggestions.append("Ensure panels is an array of panel objects")
            elif "image_data" in error:
                suggestions.append("Each panel must have image_data with type, provider, and image content")
            elif "character_seeds" in error:
                suggestions.append("Include character_seeds dictionary for consistency tracking")
            elif "statistics" in error:
                suggestions.append("Add statistics section with generation metrics")
            elif "prompt" in error:
                suggestions.append("Include descriptive prompt used for image generation")
            else:
                suggestions.append(f"Fix issue: {error}")
        
        return suggestions