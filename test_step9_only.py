#!/usr/bin/env python3
"""Test Step 9 only with existing Step 8 data"""

import json
from pathlib import Path
from src.pipeline.steps.step_9_scene_briefs import Step9SceneBriefs

def test_step_9():
    # Load existing Step 8 artifact
    step8_path = Path("artifacts/smoketestnovel_20250819_153616/step_8_scene_list.json")
    
    if not step8_path.exists():
        print(f"Step 8 artifact not found at {step8_path}")
        return
    
    with open(step8_path, "r", encoding="utf-8") as f:
        step8_artifact = json.load(f)
    
    print(f"Loaded Step 8 with {len(step8_artifact.get('scenes', []))} scenes")
    
    # Initialize Step 9
    step9 = Step9SceneBriefs(project_dir="test_artifacts")
    
    # Execute Step 9
    print("\nExecuting Step 9 with batching...")
    ok, artifact, msg = step9.execute(
        step8_artifact,
        "test_step9_batching",
        model_config={"temperature": 0.3, "max_tokens": 2000}
    )
    
    if ok:
        print(f"[PASS] {msg}")
        briefs = artifact.get("scene_briefs", [])
        print(f"  Generated {len(briefs)} scene briefs")
        
        # Show first few briefs
        for i, brief in enumerate(briefs[:3]):
            print(f"\n  Brief {i+1}: Type={brief.get('type')}")
            if brief.get('type') == 'Proactive':
                print(f"    Goal: {brief.get('goal', 'N/A')[:50]}...")
            else:
                print(f"    Reaction: {brief.get('reaction', 'N/A')[:50]}...")
    else:
        print(f"[FAIL] {msg}")

if __name__ == "__main__":
    test_step_9()