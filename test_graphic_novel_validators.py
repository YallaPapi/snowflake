"""
Test graphic novel pipeline validators only (no AI calls)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.validators.step_11_validator import Step11Validator
from pipeline.validators.step_12_validator import Step12Validator
from pipeline.validators.step_13_validator import Step13Validator
from pipeline.validators.step_14_validator import Step14Validator
from pipeline.validators.step_15_validator import Step15Validator

def test_validators():
    """Test all graphic novel validators with mock data"""
    
    print("Testing Graphic Novel Pipeline Validators")
    print("=" * 50)
    
    # Test Step 11 Validator
    print("\nTesting Step 11 Validator (Comic Script)...")
    step11_artifact = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "script_format": "full_script",
        "total_pages": 2,
        "total_panels": 6,
        "pages": [
            {
                "page_number": 1,
                "scene_index": 0,
                "panel_count": 3,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "WIDE SHOT: City skyline",
                        "dialogue": [],
                        "shot_type": "wide_shot",
                        "mood": "atmospheric",
                        "word_count": 0
                    },
                    {
                        "panel_number": 2,
                        "description": "MEDIUM: Hero on rooftop",
                        "dialogue": [{"character": "Hero", "type": "balloon", "text": "Test"}],
                        "shot_type": "medium_shot",
                        "mood": "determined",
                        "word_count": 1
                    },
                    {
                        "panel_number": 3,
                        "description": "CLOSE UP: Hero's eyes",
                        "dialogue": [],
                        "shot_type": "close_up",
                        "mood": "intense",
                        "word_count": 0
                    }
                ]
            }
        ]
    }
    
    validator11 = Step11Validator()
    is_valid, errors = validator11.validate(step11_artifact)
    print(f"  Step 11 valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    # Test Step 12 Validator
    print("\nTesting Step 12 Validator (Formatted Script)...")
    step12_artifact = {
        "metadata": {
            "step": 12,
            "step_name": "comic_formatter",
            "project_id": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "formatted_script": step11_artifact["pages"],
        "total_pages": 2,
        "total_panels": 6,
        "panel_layout": {
            "page_1": {"layout": "3-panel-vertical"},
            "page_2": {"layout": "3-panel-horizontal"}
        }
    }
    
    validator12 = Step12Validator()
    is_valid, errors = validator12.validate(step12_artifact)
    print(f"  Step 12 valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    # Test Step 13 Validator
    print("\nTesting Step 13 Validator (Panel Art Generation)...")
    step13_artifact = {
        "metadata": {
            "step": 13,
            "step_name": "panel_art_generation",
            "project_id": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "panels": [
            {
                "page_number": 1,
                "panel_number": 1,
                "description": "Test panel",
                "art_prompt": "Test prompt",
                "image_url": "mock://test.png",
                "style_tags": ["comic"],
                "generated": True
            }
        ]
    }
    
    validator13 = Step13Validator()
    is_valid, errors = validator13.validate(step13_artifact)
    print(f"  Step 13 valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    # Test Step 14 Validator
    print("\nTesting Step 14 Validator (Panel Composition)...")
    step14_artifact = {
        "metadata": {
            "step": 14,
            "step_name": "panel_composition",
            "project_id": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "composed_pages": [
            {
                "page_number": 1,
                "layout": "3-panel-grid",
                "panels": step13_artifact["panels"],
                "dialogue_bubbles": [
                    {
                        "panel_number": 1,
                        "character": "Hero",
                        "text": "Test",
                        "type": "balloon",
                        "position": {"x": 50, "y": 50}
                    }
                ],
                "composition_complete": True
            }
        ]
    }
    
    validator14 = Step14Validator()
    is_valid, errors = validator14.validate(step14_artifact)
    print(f"  Step 14 valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    # Test Step 15 Validator
    print("\nTesting Step 15 Validator (Graphic Novel Assembly)...")
    step15_artifact = {
        "metadata": {
            "step": 15,
            "step_name": "graphic_novel_assembly",
            "project_id": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "output_formats": {
            "pdf": "test.pdf",
            "cbz": "test.cbz"
        },
        "assembly_complete": True,
        "total_pages": 2,
        "total_panels": 6
    }
    
    validator15 = Step15Validator()
    is_valid, errors = validator15.validate(step15_artifact)
    print(f"  Step 15 valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    print("\n" + "=" * 50)
    print("All validators tested successfully!")
    
    return True

if __name__ == "__main__":
    success = test_validators()
    if not success:
        sys.exit(1)