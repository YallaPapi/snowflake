"""
Step 14 Validator: Panel Composition
Validates composed comic pages with lettering
"""

from typing import Tuple, List, Dict, Any

class Step14Validator:
    """Validator for Step 14: Panel Composition"""
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 14 panel composition artifact
        
        Args:
            artifact: The composed pages artifact to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check metadata
        if 'metadata' not in artifact:
            errors.append("MISSING: metadata section required")
        else:
            metadata = artifact['metadata']
            required_meta = ['step', 'step_name', 'project_id', 'created_at', 'version']
            for field in required_meta:
                if field not in metadata:
                    errors.append(f"MISSING: metadata.{field} required")
            
            if metadata.get('step') != 14:
                errors.append("INVALID: metadata.step must be 14")
            
            if metadata.get('step_name') != 'panel_composition':
                errors.append("INVALID: metadata.step_name must be 'panel_composition'")
        
        # Check composition config
        if 'composition_config' not in artifact:
            errors.append("MISSING: composition_config required")
        else:
            config = artifact['composition_config']
            if 'layout' not in config:
                errors.append("MISSING: composition_config.layout required")
        
        # Check pages
        if 'pages' not in artifact:
            errors.append("MISSING: pages array required")
        else:
            pages = artifact['pages']
            if not isinstance(pages, list):
                errors.append("INVALID: pages must be an array")
            elif len(pages) == 0:
                errors.append("EMPTY: at least one page must be composed")
            else:
                # Validate each page
                for idx, page in enumerate(pages):
                    page_errors = self._validate_page(page, idx)
                    errors.extend(page_errors)
        
        # Check statistics
        if 'statistics' not in artifact:
            errors.append("MISSING: statistics section required")
        else:
            stats = artifact['statistics']
            required_stats = ['total_pages', 'total_panels', 'layout_used']
            for field in required_stats:
                if field not in stats:
                    errors.append(f"MISSING: statistics.{field} required")
        
        return len(errors) == 0, errors
    
    def _validate_page(self, page: Dict[str, Any], idx: int) -> List[str]:
        """Validate individual composed page"""
        errors = []
        
        # Required fields
        required_fields = ['page_number', 'panel_count', 'layout_used']
        for field in required_fields:
            if field not in page:
                errors.append(f"MISSING: pages[{idx}].{field} required")
        
        # Validate page number
        if 'page_number' in page:
            if not isinstance(page['page_number'], int) or page['page_number'] < 1:
                errors.append(f"INVALID: pages[{idx}].page_number must be positive integer")
        
        # Validate panel count
        if 'panel_count' in page:
            if not isinstance(page['panel_count'], int) or page['panel_count'] < 1:
                errors.append(f"INVALID: pages[{idx}].panel_count must be positive integer")
            elif page['panel_count'] > 9:
                errors.append(f"WARNING: pages[{idx}].panel_count exceeds recommended maximum of 9")
        
        # Validate image data or file path
        if 'image_data' in page:
            image_data = page['image_data']
            if not isinstance(image_data, dict):
                errors.append(f"INVALID: pages[{idx}].image_data must be a dictionary")
            else:
                # Must have format
                if 'format' not in image_data:
                    errors.append(f"MISSING: pages[{idx}].image_data.format required")
                
                # Must have either base64 or file path
                if not any(k in image_data for k in ['base64', 'file_path']):
                    errors.append(f"MISSING: pages[{idx}].image_data must have base64 or file_path")
        elif 'file_path' not in page:
            errors.append(f"MISSING: pages[{idx}] must have image_data or file_path")
        
        # Validate layout
        if 'layout_used' in page:
            valid_layouts = ['standard', 'manga', 'webcomic', 'square']
            if page['layout_used'] not in valid_layouts:
                errors.append(f"INVALID: pages[{idx}].layout_used must be one of {valid_layouts}")
        
        # Validate dimensions if present
        if 'dimensions' in page:
            if not isinstance(page['dimensions'], str) or 'x' not in page['dimensions']:
                errors.append(f"INVALID: pages[{idx}].dimensions should be format 'WIDTHxHEIGHT'")
        
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
                suggestions.append("Add required metadata fields with step=14")
            elif "composition_config" in error:
                suggestions.append("Include composition_config with layout specification")
            elif "pages" in error and "array" in error:
                suggestions.append("Ensure pages is an array of page objects")
            elif "page_number" in error:
                suggestions.append("Each page must have a positive page_number")
            elif "panel_count" in error:
                suggestions.append("Include panel_count for each page (1-9 recommended)")
            elif "image_data" in error:
                suggestions.append("Each page must have image_data with format and content")
            elif "statistics" in error:
                suggestions.append("Add statistics section with page and panel counts")
            elif "layout_used" in error:
                suggestions.append("Specify layout: standard, manga, webcomic, or square")
            else:
                suggestions.append(f"Fix issue: {error}")
        
        return suggestions