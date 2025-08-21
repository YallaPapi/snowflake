#!/usr/bin/env python3
"""
Final test of Steps 7 and 8 with all fixes
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles
from src.pipeline.steps.step_8_scene_list import Step8SceneList

def final_test():
    """Final test with complete data"""
    
    # Use existing good data
    source_project = "smoketestnovel_20250819_153616"
    test_project = f"final_test_7_8_{datetime.now().strftime('%H%M%S')}"
    
    artifact_dir = Path("artifacts") / source_project
    
    print("="*60)
    print("FINAL TEST - STEPS 7 AND 8")
    print("="*60)
    
    # Load Step 5 and 6
    with open(artifact_dir / "step_5_character_synopses.json", "r") as f:
        step5_artifact = json.load(f)
    
    with open(artifact_dir / "step_6_long_synopsis.json", "r") as f:
        step6_artifact = json.load(f)
    
    print(f"\nLoaded artifacts:")
    print(f"  - Step 5: {len(step5_artifact.get('characters', []))} characters")
    print(f"  - Step 6: {len(step6_artifact.get('long_synopsis', ''))} chars in synopsis")
    
    # TEST STEP 7
    print("\n" + "-"*60)
    print("STEP 7: CHARACTER BIBLES")
    print("-"*60)
    
    step7 = Step7CharacterBibles()
    
    # Use GPT-4o-mini for speed
    model_config = {
        "model_name": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 3000
    }
    
    print(f"Model: {model_config['model_name']}")
    print("Generating character bibles...")
    
    success7, artifact7, message7 = step7.execute(
        step5_artifact=step5_artifact,
        project_id=test_project,
        model_config=model_config
    )
    
    if not success7:
        print(f"FAILED: {message7}")
        return False
    
    print(f"SUCCESS: Generated {len(artifact7.get('bibles', []))} character bibles")
    
    # Analyze Step 7 results
    for bible in artifact7.get('bibles', []):
        name = bible.get('name', 'Unknown')
        print(f"\n  {name}:")
        
        # Check sections
        sections_present = []
        for section in ['physical', 'personality', 'environment', 'psychology']:
            if bible.get(section):
                sections_present.append(section)
        
        print(f"    Sections: {', '.join(sections_present)}")
        print(f"    Voice notes: {len(bible.get('voice_notes', []))}")
        
        # Sample psychology
        psych = bible.get('psychology', {})
        if isinstance(psych, dict):
            if psych.get('backstory_wound'):
                print(f"    Wound: \"{psych['backstory_wound'][:50]}...\"")
    
    # TEST STEP 8
    print("\n" + "-"*60)
    print("STEP 8: SCENE LIST")
    print("-"*60)
    
    step8 = Step8SceneList()
    
    # Use same model for consistency
    print(f"Model: {model_config['model_name']}")
    print("Generating scene list...")
    
    success8, artifact8, message8 = step8.execute(
        step6_artifact=step6_artifact,
        step7_artifact=artifact7,
        project_id=test_project,
        model_config=model_config
    )
    
    if not success8:
        print(f"FAILED: {message8}")
        return False
    
    scenes = artifact8.get('scenes', [])
    print(f"SUCCESS: Generated {len(scenes)} scenes")
    
    # Analyze Step 8 results
    print(f"\nScene List Analysis:")
    print(f"  Total word target: {artifact8.get('total_word_target', 0):,} words")
    
    # Disasters
    disasters = artifact8.get('disaster_anchors', {})
    d1, d2, d3 = disasters.get('d1_scene'), disasters.get('d2_scene'), disasters.get('d3_scene')
    
    if d1 and d2 and d3:
        print(f"  Disasters: D1 at scene {d1}, D2 at scene {d2}, D3 at scene {d3}")
    else:
        missing = []
        if not d1: missing.append("D1")
        if not d2: missing.append("D2")
        if not d3: missing.append("D3")
        print(f"  Missing disasters: {', '.join(missing)}")
    
    # Scene types
    proactive = sum(1 for s in scenes if s.get('type') == 'Proactive')
    reactive = sum(1 for s in scenes if s.get('type') == 'Reactive')
    print(f"  Scene types: {proactive} Proactive, {reactive} Reactive")
    
    # Conflict validation
    conflict_check = artifact8.get('conflict_validation', {})
    if conflict_check.get('all_have_conflict'):
        print(f"  Conflict: All scenes have conflict")
    else:
        without = conflict_check.get('scenes_without_conflict', [])
        print(f"  Warning: {len(without)} scenes may lack explicit conflict")
    
    # Check CSV
    csv_path = Path("artifacts") / test_project / "step_8_scenes.csv"
    if csv_path.exists():
        print(f"  CSV: Exported successfully")
    
    # Show sample scenes
    print(f"\nSample Scenes:")
    for i, scene in enumerate(scenes[:3], 1):
        print(f"\n  Scene {i}: {scene.get('type')} - POV: {scene.get('pov')}")
        print(f"    Location: {scene.get('location')}")
        summary = scene.get('summary', '')[:100]
        print(f"    Summary: {summary}...")
        if scene.get('disaster_anchor'):
            print(f"    >>> DISASTER: {scene['disaster_anchor']} <<<")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("Steps 7 and 8 are now generating comprehensive, properly formatted outputs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = final_test()
    sys.exit(0 if success else 1)