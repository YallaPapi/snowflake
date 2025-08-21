#!/usr/bin/env python3
"""Test Steps 9 and 10 - The actual novel writing steps"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Test Step 9: Scene Briefs
def test_step_9():
    """Test scene brief generation with concrete triads"""
    print("\n" + "="*60)
    print("TESTING STEP 9: SCENE BRIEFS")
    print("="*60)
    
    from src.pipeline.steps.step_9_scene_briefs_v2 import Step9SceneBriefsV2
    
    # Create test scene list (minimal for testing)
    test_scenes = [
        {
            "index": 1,
            "chapter_hint": "Chapter 1",
            "type": "Proactive",
            "pov": "Sarah",
            "summary": "Sarah infiltrates the enemy compound to steal evidence",
            "time": "Midnight",
            "location": "Enemy compound",
            "word_target": 1500,
            "conflict": {"type": "external", "against": "Guards"},
            "disaster_anchor": None,
            "inbound_hook": "Received tip about evidence location",
            "outbound_hook": "Alarm sounds"
        },
        {
            "index": 2,
            "chapter_hint": "Chapter 1", 
            "type": "Reactive",
            "pov": "Sarah",
            "summary": "Sarah processes being discovered and decides next move",
            "time": "12:30 AM",
            "location": "Ventilation shaft",
            "word_target": 1000,
            "conflict": {"type": "internal", "about": "Trust"},
            "disaster_anchor": "D1",
            "inbound_hook": "Alarm sounds",
            "outbound_hook": "Commits to dangerous plan"
        },
        {
            "index": 3,
            "chapter_hint": "Chapter 2",
            "type": "Proactive",
            "pov": "Marcus",
            "summary": "Marcus races to extract Sarah before SWAT arrives",
            "time": "12:45 AM",
            "location": "Streets outside compound",
            "word_target": 1500,
            "conflict": {"type": "external", "against": "Time and police"},
            "disaster_anchor": None,
            "inbound_hook": "Gets Sarah's emergency signal",
            "outbound_hook": "Extraction route blocked"
        }
    ]
    
    step8_artifact = {
        "scenes": test_scenes,
        "metadata": {"test": True}
    }
    
    # Initialize Step 9
    step9 = Step9SceneBriefsV2(project_dir="test_artifacts")
    
    # Execute
    print("\nGenerating scene briefs...")
    ok, artifact, msg = step9.execute(
        step8_artifact,
        "test_novel_writing",
        model_config={"temperature": 0.5, "max_tokens": 2000}
    )
    
    if ok:
        print(f"[PASS] Step 9 passed: {msg}")
        briefs = artifact.get("scene_briefs", [])
        
        # Show generated briefs
        for i, brief in enumerate(briefs):
            print(f"\n  Scene {i+1} ({brief.get('type', 'Unknown')}):")
            if brief.get('type') == 'Proactive':
                print(f"    Goal: {brief.get('goal', 'N/A')[:60]}...")
                print(f"    Conflict: {brief.get('conflict', 'N/A')[:60]}...")
                print(f"    Setback: {brief.get('setback', 'N/A')[:60]}...")
            else:
                print(f"    Reaction: {brief.get('reaction', 'N/A')[:60]}...")
                print(f"    Dilemma: {brief.get('dilemma', 'N/A')[:60]}...")
                print(f"    Decision: {brief.get('decision', 'N/A')[:60]}...")
            print(f"    Stakes: {brief.get('stakes', 'N/A')[:60]}...")
        
        return True, artifact
    else:
        print(f"[FAIL] Step 9 failed: {msg}")
        return False, None

# Test Step 10: Draft Writer
def test_step_10(step9_artifact):
    """Test actual prose generation"""
    print("\n" + "="*60)
    print("TESTING STEP 10: DRAFT WRITER")
    print("="*60)
    
    from src.pipeline.steps.step_10_draft_writer import Step10DraftWriter
    
    # Create minimal character bibles for POV characters
    character_bibles = {
        "bibles": [
            {
                "name": "Sarah",
                "role": "protagonist",
                "personality": {
                    "traits": ["determined", "resourceful", "haunted"],
                    "flaws": ["trust issues", "impulsive"]
                },
                "voice_notes": ["terse internal monologue", "notices exits first"],
                "physical": {"age": 32, "description": "athletic build, sharp eyes"}
            },
            {
                "name": "Marcus",
                "role": "ally",
                "personality": {
                    "traits": ["loyal", "tactical", "protective"],
                    "flaws": ["overprotective", "guilt-driven"]
                },
                "voice_notes": ["military precision in thought", "tactical assessment"],
                "physical": {"age": 35, "description": "ex-military bearing"}
            }
        ]
    }
    
    # Use same scene list from Step 9
    scene_list = {
        "scenes": [
            {
                "index": 1,
                "chapter_hint": "Chapter 1",
                "type": "Proactive",
                "pov": "Sarah",
                "summary": "Sarah infiltrates the enemy compound to steal evidence",
                "time": "Midnight",
                "location": "Enemy compound - server room",
                "word_target": 800,  # Reduced for testing
                "inbound_hook": "Received tip about evidence location",
                "outbound_hook": "Alarm sounds"
            },
            {
                "index": 2,
                "chapter_hint": "Chapter 1",
                "type": "Reactive",
                "pov": "Sarah",
                "summary": "Sarah processes being discovered and decides next move",
                "time": "12:30 AM",
                "location": "Ventilation shaft",
                "word_target": 600,  # Reduced for testing
                "inbound_hook": "Alarm sounds",
                "outbound_hook": "Commits to dangerous plan"
            },
            {
                "index": 3,
                "chapter_hint": "Chapter 2",
                "type": "Proactive",
                "pov": "Marcus",
                "summary": "Marcus races to extract Sarah before SWAT arrives",
                "time": "12:45 AM",
                "location": "Streets outside compound",
                "word_target": 800,  # Reduced for testing
                "inbound_hook": "Gets Sarah's emergency signal",
                "outbound_hook": "Extraction route blocked"
            }
        ]
    }
    
    # Initialize Step 10
    step10 = Step10DraftWriter(project_dir="test_artifacts")
    
    # Execute with lower word targets for testing
    print("\nGenerating manuscript prose...")
    print("This will write ACTUAL NOVEL PROSE for each scene...")
    
    ok, manuscript, msg = step10.execute(
        scene_list,
        step9_artifact,
        character_bibles,
        "test_novel_writing",
        target_words=2200,  # Total for 3 test scenes
        model_config={
            "temperature": 0.8,  # Higher for creative prose
            "max_tokens": 4000   # Enough for full scenes
        }
    )
    
    if ok:
        print(f"\n[PASS] Step 10 passed: {msg}")
        
        # Show prose samples
        scenes = manuscript.get("scenes", [])
        for scene in scenes:
            print(f"\n  Scene {scene.get('scene_num', 0)} - {scene.get('pov', 'Unknown')} POV")
            print(f"  Type: {scene.get('type', 'Unknown')}")
            print(f"  Words: {scene.get('word_count', 0)}")
            
            # Show first 200 chars of prose
            prose = scene.get('prose', '')
            if prose:
                print(f"  Opening: {prose[:200]}...")
        
        # Show totals
        print(f"\n  TOTALS:")
        print(f"    Chapters: {manuscript.get('chapter_count', 0)}")
        print(f"    Scenes: {manuscript.get('scene_count', 0)}")
        print(f"    Words: {manuscript.get('total_word_count', 0):,}")
        
        # Save sample
        output_path = Path("test_artifacts/test_novel_writing")
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save manuscript
        with open(output_path / "manuscript.json", "w", encoding="utf-8") as f:
            json.dump(manuscript, f, indent=2, ensure_ascii=False)
        
        # Save readable version
        with open(output_path / "manuscript.md", "w", encoding="utf-8") as f:
            f.write("# TEST MANUSCRIPT\n\n")
            for scene in scenes:
                f.write(f"## Scene {scene.get('scene_num', 0)}\n\n")
                f.write(f"**POV:** {scene.get('pov', 'Unknown')} | ")
                f.write(f"**Type:** {scene.get('type', 'Unknown')} | ")
                f.write(f"**Words:** {scene.get('word_count', 0)}\n\n")
                f.write(scene.get('prose', '[No prose generated]'))
                f.write("\n\n---\n\n")
        
        print(f"\n  Manuscript saved to: {output_path}/manuscript.md")
        
        return True
    else:
        print(f"\n[FAIL] Step 10 failed: {msg}")
        return False

# Main test runner
def main():
    """Run complete test of novel writing pipeline"""
    print("\n" + "#"*60)
    print("# TESTING NOVEL WRITING PIPELINE (STEPS 9 & 10)")
    print("#"*60)
    
    # Test Step 9
    step9_ok, step9_artifact = test_step_9()
    
    if not step9_ok:
        print("\n[ERROR] Step 9 failed - cannot proceed to Step 10")
        return 1
    
    # Test Step 10  
    step10_ok = test_step_10(step9_artifact)
    
    if not step10_ok:
        print("\n[ERROR] Step 10 failed - novel not written")
        return 1
    
    print("\n" + "="*60)
    print("[SUCCESS] NOVEL WRITING PIPELINE TEST COMPLETE!")
    print("="*60)
    print("\nThe system successfully:")
    print("1. Generated concrete scene briefs with proper triads")
    print("2. Wrote actual novel prose for each scene")
    print("3. Assembled chapters and tracked word count")
    print("4. Exported readable manuscript")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())