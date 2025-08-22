"""
Step 15 Validator: Graphic Novel Assembly
Validates assembled graphic novel files
"""

from typing import Tuple, List, Dict, Any
import os

class Step15Validator:
    """Validator for Step 15: Graphic Novel Assembly"""
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 15 graphic novel assembly artifact
        
        Args:
            artifact: The assembly artifact to validate
            
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
            
            if metadata.get('step') != 15:
                errors.append("INVALID: metadata.step must be 15")
            
            if metadata.get('step_name') != 'graphic_novel_assembly':
                errors.append("INVALID: metadata.step_name must be 'graphic_novel_assembly'")
        
        # Check novel metadata
        if 'novel_metadata' not in artifact:
            errors.append("MISSING: novel_metadata required")
        else:
            novel_meta = artifact['novel_metadata']
            required_fields = ['title', 'author', 'total_pages']
            for field in required_fields:
                if field not in novel_meta:
                    errors.append(f"MISSING: novel_metadata.{field} required")
        
        # Check assembly config
        if 'assembly_config' not in artifact:
            errors.append("MISSING: assembly_config required")
        else:
            config = artifact['assembly_config']
            if 'formats' not in config or not config['formats']:
                errors.append("MISSING: assembly_config.formats must contain at least one format")
        
        # Check assembled files
        if 'assembled_files' not in artifact:
            errors.append("MISSING: assembled_files dictionary required")
        else:
            files = artifact['assembled_files']
            if not isinstance(files, dict):
                errors.append("INVALID: assembled_files must be a dictionary")
            elif len(files) == 0:
                errors.append("EMPTY: at least one file must be assembled")
            else:
                # Validate each file path
                for format_name, file_path in files.items():
                    if not isinstance(file_path, str):
                        errors.append(f"INVALID: assembled_files.{format_name} must be a file path string")
                    # Don't check file existence as it might be on a different system
        
        # Check statistics
        if 'statistics' not in artifact:
            errors.append("MISSING: statistics section required")
        else:
            stats = artifact['statistics']
            if 'formats_created' not in stats:
                errors.append("MISSING: statistics.formats_created required")
            if 'total_pages' not in stats:
                errors.append("MISSING: statistics.total_pages required")
        
        return len(errors) == 0, errors
    
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
            if "metadata" in error and "step" not in error:
                suggestions.append("Add required metadata fields with step=15")
            elif "novel_metadata" in error:
                suggestions.append("Include novel_metadata with title, author, and page count")
            elif "assembly_config" in error:
                suggestions.append("Specify assembly_config with formats list (cbz, pdf, epub, web)")
            elif "assembled_files" in error:
                suggestions.append("Include assembled_files dictionary with format->path mappings")
            elif "statistics" in error:
                suggestions.append("Add statistics with formats_created and total_pages")
            elif "formats" in error:
                suggestions.append("Specify at least one output format in assembly_config.formats")
            else:
                suggestions.append(f"Fix issue: {error}")
        
        return suggestions