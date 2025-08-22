"""
Generate ACTUAL comic panels with images using Replicate API
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
    """Generate real comic panels with Replicate"""
    
    print("GENERATING ACTUAL COMIC PANELS WITH REPLICATE API")
    print("="*60)
    
    # Create comic script data
    step11_data = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "real_panels_demo",
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
                        "description": "A female archaeologist in explorer outfit discovers glowing blue crystal in ancient temple",
                        "dialogue": [
                            {"character": "Maya", "type": "balloon", "text": "The Crystal of Eternia! It's real!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "awe",
                        "characters": ["Maya"],
                        "word_count": 6
                    },
                    {
                        "panel_number": 2,
                        "description": "Close-up of Maya's excited face as she reaches for the floating crystal",
                        "dialogue": [
                            {"character": "Maya", "type": "thought", "text": "Years of searching... finally!"}
                        ],
                        "shot_type": "close_up",
                        "mood": "excited",
                        "characters": ["Maya"],
                        "word_count": 4
                    },
                    {
                        "panel_number": 3,
                        "description": "Massive stone guardian with glowing blue eyes awakens behind Maya",
                        "dialogue": [
                            {"character": "Guardian", "type": "balloon", "text": "WHO DARES DISTURB MY SLUMBER?"},
                            {"character": "Maya", "type": "balloon", "text": "Oh no!"}
                        ],
                        "shot_type": "dramatic_angle",
                        "mood": "danger",
                        "characters": ["Maya", "Guardian"],
                        "word_count": 8
                    }
                ]
            }
        ]
    }
    
    step12_data = {
        "metadata": {
            "step": 12,
            "step_name": "comic_formatter",
            "project_id": "real_panels_demo",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "formatted_script": step11_data["pages"],
        "total_pages": 1,
        "total_panels": 3,
        "panel_layout": {
            "page_1": {"layout": "3-panel-vertical"}
        }
    }
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/real_comic_panels_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to: {artifacts_dir}")
    print("\nStep 13: Generating panel art with Replicate...")
    print("-"*60)
    
    # Create minimal character bibles for Step 13
    step7_data = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "real_panels_demo"
        },
        "character_bibles": [
            {
                "name": "Maya",
                "physical": {
                    "appearance": "Female archaeologist, brown hair in ponytail, explorer outfit, backpack"
                }
            },
            {
                "name": "Guardian",
                "physical": {
                    "appearance": "Massive stone golem, glowing blue eyes, ancient carvings on body"
                }
            }
        ]
    }
    
    # Initialize Step 13
    step13 = Step13PanelArtGeneration(str(artifacts_dir))
    
    # Run Step 13 to generate actual images
    success, step13_result, message = step13.execute(
        step11_artifact=step11_data,
        step7_artifact=step7_data,
        project_id="real_panels_demo"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_13_panel_art.json", "w") as f:
            json.dump(step13_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 14: Composing panels with dialogue...")
    print("-"*60)
    
    # Initialize Step 14
    step14 = Step14PanelComposition(str(artifacts_dir))
    
    # Run Step 14 to add dialogue bubbles
    success, step14_result, message = step14.execute(
        step13_artifact=step13_result,
        step11_artifact=step11_data,
        project_id="real_panels_demo"
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
    
    # Run Step 15 to create final comic
    success, step15_result, message = step15.execute(
        step14_artifact=step14_result,
        step11_artifact=step11_data,
        project_id="real_panels_demo"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_15_graphic_novel_assembly.json", "w") as f:
            json.dump(step15_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\n" + "="*60)
    print("SUCCESS! YOUR COMIC PANELS ARE READY!")
    print("="*60)
    print(f"\nGENERATED FILES IN: {artifacts_dir.absolute()}")
    print("\nPANEL IMAGES:")
    
    # List generated panels
    panels_dir = artifacts_dir / "comic_panels"
    if panels_dir.exists():
        for panel_file in sorted(panels_dir.glob("*.png")):
            print(f"  - {panel_file.name}")
    
    print("\nCOMPLETE COMIC:")
    if (artifacts_dir / "The_Crystal_Guardian.pdf").exists():
        print(f"  - The_Crystal_Guardian.pdf")
    if (artifacts_dir / "The_Crystal_Guardian.cbz").exists():
        print(f"  - The_Crystal_Guardian.cbz")
    
    print("\nOpen the folder to see your generated comic panels with dialogue!")

if __name__ == "__main__":
    main()