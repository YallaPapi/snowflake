"""
Simple test for graphic novel pipeline without actual image generation
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.steps.step_11_manuscript_to_script import Step11ManuscriptToScript
from pipeline.steps.step_12_comic_formatter import Step12ComicFormatter
from pipeline.validators.step_11_validator import Step11Validator
from pipeline.validators.step_12_validator import Step12Validator

def create_test_manuscript():
    """Create a minimal test manuscript (Step 10 output)"""
    return {
        "metadata": {
            "step": 10,
            "step_name": "first_draft",
            "project_id": "test_graphic_novel",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "manuscript": {
            "title": "Cyberpunk Test Story",
            "author": "Test Author",
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Beginning",
                    "scenes": [
                        {
                            "scene_index": 0,
                            "content": "The neon lights of Neo-Tokyo cast long shadows across the rain-slicked streets. Zara stood on the rooftop, her cybernetic eye scanning the city below. 'The city never sleeps,' she muttered, 'and neither do I.' A movement in sector 7 caught her attention. Without hesitation, she activated her rocket boots and leaped into the void between buildings.",
                            "word_count": 52
                        }
                    ],
                    "word_count": 52
                }
            ],
            "total_word_count": 52
        }
    }

def create_test_character_bibles():
    """Create minimal character bibles (Step 7 output)"""
    return {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "test_graphic_novel",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "character_bibles": [
            {
                "name": "Zara",
                "role": "protagonist",
                "physical": {
                    "age": "25",
                    "height": "5'7\"",
                    "build": "Athletic",
                    "hair": "Purple, short",
                    "eyes": "One natural brown, one cybernetic blue",
                    "distinguishing_features": "Cybernetic eye, tech suit"
                },
                "personality": {
                    "traits": ["Determined", "Vigilant", "Solitary"],
                    "strengths": ["Tech-savvy", "Athletic", "Observant"],
                    "weaknesses": ["Insomnia", "Trust issues"]
                }
            },
            {
                "name": "Shadow",
                "role": "antagonist",
                "physical": {
                    "age": "Unknown",
                    "height": "6'0\"",
                    "build": "Lean",
                    "hair": "Hidden",
                    "eyes": "Unknown",
                    "distinguishing_features": "Black coat, always in shadows"
                },
                "personality": {
                    "traits": ["Mysterious", "Calculating", "Patient"],
                    "strengths": ["Strategic", "Invisible", "Manipulative"],
                    "weaknesses": ["Overconfident"]
                }
            }
        ]
    }

def test_steps_11_12():
    """Test Steps 11 and 12 of the pipeline"""
    
    # Create test data
    manuscript = create_test_manuscript()
    character_bibles = create_test_character_bibles()
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/graphic_novel_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print("Testing Graphic Novel Pipeline Steps 11-12")
    print("=" * 50)
    
    # Step 11: Convert manuscript to comic script
    print("\n📝 Step 11: Converting manuscript to comic script...")
    step11 = Step11ManuscriptToScript()
    step11_result = step11.run(
        step_10_manuscript=manuscript,
        step_7_character_bibles=character_bibles,
        project_id="test_graphic_novel"
    )
    
    # Validate Step 11
    validator11 = Step11Validator()
    is_valid, errors = validator11.validate(step11_result)
    
    if is_valid:
        print("✅ Step 11 completed successfully!")
        # Save artifact
        with open(artifacts_dir / "step_11_comic_script.json", "w") as f:
            json.dump(step11_result, f, indent=2)
    else:
        print("❌ Step 11 validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Step 12: Format comic script
    print("\n🎨 Step 12: Formatting comic script...")
    step12 = Step12ComicFormatter()
    step12_result = step12.run(
        step_11_script=step11_result,
        project_id="test_graphic_novel"
    )
    
    # Validate Step 12
    validator12 = Step12Validator()
    is_valid, errors = validator12.validate(step12_result)
    
    if is_valid:
        print("✅ Step 12 completed successfully!")
        # Save artifact
        with open(artifacts_dir / "step_12_formatted_script.json", "w") as f:
            json.dump(step12_result, f, indent=2)
    else:
        print("❌ Step 12 validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Pipeline Summary:")
    print(f"  - Total pages: {step12_result.get('total_pages', 0)}")
    print(f"  - Total panels: {step12_result.get('total_panels', 0)}")
    print(f"  - Artifacts saved to: {artifacts_dir}")
    
    return True

if __name__ == "__main__":
    success = test_steps_11_12()
    if success:
        print("\n✨ Graphic novel pipeline test completed successfully!")
    else:
        print("\n❌ Graphic novel pipeline test failed.")
        sys.exit(1)