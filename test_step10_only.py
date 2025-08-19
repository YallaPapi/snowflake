#!/usr/bin/env python3
"""Test Step 10 with existing Step 7, 8, 9 data"""

import json
from pathlib import Path
from src.pipeline.steps.step_10_first_draft import Step10FirstDraft

def test_step_10():
    # Use the old project that has steps 0-8 completed
    project_id = "smoketestnovel_20250819_153616"
    base_path = Path(f"artifacts/{project_id}")
    
    # Load required artifacts
    step7_path = base_path / "step_7_character_bibles.json"
    step8_path = base_path / "step_8_scene_list.json"
    step9_path = base_path / "step_9_scene_briefs.json"  # May not exist yet
    
    # Check if Step 9 exists, if not use a minimal one
    if not step9_path.exists():
        print("Step 9 not found, creating minimal briefs...")
        # Load Step 8 to get scene count
        with open(step8_path, "r", encoding="utf-8") as f:
            step8 = json.load(f)
        
        # Create minimal briefs
        scenes = step8.get("scenes", [])
        briefs = []
        for i, scene in enumerate(scenes[:5]):  # Just test first 5 scenes
            if scene.get("type") == "Proactive":
                brief = {
                    "type": "Proactive",
                    "goal": f"achieve objective in scene {i+1} before deadline",
                    "conflict": "face opposition from antagonist forces",
                    "setback": "situation worsens forcing new approach",
                    "stakes": "failure means loss of critical opportunity"
                }
            else:
                brief = {
                    "type": "Reactive",
                    "reaction": "process emotional impact with physical response",
                    "dilemma": "choose between two difficult options",
                    "decision": "commit to new course of action",
                    "stakes": "wrong choice leads to greater losses"
                }
            briefs.append(brief)
        
        step9_artifact = {"scene_briefs": briefs}
    else:
        with open(step9_path, "r", encoding="utf-8") as f:
            step9_artifact = json.load(f)
    
    # Load other artifacts
    with open(step7_path, "r", encoding="utf-8") as f:
        step7_artifact = json.load(f)
    
    with open(step8_path, "r", encoding="utf-8") as f:
        step8_artifact = json.load(f)
    
    # Limit to first 5 scenes for testing
    step8_artifact["scenes"] = step8_artifact["scenes"][:5]
    step9_artifact["scene_briefs"] = step9_artifact.get("scene_briefs", [])[:5]
    
    print(f"Testing Step 10 with {len(step8_artifact['scenes'])} scenes")
    
    # Initialize Step 10
    step10 = Step10FirstDraft(project_dir="test_artifacts")
    
    # Execute
    print("\nGenerating manuscript...")
    ok, artifact, msg = step10.execute(
        step9_artifact,
        step7_artifact,
        step8_artifact,
        "test_step10",
        model_config={"temperature": 0.7, "max_tokens": 2000}
    )
    
    if ok:
        print(f"[PASS] {msg}")
        manuscript = artifact.get("manuscript", {})
        print(f"  Chapters: {manuscript.get('total_chapters', 0)}")
        print(f"  Scenes: {manuscript.get('total_scenes', 0)}")
        print(f"  Words: {manuscript.get('total_word_count', 0):,}")
    else:
        print(f"[FAIL] {msg}")

if __name__ == "__main__":
    test_step_10()