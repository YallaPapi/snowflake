#!/usr/bin/env python3
"""
Complete E2E Test of Snowflake Pipeline
Tests all steps from 0-10 with minimal configuration
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from src.pipeline.orchestrator import SnowflakePipeline
from src.export.manuscript_exporter import ManuscriptExporter

def test_e2e():
    """Run complete E2E test"""
    
    # Initialize pipeline
    project_id = f"e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pipeline = SnowflakePipeline(project_dir="test_e2e_artifacts")
    
    print(f"Starting E2E test: {project_id}")
    print("=" * 60)
    
    # Create project with minimal configuration
    config = {
        "project_id": project_id,
        "title": "E2E Test Novel",
        "author": "Test Author",
        "target_words": 10000,  # Small for testing
        "model_config": {
            "temperature": 0.3,
            "max_tokens": 2000
        }
    }
    
    # Initialize project
    print("\nCreating project...")
    created_id = pipeline.create_project(project_name=config["title"])
    
    if not created_id:
        print("[FAIL] Could not create project")
        return False
    
    # Use the created project ID
    project_id = created_id
    
    # Test data for Step 0
    test_input = {
        "category": "Thriller",
        "target_audience": "Adult readers who enjoy police procedurals",
        "story_kind": "Crime thriller about police corruption",
        "delight_statement": "A gripping investigation that exposes systemic corruption"
    }
    
    story_brief = "An internal affairs detective investigates a police shooting that uncovers department-wide corruption"
    
    # Track timing
    step_times = {}
    
    # Run all steps
    # First, Step 0 needs the input formatted as a story brief string
    story_brief_full = f"""
Category: {test_input['category']}
Target Audience: {test_input['target_audience']}
Story Kind: {test_input['story_kind']}
Delight: {test_input['delight_statement']}

Brief: {story_brief}
"""
    
    steps = [
        ("Step 0: First Things First", lambda: pipeline.execute_step_0(story_brief_full)),
        ("Step 1: One Sentence Summary", lambda: pipeline.execute_step_1(story_brief)),
        ("Step 2: One Paragraph Summary", lambda: pipeline.execute_step_2()),
        ("Step 3: Character Summaries", lambda: pipeline.execute_step_3()),
        ("Step 4: One Page Synopsis", lambda: pipeline.execute_step_4()),
        ("Step 5: Character Synopses", lambda: pipeline.execute_step_5()),
        ("Step 6: Long Synopsis", lambda: pipeline.execute_step_6()),
        ("Step 7: Character Bibles", lambda: pipeline.execute_step_7()),
        ("Step 8: Scene List", lambda: pipeline.execute_step_8()),
        ("Step 9: Scene Briefs", lambda: pipeline.execute_step_9()),
        ("Step 10: First Draft", lambda: pipeline.execute_step_10(target_words=5000))
    ]
    
    total_start = time.time()
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        start_time = time.time()
        
        try:
            success, artifact, message = step_func()
            elapsed = time.time() - start_time
            step_times[step_name] = elapsed
            
            if success:
                print(f"  [PASS] {message} ({elapsed:.1f}s)")
            else:
                print(f"  [FAIL] {message} ({elapsed:.1f}s)")
                failed_steps.append(step_name)
                # Continue anyway to test as much as possible
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  [ERROR] {e} ({elapsed:.1f}s)")
            failed_steps.append(step_name)
    
    total_time = time.time() - total_start
    
    # Export test
    print("\nTesting exports...")
    try:
        # Load Step 10 artifact
        artifact_path = Path(f"test_e2e_artifacts/{project_id}/step_10_manuscript.json")
        if artifact_path.exists():
            import json
            with open(artifact_path, "r", encoding="utf-8") as f:
                manuscript = json.load(f)
            
            exporter = ManuscriptExporter(project_dir="test_e2e_artifacts")
            
            # Test all export formats
            export_formats = ["docx", "epub", "markdown"]
            for fmt in export_formats:
                try:
                    if fmt == "docx":
                        path = exporter.export_docx(manuscript, project_id=project_id)
                    elif fmt == "epub":
                        path = exporter.export_epub(manuscript, project_id=project_id)
                    else:
                        path = exporter.export_markdown(manuscript, project_id=project_id)
                    
                    print(f"  [PASS] {fmt.upper()} export: {path.name}")
                except Exception as e:
                    print(f"  [FAIL] {fmt.upper()} export: {e}")
        else:
            print("  [SKIP] No manuscript to export")
    except Exception as e:
        print(f"  [ERROR] Export test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("E2E TEST SUMMARY")
    print("=" * 60)
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Failed steps: {len(failed_steps)}")
    
    if failed_steps:
        print("\nFailed steps:")
        for step in failed_steps:
            print(f"  - {step}")
    
    print("\nStep timings:")
    for step, timing in step_times.items():
        print(f"  {step}: {timing:.1f}s")
    
    # Check artifacts
    artifact_dir = Path(f"test_e2e_artifacts/{project_id}")
    if artifact_dir.exists():
        artifacts = list(artifact_dir.glob("*.json"))
        print(f"\nArtifacts created: {len(artifacts)}")
        
        # Check manuscript stats
        manuscript_path = artifact_dir / "manuscript.md"
        if manuscript_path.exists():
            with open(manuscript_path, "r", encoding="utf-8") as f:
                content = f.read()
                word_count = len(content.split())
                print(f"Manuscript word count: {word_count:,}")
    
    success = len(failed_steps) == 0
    print(f"\n{'[PASS]' if success else '[FAIL]'} E2E Test {'succeeded' if success else 'failed'}")
    
    return success

if __name__ == "__main__":
    success = test_e2e()
    sys.exit(0 if success else 1)