#!/usr/bin/env python3
"""
Test the Snowflake pipeline steps 0-4
Verifies that our fixes have resolved the blocking issues
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.pipeline.orchestrator import SnowflakePipeline

def test_pipeline_steps():
    """Test the first 5 steps of the pipeline"""
    
    print("=" * 60)
    print("SNOWFLAKE PIPELINE TEST - STEPS 0-4")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] No OPENAI_API_KEY found in environment")
        print("Please set your OpenAI API key to run this test")
        return False
    
    # Initialize pipeline
    print("\nInitializing pipeline...")
    pipeline = SnowflakePipeline(project_dir="test_artifacts_pipeline")
    print("[PASS] Pipeline initialized")
    
    # Create new project
    project_name = f"test_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\nCreating project: {project_name}")
    project_id = pipeline.create_project(project_name)
    print(f"[PASS] Project created: {project_id}")
    
    # Test brief
    initial_brief = "A satirical near-future novel about immortality and capitalism"
    story_brief = "Casey Chen sells years of her life to pay rent, then must steal them back from time-repo agents"
    
    results = []
    
    try:
        # Step 0: First Things First
        print("\n" + "-" * 60)
        print("STEP 0: First Things First")
        print("-" * 60)
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_0(initial_brief)
        
        elapsed = time.time() - start_time
        if success:
            print(f"[PASS] Step 0 completed in {elapsed:.1f}s")
            print(f"  Category: {result.get('category', 'N/A')}")
            print(f"  Target Audience: {result.get('target_audience', 'N/A')}")
            print(f"  Story Kind: {result.get('story_kind', 'N/A')}")
            results.append(("Step 0", True, elapsed))
        else:
            print(f"[FAIL] Step 0 failed: {message}")
            results.append(("Step 0", False, elapsed))
            return False
        
        # Step 1: One Sentence Summary
        print("\n" + "-" * 60)
        print("STEP 1: One Sentence Summary")
        print("-" * 60)
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_1(story_brief)
        
        elapsed = time.time() - start_time
        if success:
            print(f"[PASS] Step 1 completed in {elapsed:.1f}s")
            print(f"  Logline: {result}")
            results.append(("Step 1", True, elapsed))
        else:
            print(f"[FAIL] Step 1 failed: {message}")
            results.append(("Step 1", False, elapsed))
            return False
        
        # Step 2: One Paragraph Summary
        print("\n" + "-" * 60)
        print("STEP 2: One Paragraph Summary")
        print("-" * 60)
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_2()
        
        elapsed = time.time() - start_time
        if success:
            print(f"[PASS] Step 2 completed in {elapsed:.1f}s")
            if isinstance(result, dict):
                if 'paragraph' in result:
                    para = result.get('paragraph', {})
                    if isinstance(para, dict) and 'sentences' in para:
                        print(f"  Paragraph sentences: {len(para.get('sentences', []))}")
                if 'moral_premise' in result:
                    print(f"  Moral premise: {result['moral_premise'][:80]}...")
            elif isinstance(result, str):
                print(f"  Paragraph length: {len(result)} characters")
            results.append(("Step 2", True, elapsed))
        else:
            print(f"[FAIL] Step 2 failed: {message}")
            results.append(("Step 2", False, elapsed))
            return False
        
        # Step 3: Character Summaries
        print("\n" + "-" * 60)
        print("STEP 3: Character Summaries")
        print("-" * 60)
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_3()
        
        elapsed = time.time() - start_time
        if success:
            print(f"[PASS] Step 3 completed in {elapsed:.1f}s")
            if isinstance(result, dict) and 'characters' in result:
                print(f"  Characters created: {len(result['characters'])}")
                for char in result['characters']:
                    print(f"    - {char.get('name', 'Unknown')}: {char.get('role', 'Unknown')}")
            results.append(("Step 3", True, elapsed))
        else:
            print(f"[FAIL] Step 3 failed: {message}")
            results.append(("Step 3", False, elapsed))
            return False
        
        # Step 4: One Page Synopsis
        print("\n" + "-" * 60)
        print("STEP 4: One Page Synopsis")
        print("-" * 60)
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_4()
        
        elapsed = time.time() - start_time
        if success:
            print(f"[PASS] Step 4 completed in {elapsed:.1f}s")
            if isinstance(result, str):
                print(f"  Synopsis length: {len(result)} characters")
                print(f"  Word count: ~{len(result.split())} words")
            results.append(("Step 4", True, elapsed))
        else:
            print(f"[FAIL] Step 4 failed: {message}")
            results.append(("Step 4", False, elapsed))
            return False
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_time = sum(r[2] for r in results)
    all_passed = all(r[1] for r in results)
    
    for step_name, passed, elapsed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {step_name:15} {status:7} ({elapsed:.1f}s)")
    
    print(f"\n  Total time: {total_time:.1f}s")
    print(f"  Average per step: {total_time/len(results):.1f}s")
    
    # Check artifacts
    print("\n" + "=" * 60)
    print("ARTIFACT VERIFICATION")
    print("=" * 60)
    
    artifact_dir = Path("test_artifacts_pipeline") / project_id
    if artifact_dir.exists():
        artifacts = list(artifact_dir.glob("*.json")) + list(artifact_dir.glob("*.md"))
        print(f"  Artifacts created: {len(artifacts)}")
        for artifact in artifacts[:10]:  # Show first 10
            size = artifact.stat().st_size
            print(f"    - {artifact.name} ({size} bytes)")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] ALL PIPELINE STEPS COMPLETED SUCCESSFULLY")
        print("The Snowflake pipeline is working correctly!")
    else:
        print("[FAIL] SOME PIPELINE STEPS FAILED")
    
    return all_passed

if __name__ == "__main__":
    success = test_pipeline_steps()
    exit(0 if success else 1)