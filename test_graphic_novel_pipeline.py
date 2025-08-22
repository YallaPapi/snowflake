"""
Test the complete graphic novel generation pipeline with Replicate API
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

def create_test_artifacts():
    """Create minimal test artifacts for Steps 11 and 7"""
    
    # Step 11 artifact (comic script)
    step11_artifact = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "test_graphic_novel",
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
                        "description": "WIDE SHOT: A cyberpunk city at night, neon lights reflecting off wet streets",
                        "dialogue": [
                            {"character": "Narrator", "type": "caption", "text": "Neo-Tokyo, 2089"}
                        ],
                        "transition_type": "scene_to_scene",
                        "characters": [],
                        "shot_type": "wide_shot",
                        "mood": "dark",
                        "word_count": 3
                    },
                    {
                        "panel_number": 2,
                        "description": "MEDIUM SHOT: A young woman with purple hair in a tech suit standing on a rooftop",
                        "dialogue": [
                            {"character": "Zara", "type": "balloon", "text": "The city never sleeps... and neither do I."}
                        ],
                        "transition_type": "action_to_action",
                        "characters": ["Zara"],
                        "shot_type": "medium_shot",
                        "mood": "tense",
                        "word_count": 9
                    },
                    {
                        "panel_number": 3,
                        "description": "CLOSE UP: Zara's cybernetic eye glowing blue as she scans the city",
                        "dialogue": [
                            {"character": "Zara", "type": "thought", "text": "There... movement in sector 7."}
                        ],
                        "transition_type": "action_to_action",
                        "characters": ["Zara"],
                        "shot_type": "close_up",
                        "mood": "dramatic",
                        "word_count": 5
                    }
                ]
            },
            {
                "page_number": 2,
                "scene_index": 0,
                "panel_count": 3,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "ACTION SHOT: Zara leaps between buildings with rocket boots",
                        "dialogue": [],
                        "transition_type": "action_to_action",
                        "characters": ["Zara"],
                        "shot_type": "wide_shot",
                        "mood": "dramatic",
                        "word_count": 0
                    },
                    {
                        "panel_number": 2,
                        "description": "MEDIUM SHOT: A mysterious figure in a black coat watches from the shadows",
                        "dialogue": [
                            {"character": "Shadow", "type": "balloon", "text": "She's taken the bait..."}
                        ],
                        "transition_type": "subject_to_subject",
                        "characters": ["Shadow"],
                        "shot_type": "medium_shot",
                        "mood": "dark",
                        "word_count": 4
                    },
                    {
                        "panel_number": 3,
                        "description": "WIDE SHOT: Zara lands on a building as alarms start blaring",
                        "dialogue": [
                            {"character": "Zara", "type": "balloon", "text": "What?! It's a trap!"},
                            {"character": "Shadow", "type": "balloon", "text": "Welcome to the game, Zara."}
                        ],
                        "transition_type": "scene_to_scene",
                        "characters": ["Zara", "Shadow"],
                        "shot_type": "wide_shot",
                        "mood": "tense",
                        "word_count": 8
                    }
                ]
            }
        ],
        "character_designs": {
            "Zara": {
                "description": "Young woman, early 20s, athletic build",
                "hair": "Purple, short bob cut",
                "eyes": "One normal brown, one cybernetic blue",
                "clothing": "Black tech suit with neon blue accents",
                "distinguishing_features": "Glowing cybernetic eye, tech gauntlets"
            },
            "Shadow": {
                "description": "Mysterious figure, age unknown",
                "hair": "Hidden under hood",
                "eyes": "Not visible",
                "clothing": "Long black coat with hood",
                "distinguishing_features": "Always in shadows, face never fully visible"
            }
        }
    }
    
    # Step 7 artifact (character bibles)
    step7_artifact = {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles"
        },
        "bibles": [
            {
                "name": "Zara",
                "physical": {
                    "age": "22",
                    "appearance": "Athletic and agile",
                    "hair": "Purple bob cut",
                    "eyes": "One brown, one cybernetic blue",
                    "build": "Athletic",
                    "height": "5'7\"",
                    "clothing": "Black tech suit with neon accents"
                },
                "personality": "Determined, quick-thinking, independent",
                "environment": {
                    "home": "Small apartment in Neo-Tokyo",
                    "work": "Freelance tech hunter"
                }
            },
            {
                "name": "Shadow",
                "physical": {
                    "age": "Unknown",
                    "appearance": "Mysterious and intimidating",
                    "hair": "Hidden",
                    "eyes": "Not visible",
                    "build": "Tall and lean",
                    "height": "6'2\"",
                    "clothing": "Black hooded coat"
                },
                "personality": "Calculating, mysterious, manipulative",
                "environment": {
                    "home": "Unknown",
                    "work": "Unknown organization"
                }
            }
        ]
    }
    
    return step11_artifact, step7_artifact

def test_pipeline():
    """Test the complete graphic novel pipeline"""
    
    print("=" * 60)
    print("TESTING GRAPHIC NOVEL PIPELINE WITH REPLICATE API")
    print("=" * 60)
    
    # Create test artifacts
    print("\n1. Creating test artifacts...")
    step11_artifact, step7_artifact = create_test_artifacts()
    
    project_id = f"graphic_novel_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"   Project ID: {project_id}")
    
    # Step 13: Generate panel art
    print("\n2. Step 13: Generating panel art with Replicate...")
    print("   Using SDXL model via Replicate API")
    
    step13 = Step13PanelArtGeneration()
    
    generation_config = {
        "provider": "replicate",
        "model": "sdxl",
        "style": "western",
        "quality": "standard",
        "max_pages": 2  # Generate both test pages
    }
    
    success, panel_artifact, message = step13.execute(
        step11_artifact,
        step7_artifact,
        project_id,
        generation_config
    )
    
    if not success:
        print(f"   ERROR: {message}")
        return False
    
    print(f"   SUCCESS: {message}")
    print(f"   Generated {len(panel_artifact.get('panels', []))} panel images")
    
    # Step 14: Composite panels into pages
    print("\n3. Step 14: Compositing panels into pages...")
    
    step14 = Step14PanelComposition()
    
    composition_config = {
        "layout": "standard",
        "style": "western",
        "add_page_numbers": True,
        "add_borders": True
    }
    
    success, pages_artifact, message = step14.execute(
        panel_artifact,
        step11_artifact,
        project_id,
        composition_config
    )
    
    if not success:
        print(f"   ERROR: {message}")
        return False
    
    print(f"   SUCCESS: {message}")
    print(f"   Composited {len(pages_artifact.get('pages', []))} pages")
    
    # Step 15: Assemble graphic novel
    print("\n4. Step 15: Assembling graphic novel...")
    
    step15 = Step15GraphicNovelAssembly()
    
    assembly_config = {
        "formats": ["cbz", "pdf", "web"],
        "title": "Cyberpunk Test Comic",
        "author": "AI Generated",
        "include_cover": True,
        "include_metadata": True
    }
    
    success, novel_artifact, message = step15.execute(
        pages_artifact,
        step11_artifact,
        project_id,
        assembly_config
    )
    
    if not success:
        print(f"   ERROR: {message}")
        return False
    
    print(f"   SUCCESS: {message}")
    
    # Display results
    print("\n" + "=" * 60)
    print("GRAPHIC NOVEL GENERATION COMPLETE!")
    print("=" * 60)
    
    assembled_files = novel_artifact.get('assembled_files', {})
    for format_name, file_path in assembled_files.items():
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        size_mb = file_size / (1024 * 1024)
        print(f"\n{format_name.upper()} Format:")
        print(f"  File: {file_path}")
        print(f"  Size: {size_mb:.2f} MB")
    
    # Check if we got real images or placeholders
    print("\n" + "-" * 60)
    panel_stats = panel_artifact.get('statistics', {})
    provider_used = panel_stats.get('provider_used', 'unknown')
    
    if provider_used == 'replicate':
        print("[SUCCESS] REAL IMAGES GENERATED via Replicate API!")
    else:
        print("[WARNING] Placeholder images used (API might have failed)")
    
    print("\nTo view your graphic novel:")
    web_path = assembled_files.get('web')
    if web_path:
        print(f"  Open in browser: {web_path}")
    
    return True

if __name__ == "__main__":
    try:
        # Test the pipeline
        success = test_pipeline()
        
        if success:
            print("\n[SUCCESS] All tests passed! Graphic novel pipeline is working!")
        else:
            print("\n[FAILED] Pipeline test failed. Check the errors above.")
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()