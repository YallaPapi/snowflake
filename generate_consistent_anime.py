"""
Generate anime panels with CONSISTENT CHARACTERS across all panels
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Set the Replicate API token from environment variable
if 'REPLICATE_API_TOKEN' not in os.environ:
    print("Warning: REPLICATE_API_TOKEN environment variable not set")
    # Use placeholder - must be set before running
    os.environ['REPLICATE_API_TOKEN'] = 'YOUR_API_KEY_HERE'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.steps.step_13_panel_art_generation import Step13PanelArtGeneration
from pipeline.steps.step_14_panel_composition import Step14PanelComposition
from pipeline.steps.step_15_graphic_novel_assembly import Step15GraphicNovelAssembly

def main():
    """Generate anime panels with consistent characters"""
    
    print("GENERATING ANIME PANELS WITH CONSISTENT CHARACTERS")
    print("="*60)
    
    # Create detailed character descriptions for consistency
    step11_data = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "consistent_anime",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "script_format": "full_script",
        "total_pages": 1,
        "total_panels": 3,
        "pages": [
            {
                "page_number": 1,
                "scene_index": 0,
                "panel_count": 3,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "Wide shot of Sakura the magical girl standing on Tokyo Tower at sunset",
                        "dialogue": [
                            {"character": "Sakura", "type": "balloon", "text": "The Crystal of Eternia!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "magical",
                        "characters": ["Sakura"],
                        "word_count": 4
                    },
                    {
                        "panel_number": 2,
                        "description": "Close-up of Sakura's face showing determination",
                        "dialogue": [
                            {"character": "Sakura", "type": "thought", "text": "I found it!"}
                        ],
                        "shot_type": "close_up",
                        "mood": "determined",
                        "characters": ["Sakura"],
                        "word_count": 3
                    },
                    {
                        "panel_number": 3,
                        "description": "Sakura facing her rival Shadow in confrontation",
                        "dialogue": [
                            {"character": "Shadow", "type": "balloon", "text": "Stop!"},
                            {"character": "Sakura", "type": "balloon", "text": "Never!"}
                        ],
                        "shot_type": "medium_shot",
                        "mood": "confrontation",
                        "characters": ["Sakura", "Shadow"],
                        "word_count": 2
                    }
                ]
            }
        ]
    }
    
    # VERY DETAILED character bibles for maximum consistency
    step7_data = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "consistent_anime"
        },
        "character_bibles": [
            {
                "name": "Sakura",
                "role": "protagonist",
                "physical": {
                    "age": "16",
                    "face_shape": "heart-shaped",
                    "eye_color": "bright green",
                    "eye_shape": "large round anime eyes",
                    "hair_color": "pink",
                    "hair_style": "long twin-tails with ribbons",
                    "height": "5'3\"",
                    "build": "petite",
                    "skin_tone": "fair",
                    "outfit": "white and pink sailor uniform with red bow, pleated skirt, white boots",
                    "accessories": "golden star hairpin, magical wand with crystal",
                    "distinguishing_features": "star-shaped birthmark on left cheek",
                    "appearance": "Sakura is a 16-year-old magical girl with bright green large anime eyes, long pink hair in twin-tails with red ribbons, wearing a white and pink sailor uniform with red bow, white boots, and carrying a crystal-topped magical wand"
                }
            },
            {
                "name": "Shadow",
                "role": "antagonist",
                "physical": {
                    "age": "17",
                    "face_shape": "angular",
                    "eye_color": "crimson red",
                    "eye_shape": "narrow sharp anime eyes",
                    "hair_color": "black with purple highlights",
                    "hair_style": "long straight hair reaching waist",
                    "height": "5'6\"",
                    "build": "slender",
                    "skin_tone": "pale",
                    "outfit": "black gothic dress with purple trim, cape, thigh-high boots",
                    "accessories": "silver moon tiara, dark crystal pendant",
                    "distinguishing_features": "crescent moon marking on forehead",
                    "appearance": "Shadow is a 17-year-old dark magical girl with crimson red narrow eyes, long straight black hair with purple highlights, wearing a black gothic dress with cape and thigh-high boots, silver moon tiara"
                }
            }
        ]
    }
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/consistent_anime_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to: {artifacts_dir}")
    print("\nStep 13: Generating panels with CONSISTENT characters...")
    print("-"*60)
    
    # Initialize Step 13
    step13 = Step13PanelArtGeneration(str(artifacts_dir))
    
    # Configuration for character consistency
    generation_config = {
        "provider": "replicate",
        "model": "sdxl",
        "style": "anime",
        "quality": "high",
        "generate_all": True,
        # The fixed code will now use character-specific seeds automatically
        # Each character will maintain the same seed across all panels
    }
    
    # Run Step 13 with character consistency
    success, step13_result, message = step13.execute(
        step11_artifact=step11_data,
        step7_artifact=step7_data,
        project_id="consistent_anime",
        generation_config=generation_config
    )
    
    if success:
        print(f"[OK] {message}")
        print("\nCharacter seeds used:")
        if "character_seeds" in step13_result:
            for char, seed in step13_result["character_seeds"].items():
                print(f"  - {char}: {seed}")
        with open(artifacts_dir / "step_13_panel_art.json", "w") as f:
            json.dump(step13_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 14: Adding dialogue...")
    print("-"*60)
    
    # Initialize Step 14
    step14 = Step14PanelComposition(str(artifacts_dir))
    
    # Run Step 14
    success, step14_result, message = step14.execute(
        step13_artifact=step13_result,
        step11_artifact=step11_data,
        project_id="consistent_anime"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_14_panel_composition.json", "w") as f:
            json.dump(step14_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 15: Assembling final comic...")
    print("-"*60)
    
    # Initialize Step 15
    step15 = Step15GraphicNovelAssembly(str(artifacts_dir))
    
    # Run Step 15
    success, step15_result, message = step15.execute(
        step14_artifact=step14_result,
        step11_artifact=step11_data,
        project_id="consistent_anime"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_15_assembly.json", "w") as f:
            json.dump(step15_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\n" + "="*60)
    print("SUCCESS! CONSISTENT CHARACTER PANELS READY!")
    print("="*60)
    print(f"\nFILES IN: {artifacts_dir.absolute()}")
    
    # Show generated files
    project_dir = artifacts_dir / "consistent_anime"
    if project_dir.exists():
        panels_dir = project_dir / "comic_panels"
        if panels_dir.exists():
            print("\nPANELS:")
            for panel in sorted(panels_dir.glob("*.png")):
                print(f"  - {panel.name}")
        
        print("\nCOMPLETE COMIC:")
        for pdf in project_dir.glob("*.pdf"):
            print(f"  - {pdf.name}")
    
    print("\n[CHARACTER CONSISTENCY IMPROVEMENTS]")
    print("- Each character uses a unique consistent seed")
    print("- Detailed physical descriptions maintained")
    print("- Character names emphasized in prompts")
    print("- Sakura will look the same across all panels")
    print("- Shadow will maintain consistent appearance")

if __name__ == "__main__":
    main()