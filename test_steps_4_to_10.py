#!/usr/bin/env python3
"""
Test Steps 4-10 individually to identify and fix issues
"""

from pathlib import Path
from src.pipeline.orchestrator import SnowflakePipeline
import sys
import traceback

def test_step(pipeline, step_num, step_fn, step_name):
    """Test a single step and report results"""
    print(f"\n{'='*60}")
    print(f"Testing Step {step_num}: {step_name}")
    print(f"{'='*60}")
    
    try:
        ok, artifact, msg = step_fn()
        
        if ok:
            print(f"[PASS] Step {step_num} PASSED")
            print(f"   Message: {msg[:200]}...")
            
            # Check if artifact was saved
            artifact_files = {
                4: "step_4_one_page_synopsis.json",
                5: "step_5_character_synopses.json", 
                6: "step_6_long_synopsis.json",
                7: "step_7_character_bibles.json",
                8: "step_8_scene_list.json",
                9: "step_9_scene_briefs.json",
                10: "step_10_manuscript.json"
            }
            
            if step_num in artifact_files:
                artifact_path = Path("artifacts") / pipeline.current_project_id / artifact_files[step_num]
                if artifact_path.exists():
                    print(f"   Artifact saved: {artifact_path}")
                    size = artifact_path.stat().st_size
                    print(f"   Size: {size:,} bytes")
                else:
                    print(f"   [WARN] Artifact not found at {artifact_path}")
                    
        else:
            print(f"[FAIL] Step {step_num} FAILED")
            print(f"   Error: {msg}")
            
        return ok
        
    except Exception as e:
        print(f"[CRASH] Step {step_num} CRASHED")
        print(f"   Exception: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        return False

def main():
    # Use the last successful smoke test project that completed Steps 0-3
    project_id = "smoketestnovel_20250819_153616"
    
    print(f"Loading project: {project_id}")
    
    pipeline = SnowflakePipeline()
    pipeline.load_project(project_id)
    
    # Check that Steps 0-3 are complete
    print("\nVerifying Steps 0-3 are complete...")
    for step in range(4):
        artifact = pipeline._load_step_artifact(step)
        if artifact:
            print(f"  [OK] Step {step} artifact exists")
        else:
            print(f"  [ERROR] Step {step} artifact missing - cannot continue")
            return 1
    
    # Test each remaining step
    steps_to_test = [
        (4, pipeline.execute_step_4, "One Page Synopsis"),
        (5, pipeline.execute_step_5, "Character Synopses"),
        (6, pipeline.execute_step_6, "Long Synopsis"),
        (7, pipeline.execute_step_7, "Character Bibles"),
        (8, pipeline.execute_step_8, "Scene List"),
        (9, pipeline.execute_step_9, "Scene Briefs"),
        (10, lambda: pipeline.execute_step_10(90000), "Draft Writer")
    ]
    
    failed_steps = []
    
    for step_num, step_fn, step_name in steps_to_test:
        # Skip if already completed successfully
        existing_artifact = pipeline._load_step_artifact(step_num)
        if existing_artifact:
            print(f"\n[SKIP] Step {step_num} already completed - skipping")
            continue
            
        success = test_step(pipeline, step_num, step_fn, step_name)
        
        if not success:
            failed_steps.append(step_num)
            print(f"\n[STOP] Stopping at Step {step_num} due to failure")
            break  # Stop on first failure to debug
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    if failed_steps:
        print(f"[FAILED] Steps {failed_steps} need fixing")
        print("\nNext actions:")
        print("1. Check the error messages above")
        print("2. Review the step implementation")
        print("3. Fix validation or generation issues")
        return 1
    else:
        print("[SUCCESS] ALL STEPS PASSED!")
        print("\nThe pipeline is ready for full E2E testing")
        return 0

if __name__ == "__main__":
    sys.exit(main())