"""
Generate a CLEAN, SIMPLE comic with just 2-3 panels that actually looks good
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Set the Replicate API token from environment variable
import os
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
    """Generate a clean, simple comic with just 2 panels"""
    
    print("GENERATING CLEAN SIMPLE COMIC - 2 PANELS ONLY")
    print("="*60)
    
    # SIMPLE script - just 2 panels, minimal dialogue
    step11_data = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "clean_comic",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "script_format": "full_script",
        "total_pages": 1,
        "total_panels": 2,  # JUST 2 PANELS
        "pages": [
            {
                "page_number": 1,
                "scene_index": 0,
                "panel_count": 2,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "A female warrior with red hair in armor holding a glowing sword",
                        "dialogue": [
                            {"character": "Aria", "type": "balloon", "text": "I found it!"}
                        ],
                        "shot_type": "medium_shot",
                        "mood": "triumphant",
                        "characters": ["Aria"],
                        "word_count": 3
                    },
                    {
                        "panel_number": 2,
                        "description": "The same red-haired warrior Aria facing a dragon",
                        "dialogue": [
                            {"character": "Dragon", "type": "balloon", "text": "FOOL!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "danger",
                        "characters": ["Aria", "Dragon"],
                        "word_count": 1
                    }
                ]
            }
        ]
    }
    
    # Simple character designs
    step7_data = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "clean_comic"
        },
        "character_bibles": [
            {
                "name": "Aria",
                "role": "protagonist",
                "physical": {
                    "appearance": "Female warrior, long red hair, silver armor, blue eyes, holding glowing sword"
                }
            },
            {
                "name": "Dragon",
                "role": "antagonist",
                "physical": {
                    "appearance": "Large black dragon with red eyes, wings spread, breathing fire"
                }
            }
        ]
    }
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/clean_comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to: {artifacts_dir}")
    print("\nStep 13: Generating 2 simple panels...")
    print("-"*60)
    
    # Initialize Step 13
    step13 = Step13PanelArtGeneration(str(artifacts_dir))
    
    # Simple configuration
    generation_config = {
        "provider": "replicate",
        "model": "sdxl",
        "style": "western",  # Back to western comic style
        "quality": "high",
        "generate_all": True
    }
    
    # Run Step 13
    success, step13_result, message = step13.execute(
        step11_artifact=step11_data,
        step7_artifact=step7_data,
        project_id="clean_comic",
        generation_config=generation_config
    )
    
    if success:
        print(f"[OK] {message}")
        if "character_seeds" in step13_result:
            for char, seed in step13_result["character_seeds"].items():
                print(f"  - {char}: {seed}")
        with open(artifacts_dir / "step_13_panel_art.json", "w") as f:
            json.dump(step13_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 14: Adding simple dialogue...")
    print("-"*60)
    
    # Initialize Step 14
    step14 = Step14PanelComposition(str(artifacts_dir))
    
    # Run Step 14
    success, step14_result, message = step14.execute(
        step13_artifact=step13_result,
        step11_artifact=step11_data,
        project_id="clean_comic"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_14_panel_composition.json", "w") as f:
            json.dump(step14_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 15: Assembling comic...")
    print("-"*60)
    
    # Initialize Step 15
    step15 = Step15GraphicNovelAssembly(str(artifacts_dir))
    
    # Run Step 15
    success, step15_result, message = step15.execute(
        step14_artifact=step14_result,
        step11_artifact=step11_data,
        project_id="clean_comic"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_15_assembly.json", "w") as f:
            json.dump(step15_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\n" + "="*60)
    print("DONE - CLEAN SIMPLE COMIC READY")
    print("="*60)
    print(f"\nFILES: {artifacts_dir.absolute()}")
    
    # Show generated files
    project_dir = artifacts_dir / "clean_comic"
    if project_dir.exists():
        panels_dir = project_dir / "comic_panels"
        if panels_dir.exists():
            print("\nPANELS (just 2):")
            for panel in sorted(panels_dir.glob("*.png")):
                print(f"  - {panel.name}")
        
        print("\nFINAL COMIC:")
        for pdf in project_dir.glob("*.pdf"):
            print(f"  - {pdf.name}")
    
    print("\n[CLEAN VERSION]")
    print("- Only 2 panels (not cluttered)")
    print("- Simple dialogue (short text)")
    print("- Western comic style (cleaner)")
    print("- Character consistency maintained")

if __name__ == "__main__":
    main()