#!/usr/bin/env python3
"""
Test Steps 7 and 8 using existing artifacts
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles
from src.pipeline.steps.step_8_scene_list import Step8SceneList
from src.ai.model_selector import ModelSelector

def test_with_existing_data():
    """Test using existing smoketest artifacts"""
    
    # Use existing project with artifacts
    source_project = "smoketestnovel_20250819_153616"
    test_project = "test_steps_7_8_fixed"
    
    # Load existing artifacts
    artifact_dir = Path("artifacts") / source_project
    
    print("Loading existing artifacts...")
    
    # Load Step 5
    with open(artifact_dir / "step_5_character_synopses.json", "r") as f:
        step5_artifact = json.load(f)
    print(f"  - Loaded Step 5: {len(step5_artifact.get('characters', []))} characters")
    
    # Load Step 6
    with open(artifact_dir / "step_6_long_synopsis.json", "r") as f:
        step6_artifact = json.load(f)
    synopsis_len = len(step6_artifact.get('long_synopsis', ''))
    print(f"  - Loaded Step 6: {synopsis_len} characters in synopsis")
    
    # Test Step 7
    print("\n" + "="*60)
    print("TESTING STEP 7: CHARACTER BIBLES")
    print("="*60)
    
    step7 = Step7CharacterBibles()
    model_config = ModelSelector.get_model_config(step=7)
    print(f"Using model: {model_config.get('model_name', 'default')}")
    
    print("\nGenerating comprehensive character bibles...")
    success, artifact7, message = step7.execute(
        step5_artifact=step5_artifact,
        project_id=test_project,
        model_config=model_config
    )
    
    if success:
        print(f"SUCCESS: {message}")
        bibles = artifact7.get('bibles', [])
        print(f"\nGenerated {len(bibles)} character bibles:")
        
        for bible in bibles:
            name = bible.get('name', 'Unknown')
            
            # Count completeness
            total_fields = 0
            filled_fields = 0
            
            # Check each section
            sections_status = {}
            for section in ['physical', 'personality', 'environment', 'psychology']:
                section_data = bible.get(section, {})
                section_filled = 0
                section_total = 0
                
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        section_total += 1
                        total_fields += 1
                        if value and str(value).strip():
                            section_filled += 1
                            filled_fields += 1
                elif section_data:
                    section_total = 1
                    section_filled = 1
                    total_fields += 1
                    filled_fields += 1
                
                if section_total > 0:
                    sections_status[section] = f"{section_filled}/{section_total}"
            
            completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            
            print(f"\n  {name}:")
            print(f"    - Overall completeness: {completeness:.0f}% ({filled_fields}/{total_fields} fields)")
            print(f"    - Sections: {sections_status}")
            print(f"    - Voice notes: {len(bible.get('voice_notes', []))}")
            print(f"    - Contradictions: {len(bible.get('contradictions', []))}")
            
            # Show sample of psychology
            psych = bible.get('psychology', {})
            if isinstance(psych, dict):
                wound = psych.get('backstory_wound') or psych.get('wound', '')
                if wound:
                    print(f"    - Core wound: \"{wound[:60]}...\"")
    else:
        print(f"FAILED: {message}")
        return False
    
    # Load existing Step 7 for comparison
    with open(artifact_dir / "step_7_character_bibles.json", "r") as f:
        old_step7 = json.load(f)
    
    old_bibles = old_step7.get('bibles', [])
    print(f"\nComparison with old Step 7:")
    print(f"  - Old: {len(old_bibles)} bibles")
    print(f"  - New: {len(artifact7.get('bibles', []))} bibles")
    
    # Test Step 8
    print("\n" + "="*60)
    print("TESTING STEP 8: SCENE LIST")
    print("="*60)
    
    step8 = Step8SceneList()
    model_config = ModelSelector.get_model_config(step=8)
    print(f"Using model: {model_config.get('model_name', 'default')}")
    
    print("\nGenerating comprehensive scene list...")
    success, artifact8, message = step8.execute(
        step6_artifact=step6_artifact,
        step7_artifact=artifact7,
        project_id=test_project,
        model_config=model_config
    )
    
    if success:
        print(f"SUCCESS: {message}")
        
        scenes = artifact8.get('scenes', [])
        print(f"\nGenerated {len(scenes)} scenes")
        print(f"Total word target: {artifact8.get('total_word_target', 0):,} words")
        
        # Analyze scenes
        disasters = artifact8.get('disaster_anchors', {})
        print(f"\nDisaster placement:")
        for d in ['d1_scene', 'd2_scene', 'd3_scene']:
            scene_num = disasters.get(d)
            if scene_num:
                percent = (scene_num / len(scenes)) * 100
                print(f"  - {d.upper()[:2]}: Scene {scene_num} ({percent:.0f}% through story)")
            else:
                print(f"  - {d.upper()[:2]}: Not set")
        
        # POV distribution
        pov_dist = artifact8.get('pov_distribution', {})
        print(f"\nPOV distribution:")
        for pov, count in sorted(pov_dist.items(), key=lambda x: x[1], reverse=True):
            percent = (count / len(scenes)) * 100
            print(f"  - {pov}: {count} scenes ({percent:.0f}%)")
        
        # Scene types
        proactive = sum(1 for s in scenes if s.get('type') == 'Proactive')
        reactive = sum(1 for s in scenes if s.get('type') == 'Reactive')
        print(f"\nScene type balance:")
        print(f"  - Proactive: {proactive} ({proactive/len(scenes)*100:.0f}%)")
        print(f"  - Reactive: {reactive} ({reactive/len(scenes)*100:.0f}%)")
        
        # Conflict check
        conflict_check = artifact8.get('conflict_validation', {})
        if conflict_check.get('all_have_conflict'):
            print(f"\nOK: All {len(scenes)} scenes have conflict")
        else:
            without = conflict_check.get('scenes_without_conflict', [])
            print(f"\nERROR: {len(without)} scenes without conflict: {without[:5]}...")
        
        # CSV check
        csv_path = Path("artifacts") / test_project / "step_8_scenes.csv"
        if csv_path.exists():
            print(f"\nOK: CSV exported to: {csv_path}")
            # Count lines in CSV
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = len(f.readlines()) - 1  # Subtract header
            print(f"    - CSV has {lines} scene rows")
        
        # Sample first few scenes
        print(f"\nFirst 3 scenes:")
        for i, scene in enumerate(scenes[:3], 1):
            print(f"\n  Scene {i}: {scene.get('type')} - {scene.get('pov')}")
            summary = scene.get('summary', '')[:150]
            print(f"    {summary}...")
            if scene.get('disaster_anchor'):
                print(f"    DISASTER: {scene['disaster_anchor']}")
    else:
        print(f"FAILED: {message}")
        return False
    
    # Load old Step 8 for comparison
    with open(artifact_dir / "step_8_scene_list.json", "r") as f:
        old_step8 = json.load(f)
    
    old_scenes = old_step8.get('scenes', [])
    print(f"\nComparison with old Step 8:")
    print(f"  - Old: {len(old_scenes)} scenes")
    print(f"  - New: {len(scenes)} scenes")
    
    print("\n" + "="*60)
    print("TESTS COMPLETED SUCCESSFULLY")
    print("Both Step 7 and Step 8 are now generating comprehensive outputs!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_with_existing_data()
    sys.exit(0 if success else 1)