"""
Generate comic panels in ANIME/MANGA style
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
    """Generate anime/manga style comic panels"""
    
    print("GENERATING ANIME/MANGA STYLE COMIC PANELS")
    print("="*60)
    
    # Create comic script data with anime-appropriate content
    step11_data = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "anime_panels",
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
                        "description": "Young female ninja with purple hair in traditional ninja outfit standing on rooftop at night, cherry blossoms in background",
                        "dialogue": [
                            {"character": "Sakura", "type": "balloon", "text": "The sacred scroll... I finally found it!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "determined",
                        "characters": ["Sakura"],
                        "word_count": 7
                    },
                    {
                        "panel_number": 2,
                        "description": "Close-up of Sakura's determined eyes with sparkles, dramatic anime expression",
                        "dialogue": [
                            {"character": "Sakura", "type": "thought", "text": "I won't let you down, sensei!"}
                        ],
                        "shot_type": "close_up",
                        "mood": "emotional",
                        "characters": ["Sakura"],
                        "word_count": 6
                    },
                    {
                        "panel_number": 3,
                        "description": "Dramatic action shot of rival ninja appearing in burst of smoke behind Sakura",
                        "dialogue": [
                            {"character": "Kuro", "type": "balloon", "text": "Not so fast, Sakura-chan!"},
                            {"character": "Sakura", "type": "balloon", "text": "Kuro?!"}
                        ],
                        "shot_type": "dramatic_angle",
                        "mood": "surprise",
                        "characters": ["Sakura", "Kuro"],
                        "word_count": 5
                    }
                ]
            }
        ]
    }
    
    # Character designs for anime style
    step7_data = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "anime_panels"
        },
        "character_bibles": [
            {
                "name": "Sakura",
                "physical": {
                    "appearance": "Young female ninja, long purple hair, big anime eyes, ninja outfit, kunai weapons"
                }
            },
            {
                "name": "Kuro",
                "physical": {
                    "appearance": "Male ninja rival, spiky black hair, red eyes, dark ninja outfit, mysterious"
                }
            }
        ]
    }
    
    # Create artifacts directory
    artifacts_dir = Path(f"artifacts/anime_panels_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to: {artifacts_dir}")
    print("\nStep 13: Generating anime-style panel art...")
    print("-"*60)
    
    # Initialize Step 13
    step13 = Step13PanelArtGeneration(str(artifacts_dir))
    
    # ANIME STYLE CONFIGURATION
    anime_config = {
        "provider": "replicate",
        "model": "sdxl",
        "style": "manga",  # This will use the manga style preset
        "quality": "high",
        "generate_all": True,
        # You could also override with custom style:
        # "custom_style": "anime art style, cel shaded, vibrant colors, big expressive eyes, Japanese animation, Studio Ghibli quality, detailed backgrounds, sakura petals"
    }
    
    # Run Step 13 with anime style
    success, step13_result, message = step13.execute(
        step11_artifact=step11_data,
        step7_artifact=step7_data,
        project_id="anime_panels",
        generation_config=anime_config
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_13_panel_art.json", "w") as f:
            json.dump(step13_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 14: Adding manga-style dialogue bubbles...")
    print("-"*60)
    
    # Initialize Step 14
    step14 = Step14PanelComposition(str(artifacts_dir))
    
    # Run Step 14
    success, step14_result, message = step14.execute(
        step13_artifact=step13_result,
        step11_artifact=step11_data,
        project_id="anime_panels"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_14_panel_composition.json", "w") as f:
            json.dump(step14_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\nStep 15: Assembling manga...")
    print("-"*60)
    
    # Initialize Step 15
    step15 = Step15GraphicNovelAssembly(str(artifacts_dir))
    
    # Run Step 15
    success, step15_result, message = step15.execute(
        step14_artifact=step14_result,
        step11_artifact=step11_data,
        project_id="anime_panels"
    )
    
    if success:
        print(f"[OK] {message}")
        with open(artifacts_dir / "step_15_manga_assembly.json", "w") as f:
            json.dump(step15_result, f, indent=2)
    else:
        print(f"[FAILED] {message}")
        return
    
    print("\n" + "="*60)
    print("SUCCESS! YOUR ANIME/MANGA PANELS ARE READY!")
    print("="*60)
    print(f"\nGENERATED FILES IN: {artifacts_dir.absolute()}")
    print("\nANIME PANEL IMAGES:")
    
    # List generated panels
    panels_dir = artifacts_dir / "anime_panels" / "comic_panels"
    if panels_dir.exists():
        for panel_file in sorted(panels_dir.glob("*.png")):
            print(f"  - {panel_file.name}")
    
    print("\nCOMPLETE MANGA:")
    manga_dir = artifacts_dir / "anime_panels"
    if manga_dir.exists():
        for file in manga_dir.glob("*.pdf"):
            print(f"  - {file.name}")
        for file in manga_dir.glob("*.cbz"):
            print(f"  - {file.name}")
    
    print("\nStyle used: MANGA/ANIME")
    print("To use other styles, change the 'style' parameter to:")
    print("  - 'western' for Marvel/DC style")
    print("  - 'graphic_novel' for painterly realistic style")
    print("  - 'noir' for black & white dramatic style")
    print("  - Or add custom_style with your own prompt!")

if __name__ == "__main__":
    main()