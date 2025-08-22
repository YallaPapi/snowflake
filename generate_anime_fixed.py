"""
Generate anime-style comic panels with FIXED dialogue bubbles
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
    """Generate anime-style comic panels"""
    
    print("GENERATING ANIME-STYLE COMIC PANELS (WITH FIXED DIALOGUE)")
    print("="*60)
    
    # Create anime-themed comic script
    step11_data = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "anime_fixed",
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
                        "description": "Wide shot of magical girl with pink hair in sailor uniform standing on Tokyo tower at sunset, cherry blossoms floating",
                        "dialogue": [
                            {"character": "Sakura", "type": "balloon", "text": "The Crystal of Eternia! It's real!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "magical",
                        "characters": ["Sakura"],
                        "word_count": 6
                    },
                    {
                        "panel_number": 2,
                        "description": "Close-up of magical girl's face with large sparkling anime eyes, emotional expression with speed lines",
                        "dialogue": [
                            {"character": "Sakura", "type": "thought", "text": "Finally found it!"}  # Simplified to avoid bubble issues
                        ],
                        "shot_type": "close_up",
                        "mood": "emotional",
                        "characters": ["Sakura"],
                        "word_count": 3
                    },
                    {
                        "panel_number": 3,
                        "description": "Dark magical rival appears in dramatic pose with flowing cape and glowing red eyes",
                        "dialogue": [
                            {"character": "Shadow", "type": "balloon", "text": "STOP RIGHT THERE!"},
                            {"character": "Sakura", "type": "balloon", "text": "No way!"}
                        ],
                        "shot_type": "dramatic_angle",
                        "mood": "confrontation",
                        "characters": ["Sakura", "Shadow"],
                        "word_count": 5
                    }
                ]
            }
        ]
    }
    
    # Anime character designs
    step7_data = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "anime_fixed"
        },
        "character_bibles": [
            {
                "name": "Sakura",
                "physical": {
                    "appearance": "Magical girl, pink twin-tail hair, sailor uniform, large anime eyes, holding magic wand"
                }
            },
            {
                "name": "Shadow",
                "physical": {
                    "appearance": "Dark magical girl rival, long black hair, gothic dress, red eyes, dark aura"
                }
            }
        ]
    }
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/anime_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to: {artifacts_dir}")
    print("\nStep 13: Generating anime-style panel art...")
    print("-"*60)
    
    # Initialize Step 13 with anime configuration
    step13 = Step13PanelArtGeneration(str(artifacts_dir))
    
    # Use anime-specific model from Replicate
    anime_config = {
        "provider": "replicate",
        "model": "sdxl",  # Base SDXL but with anime prompting
        "style": "custom",  # We'll use custom anime prompts
        "quality": "high",
        "generate_all": True,
        # Override the style in prompts
        "style_override": "anime art style, manga style, cel shaded, vibrant colors, big expressive eyes, detailed backgrounds, high quality anime, studio quality, professional anime art"
    }
    
    # Temporarily modify the prompts to be more anime-specific
    for page in step11_data["pages"]:
        for panel in page["panels"]:
            original_desc = panel["description"]
            panel["description"] = f"{original_desc}, anime style, manga art, cel shading, vibrant colors"
    
    # Run Step 13 with anime style
    success, step13_result, message = step13.execute(
        step11_artifact=step11_data,
        step7_artifact=step7_data,
        project_id="anime_fixed",
        generation_config=anime_config
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_13_panel_art.json", "w") as f:
            json.dump(step13_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 14: Adding dialogue bubbles (FIXED)...")
    print("-"*60)
    
    # Initialize Step 14
    step14 = Step14PanelComposition(str(artifacts_dir))
    
    # IMPORTANT: Restore original descriptions without anime keywords for clean dialogue
    step11_data["pages"][0]["panels"][0]["description"] = "Wide shot of magical girl with pink hair in sailor uniform standing on Tokyo tower at sunset, cherry blossoms floating"
    step11_data["pages"][0]["panels"][1]["description"] = "Close-up of magical girl's face with large sparkling anime eyes, emotional expression with speed lines"
    step11_data["pages"][0]["panels"][2]["description"] = "Dark magical rival appears in dramatic pose with flowing cape and glowing red eyes"
    
    # Run Step 14 with fixed dialogue
    success, step14_result, message = step14.execute(
        step13_artifact=step13_result,
        step11_artifact=step11_data,
        project_id="anime_fixed"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_14_panel_composition.json", "w") as f:
            json.dump(step14_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 15: Assembling anime comic...")
    print("-"*60)
    
    # Initialize Step 15
    step15 = Step15GraphicNovelAssembly(str(artifacts_dir))
    
    # Run Step 15
    success, step15_result, message = step15.execute(
        step14_artifact=step14_result,
        step11_artifact=step11_data,
        project_id="anime_fixed"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_15_anime_assembly.json", "w") as f:
            json.dump(step15_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\n" + "="*60)
    print("SUCCESS! YOUR ANIME PANELS ARE READY!")
    print("="*60)
    print(f"\nGENERATED FILES IN: {artifacts_dir.absolute()}")
    
    # Show file locations
    panels_dir = artifacts_dir / "anime_fixed" / "comic_panels"
    pages_dir = artifacts_dir / "anime_fixed" / "comic_pages"
    final_dir = artifacts_dir / "anime_fixed"
    
    print("\nANIME PANEL IMAGES:")
    if panels_dir.exists():
        for panel in sorted(panels_dir.glob("*.png")):
            print(f"  - {panel.name}")
    
    print("\nCOMPLETE PAGE:")
    if pages_dir.exists():
        for page in sorted(pages_dir.glob("*.png")):
            print(f"  - {page.name}")
    
    print("\nFINAL COMIC:")
    if final_dir.exists():
        for pdf in final_dir.glob("*.pdf"):
            print(f"  - {pdf.name}")
        for cbz in final_dir.glob("*.cbz"):
            print(f"  - {cbz.name}")
    
    print("\n[ANIME STYLE APPLIED]")
    print("The panels use anime/manga art style with:")
    print("  - Cel shading")
    print("  - Large expressive eyes")
    print("  - Vibrant colors")
    print("  - Manga-style composition")
    print("\n[DIALOGUE FIX APPLIED]")
    print("Panel 2 now has simplified text to avoid bubble duplication")

if __name__ == "__main__":
    main()