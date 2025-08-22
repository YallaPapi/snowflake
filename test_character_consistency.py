"""
Test script to verify character consistency improvements in Step 13
"""

import json
from pathlib import Path
from src.pipeline.steps.step_13_panel_art_generation import Step13PanelArtGeneration

def test_character_consistency():
    """Test that characters maintain consistent appearance across panels"""
    
    # Create test data with character descriptions
    step7_artifact = {
        "bibles": [
            {
                "name": "Sakura",
                "physical": {
                    "age": "17",
                    "gender": "female",
                    "hair": "long pink hair in twin tails",
                    "eyes": "bright green",
                    "build": "petite",
                    "face_shape": "heart-shaped",
                    "skin_tone": "fair",
                    "usual_clothing": "school uniform with red ribbon"
                },
                "personality": {
                    "traits": ["cheerful", "determined", "optimistic"]
                }
            },
            {
                "name": "Kenji",
                "physical": {
                    "age": "18",
                    "gender": "male",
                    "hair": "short black spiky",
                    "eyes": "dark brown",
                    "build": "athletic",
                    "face_shape": "angular",
                    "skin_tone": "light tan",
                    "usual_clothing": "casual t-shirt and jeans"
                },
                "personality": {
                    "traits": ["confident", "protective", "loyal"]
                }
            }
        ]
    }
    
    # Create test comic script with multiple panels featuring same characters
    step11_artifact = {
        "character_designs": {},
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "Sakura stands in the school courtyard looking determined",
                        "characters": ["Sakura"],
                        "mood": "determined",
                        "shot_type": "medium_shot"
                    },
                    {
                        "panel_number": 2,
                        "description": "Close-up of Sakura's face showing confidence",
                        "characters": ["Sakura"],
                        "mood": "confident",
                        "shot_type": "close_up"
                    },
                    {
                        "panel_number": 3,
                        "description": "Sakura and Kenji talking together",
                        "characters": ["Sakura", "Kenji"],
                        "mood": "neutral",
                        "shot_type": "medium_shot"
                    },
                    {
                        "panel_number": 4,
                        "description": "Wide shot of Sakura walking away",
                        "characters": ["Sakura"],
                        "mood": "dramatic",
                        "shot_type": "wide_shot"
                    }
                ]
            }
        ]
    }
    
    # Test configuration options
    configs = [
        {
            "name": "Standard SDXL with character seeds",
            "config": {
                "provider": "replicate",
                "model": "sdxl",
                "style": "manga",
                "generate_all": False,
                "max_pages": 1
            }
        },
        {
            "name": "Consistent Character Model",
            "config": {
                "provider": "replicate",
                "model": "sdxl",
                "style": "manga",
                "use_consistent_character": True,
                "generate_all": False,
                "max_pages": 1
            }
        }
    ]
    
    # Initialize Step 13
    step13 = Step13PanelArtGeneration(project_dir="test_artifacts")
    
    print("Testing Character Consistency Improvements")
    print("=" * 50)
    
    for test_config in configs:
        print(f"\nTest: {test_config['name']}")
        print("-" * 40)
        
        # Execute step 13
        success, artifact, message = step13.execute(
            step11_artifact=step11_artifact,
            step7_artifact=step7_artifact,
            project_id=f"consistency_test_{test_config['name'].replace(' ', '_').lower()}",
            generation_config=test_config['config']
        )
        
        if success:
            print(f"[SUCCESS] {message}")
            
            # Check character seeds were generated
            if 'character_seeds' in artifact:
                print(f"  Character seeds generated: {artifact['character_seeds']}")
            
            # Check that panels used correct seeds
            for panel in artifact.get('panels', []):
                if 'seed_used' in panel:
                    chars = panel['metadata'].get('characters', [])
                    print(f"  Panel {panel['panel']}: Characters {chars}, Seed: {panel.get('seed_used')}")
            
            # Save results for inspection
            results_path = Path(f"test_artifacts/consistency_test_{test_config['name'].replace(' ', '_').lower()}")
            results_path.mkdir(parents=True, exist_ok=True)
            
            with open(results_path / "test_results.json", 'w') as f:
                json.dump({
                    "config": test_config,
                    "character_designs": artifact.get('character_designs', {}),
                    "character_seeds": artifact.get('character_seeds', {}),
                    "panels_summary": [
                        {
                            "panel": p['panel'],
                            "characters": p['metadata'].get('characters', []),
                            "seed_used": p.get('seed_used'),
                            "prompt_excerpt": p['prompt'][:100] + "..."
                        }
                        for p in artifact.get('panels', [])
                    ]
                }, f, indent=2)
            
            print(f"  Results saved to {results_path}")
        else:
            print(f"[FAILED] {message}")
    
    print("\n" + "=" * 50)
    print("Character Consistency Test Complete")
    print("\nKey Improvements Implemented:")
    print("1. Character-specific seeds are now actually used for each panel")
    print("2. Seeds are deterministic based on character names")
    print("3. Multi-character panels use combined seeds")
    print("4. Enhanced character prompts with detailed physical descriptions")
    print("5. Character descriptions placed first in prompts for emphasis")
    print("6. Added negative prompts to prevent character morphing")
    print("7. Option to use fofr/consistent-character model for better results")
    print("\nTo use in production, set generation_config with:")
    print('  "use_consistent_character": True  # For best consistency')

if __name__ == "__main__":
    test_character_consistency()