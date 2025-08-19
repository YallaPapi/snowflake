#!/usr/bin/env python3
"""
Full E2E Test with All Improvements
Tests the complete pipeline from Steps 0-10 with exports
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from src.pipeline.orchestrator import SnowflakePipeline
from src.export.manuscript_exporter import ManuscriptExporter
from src.pipeline.progress_tracker import ProgressTracker

def run_full_e2e():
    """Run complete E2E test with progress tracking"""
    
    # Initialize
    project_id = f"full_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pipeline = SnowflakePipeline(project_dir="e2e_artifacts")
    tracker = ProgressTracker(project_dir="e2e_artifacts")
    
    print("=" * 70)
    print(f"FULL E2E TEST: {project_id}")
    print("=" * 70)
    
    # Create project
    print("\n[1/12] Creating project...")
    created_id = pipeline.create_project(project_name="Full E2E Test Novel")
    if not created_id:
        print("  [FAIL] Could not create project")
        return False
    
    # Story setup with proper format for Step 0
    story_brief = """
Category: Crime Thriller
Target Audience: Adult readers who enjoy police procedurals and corruption thrillers
Story Kind: A gripping police corruption thriller with moral complexity
Delight Factors:
1. The thrill of uncovering hidden corruption layer by layer
2. Complex moral dilemmas where right and wrong blur
3. High-stakes cat-and-mouse games between detective and corrupt cops
4. Shocking revelations about trusted authority figures
5. Justice prevailing against impossible odds

Brief: Internal affairs detective Mira Chen investigates what appears to be a routine police shooting in the Riverside district. But discrepancies in officer James Hayes' bodycam footage hint at something darker. As Chen digs deeper, she uncovers a web of corruption involving drug money, planted evidence, and murder - reaching all the way to the department's leadership. With her family threatened and nowhere to turn, Chen must decide between protecting those she loves and exposing the truth that could destroy them all.
"""
    
    print(f"\n[2/12] Starting pipeline execution...")
    print(f"  Project ID: {created_id}")
    
    # Track overall timing
    total_start = time.time()
    step_results = {}
    
    # Step 0
    print("\n[3/12] Step 0: First Things First...")
    start = time.time()
    try:
        success, artifact, message = pipeline.execute_step_0(story_brief)
        elapsed = time.time() - start
        step_results[0] = {"success": success, "time": elapsed, "message": message}
        print(f"  {'[PASS]' if success else '[FAIL]'} {message[:100]} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 0, "completed" if success else "failed")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  [ERROR] {e} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 0, "failed", error=str(e))
        step_results[0] = {"success": False, "time": elapsed, "message": str(e)}
    
    # Step 1
    print("\n[4/12] Step 1: One Sentence Summary...")
    start = time.time()
    try:
        brief_short = "An internal affairs detective uncovers police corruption while investigating a shooting."
        success, artifact, message = pipeline.execute_step_1(brief_short)
        elapsed = time.time() - start
        step_results[1] = {"success": success, "time": elapsed, "message": message}
        print(f"  {'[PASS]' if success else '[FAIL]'} {message[:100]} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 1, "completed" if success else "failed")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  [ERROR] {e} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 1, "failed", error=str(e))
        step_results[1] = {"success": False, "time": elapsed, "message": str(e)}
    
    # Steps 2-8 (faster steps)
    quick_steps = [
        (2, "Step 2: One Paragraph Summary", pipeline.execute_step_2),
        (3, "Step 3: Character Summaries", pipeline.execute_step_3),
        (4, "Step 4: One Page Synopsis", pipeline.execute_step_4),
        (5, "Step 5: Character Synopses", pipeline.execute_step_5),
        (6, "Step 6: Long Synopsis", pipeline.execute_step_6),
        (7, "Step 7: Character Bibles", pipeline.execute_step_7),
        (8, "Step 8: Scene List", pipeline.execute_step_8),
    ]
    
    for step_num, step_name, step_func in quick_steps:
        print(f"\n[{step_num+3}/12] {step_name}...")
        start = time.time()
        try:
            success, artifact, message = step_func()
            elapsed = time.time() - start
            step_results[step_num] = {"success": success, "time": elapsed, "message": message}
            print(f"  {'[PASS]' if success else '[FAIL]'} {message[:100]} ({elapsed:.1f}s)")
            tracker.save_checkpoint(created_id, step_num, "completed" if success else "failed")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [ERROR] {e} ({elapsed:.1f}s)")
            tracker.save_checkpoint(created_id, step_num, "failed", error=str(e))
            step_results[step_num] = {"success": False, "time": elapsed, "message": str(e)}
    
    # Step 9 (slower - scene briefs)
    print("\n[11/12] Step 9: Scene Briefs (this may take a while)...")
    start = time.time()
    try:
        success, artifact, message = pipeline.execute_step_9()
        elapsed = time.time() - start
        step_results[9] = {"success": success, "time": elapsed, "message": message}
        print(f"  {'[PASS]' if success else '[FAIL]'} {message[:100]} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 9, "completed" if success else "failed")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  [ERROR] {e} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 9, "failed", error=str(e))
        step_results[9] = {"success": False, "time": elapsed, "message": str(e)}
    
    # Step 10 (slowest - manuscript generation)
    print("\n[12/12] Step 10: First Draft (this will take several minutes)...")
    start = time.time()
    try:
        success, artifact, message = pipeline.execute_step_10(target_words=10000)  # Smaller for testing
        elapsed = time.time() - start
        step_results[10] = {"success": success, "time": elapsed, "message": message}
        print(f"  {'[PASS]' if success else '[FAIL]'} {message[:100]} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 10, "completed" if success else "failed")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  [ERROR] {e} ({elapsed:.1f}s)")
        tracker.save_checkpoint(created_id, 10, "failed", error=str(e))
        step_results[10] = {"success": False, "time": elapsed, "message": str(e)}
    
    total_elapsed = time.time() - total_start
    
    # Export test
    print("\n" + "=" * 70)
    print("EXPORT TEST")
    print("=" * 70)
    
    export_success = False
    try:
        manuscript_path = Path(f"e2e_artifacts/{created_id}/step_10_manuscript.json")
        if manuscript_path.exists():
            import json
            with open(manuscript_path, "r", encoding="utf-8") as f:
                manuscript = json.load(f)
            
            exporter = ManuscriptExporter(project_dir="e2e_artifacts")
            
            # Test exports
            for fmt in ["markdown", "docx", "epub"]:
                try:
                    if fmt == "markdown":
                        path = exporter.export_markdown(manuscript, project_id=created_id)
                    elif fmt == "docx":
                        path = exporter.export_docx(manuscript, project_id=created_id)
                    else:
                        path = exporter.export_epub(manuscript, project_id=created_id)
                    print(f"  [PASS] {fmt.upper()} export: {path.name}")
                    export_success = True
                except Exception as e:
                    print(f"  [FAIL] {fmt.upper()} export: {e}")
        else:
            print("  [SKIP] No manuscript to export")
    except Exception as e:
        print(f"  [ERROR] Export test failed: {e}")
    
    # Final report
    print("\n" + "=" * 70)
    print("E2E TEST SUMMARY")
    print("=" * 70)
    print(f"Total time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
    
    # Count successes
    successful_steps = sum(1 for r in step_results.values() if r["success"])
    failed_steps = [step for step, r in step_results.items() if not r["success"]]
    
    print(f"Steps completed: {successful_steps}/11")
    
    if failed_steps:
        print(f"\nFailed steps: {failed_steps}")
    
    print("\nStep timings:")
    for step, result in step_results.items():
        status = "[PASS]" if result["success"] else "[FAIL]"
        print(f"  {status} Step {step}: {result['time']:.1f}s")
    
    # Progress report
    print("\n" + tracker.create_progress_report(created_id))
    
    # Check output quality
    if manuscript_path.exists():
        with open(manuscript_path, "r", encoding="utf-8") as f:
            manuscript_data = json.load(f)
        
        ms = manuscript_data.get("manuscript", {})
        total_words = ms.get("total_word_count", 0)
        total_scenes = ms.get("total_scenes", 0)
        total_chapters = ms.get("total_chapters", 0)
        
        print(f"\nManuscript Stats:")
        print(f"  Chapters: {total_chapters}")
        print(f"  Scenes: {total_scenes}")
        print(f"  Words: {total_words:,}")
        
        if total_words > 5000:
            print(f"  Quality: GOOD (>{5000:,} words)")
        elif total_words > 1000:
            print(f"  Quality: ACCEPTABLE (>{1000:,} words)")
        else:
            print(f"  Quality: POOR (<1000 words)")
    
    # Final verdict
    success = successful_steps == 11 and export_success
    print(f"\n{'=' * 70}")
    print(f"FINAL RESULT: {'PASS' if success else 'FAIL'}")
    print(f"{'=' * 70}")
    
    return success

if __name__ == "__main__":
    success = run_full_e2e()
    sys.exit(0 if success else 1)