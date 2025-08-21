#!/usr/bin/env python3
"""
Enhanced E2E Test with Full Observability
Tests the complete Snowflake pipeline from Steps 0-10 with comprehensive monitoring
"""

import sys
import time
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.pipeline.orchestrator import SnowflakePipeline
from src.export.manuscript_exporter import ManuscriptExporter
from src.pipeline.progress_tracker import ProgressTracker
from src.observability.events import (
    start_monitoring, stop_monitoring, emit_event, emit_step_start, 
    emit_step_complete, emit_step_progress, emit_error, get_project_summary
)


class ObservabilityServer:
    """Manages the observability server lifecycle"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://127.0.0.1:5000"
    
    def start(self):
        """Start the observability server in background"""
        try:
            # Kill any existing server
            self.stop()
            
            print(f"[OBSERVABILITY] Starting monitoring server at {self.server_url}")
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "src.observability.server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Test if server is responding
            import urllib.request
            try:
                with urllib.request.urlopen(f"{self.server_url}/health", timeout=5) as response:
                    if response.getcode() == 200:
                        print(f"[OBSERVABILITY] Server started successfully")
                        print(f"[OBSERVABILITY] Dashboard: {self.server_url}")
                        print(f"[OBSERVABILITY] Health: {self.server_url}/health")
                        print(f"[OBSERVABILITY] Metrics: {self.server_url}/metrics")
                        return True
            except Exception as e:
                print(f"[OBSERVABILITY] Server health check failed: {e}")
                return False
                
        except Exception as e:
            print(f"[OBSERVABILITY] Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the observability server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
            self.server_process = None


def run_e2e_with_monitoring():
    """Run complete E2E test with full observability"""
    
    print("=" * 80)
    print("SNOWFLAKE E2E TEST WITH COMPREHENSIVE OBSERVABILITY")
    print("=" * 80)
    
    # Start observability server
    obs_server = ObservabilityServer()
    server_started = obs_server.start()
    
    try:
        # Initialize pipeline
        project_id = f"monitored_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pipeline = SnowflakePipeline(project_dir="artifacts")
        tracker = ProgressTracker(project_dir="artifacts")
        
        print(f"\n[PIPELINE] Project ID: {project_id}")
        if server_started:
            print(f"[MONITORING] Dashboard: http://127.0.0.1:5000")
            print("[MONITORING] Refresh the dashboard to see live progress")
        
        # Start comprehensive monitoring
        start_monitoring(project_id)
        
        # Create project with monitoring
        print(f"\n[1/13] Creating project with monitoring...")
        emit_event(project_id, "pipeline_start", {
            "total_steps": 11,
            "target_words": 10000,
            "story_type": "Crime Thriller"
        })
        
        created_id = pipeline.create_project(project_name="Monitored E2E Test Novel")
        if not created_id:
            emit_error(project_id, None, "project_creation_failed", "Could not create project")
            print("  [FAIL] Could not create project")
            return False
        
        # Update project_id to match created_id for consistency
        project_id = created_id
        
        # Story setup
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
        
        # Execute all steps with comprehensive monitoring
        total_start = time.time()
        step_results = {}
        successful_steps = 0
        
        # Step definitions with enhanced monitoring
        steps = [
            (0, "First Things First", lambda: pipeline.execute_step_0(story_brief)),
            (1, "One Sentence Summary", lambda: pipeline.execute_step_1("An internal affairs detective uncovers police corruption while investigating a shooting.")),
            (2, "One Paragraph Summary", lambda: pipeline.execute_step_2()),
            (3, "Character Summaries", lambda: pipeline.execute_step_3()),
            (4, "One Page Synopsis", lambda: pipeline.execute_step_4()),
            (5, "Character Synopses", lambda: pipeline.execute_step_5()),
            (6, "Long Synopsis", lambda: pipeline.execute_step_6()),
            (7, "Character Bibles", lambda: pipeline.execute_step_7()),
            (8, "Scene List", lambda: pipeline.execute_step_8()),
            (9, "Scene Briefs", lambda: pipeline.execute_step_9()),
            (10, "First Draft", lambda: pipeline.execute_step_10(target_words=10000))
        ]
        
        for step_num, step_name, step_func in steps:
            step_display = f"[{step_num+2}/13] Step {step_num}: {step_name}"
            print(f"\n{step_display}...")
            
            # Emit step start event
            emit_step_start(project_id, step_num, step_name)
            
            start_time = time.time()
            try:
                # Execute step with progress updates
                if step_num >= 9:  # Slower steps
                    print(f"  [INFO] This step may take several minutes...")
                    
                success, artifact, message = step_func()
                duration = time.time() - start_time
                
                # Emit completion event
                emit_step_complete(project_id, step_num, step_name, duration, success,
                                 artifact_size=len(str(artifact)) if artifact else 0,
                                 message=message)
                
                step_results[step_num] = {
                    "success": success, 
                    "time": duration, 
                    "message": message,
                    "artifact_size": len(str(artifact)) if artifact else 0
                }
                
                if success:
                    successful_steps += 1
                    print(f"  [PASS] Completed in {duration:.1f}s - {message[:100]}")
                    tracker.save_checkpoint(created_id, step_num, "completed")
                else:
                    print(f"  [FAIL] Failed after {duration:.1f}s - {message[:100]}")
                    emit_error(project_id, step_num, "step_execution_failed", message)
                    tracker.save_checkpoint(created_id, step_num, "failed", error=message)
                    
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                
                # Emit error event
                emit_error(project_id, step_num, "step_exception", error_msg,
                          duration=duration)
                
                print(f"  [ERROR] Exception after {duration:.1f}s - {error_msg[:100]}")
                step_results[step_num] = {
                    "success": False, 
                    "time": duration, 
                    "message": error_msg
                }
                tracker.save_checkpoint(created_id, step_num, "failed", error=error_msg)
            
            # Brief pause between steps
            time.sleep(0.5)
        
        total_elapsed = time.time() - total_start
        
        # Export test with monitoring
        print(f"\n[13/13] Export Testing...")
        export_start = time.time()
        export_success = False
        export_results = {}
        
        try:
            manuscript_path = Path(f"artifacts/{created_id}/step_10_manuscript.json")
            if manuscript_path.exists():
                import json
                with open(manuscript_path, "r", encoding="utf-8") as f:
                    manuscript = json.load(f)
                
                exporter = ManuscriptExporter(project_dir="artifacts")
                
                # Test all export formats
                for fmt in ["markdown", "docx", "epub"]:
                    fmt_start = time.time()
                    try:
                        if fmt == "markdown":
                            path = exporter.export_markdown(manuscript, project_id=created_id)
                        elif fmt == "docx":
                            path = exporter.export_docx(manuscript, project_id=created_id)
                        else:
                            path = exporter.export_epub(manuscript, project_id=created_id)
                        
                        fmt_duration = time.time() - fmt_start
                        export_results[fmt] = {"success": True, "path": str(path), "duration": fmt_duration}
                        print(f"  [PASS] {fmt.upper()} export: {path.name} ({fmt_duration:.1f}s)")
                        export_success = True
                        
                    except Exception as e:
                        fmt_duration = time.time() - fmt_start
                        export_results[fmt] = {"success": False, "error": str(e), "duration": fmt_duration}
                        print(f"  [FAIL] {fmt.upper()} export: {e} ({fmt_duration:.1f}s)")
            else:
                print("  [SKIP] No manuscript available for export")
                
        except Exception as e:
            print(f"  [ERROR] Export test failed: {e}")
        
        export_duration = time.time() - export_start
        
        # Emit final results
        emit_event(project_id, "pipeline_complete", {
            "total_duration": total_elapsed,
            "successful_steps": successful_steps,
            "failed_steps": 11 - successful_steps,
            "export_success": export_success,
            "export_results": export_results,
            "overall_success": successful_steps == 11 and export_success
        })
        
        # Generate comprehensive final report
        print("\n" + "=" * 80)
        print("COMPREHENSIVE E2E TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Duration: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
        print(f"Successful Steps: {successful_steps}/11")
        print(f"Export Success: {export_success}")
        
        if server_started:
            print(f"\nLive Dashboard: http://127.0.0.1:5000")
            print("View real-time metrics and detailed logs in the dashboard")
        
        # Step timing breakdown
        print(f"\nStep Timing Breakdown:")
        total_step_time = 0
        for step, result in step_results.items():
            status = "[PASS]" if result["success"] else "[FAIL]"
            print(f"  {status} Step {step}: {result['time']:.1f}s - {result.get('message', '')[:80]}")
            if result["success"]:
                total_step_time += result['time']
        
        print(f"\nTotal Step Execution Time: {total_step_time:.1f}s")
        print(f"Export Time: {export_duration:.1f}s")
        
        # Manuscript quality analysis
        if manuscript_path.exists():
            with open(manuscript_path, "r", encoding="utf-8") as f:
                manuscript_data = json.load(f)
            
            ms = manuscript_data.get("manuscript", {})
            total_words = ms.get("total_word_count", 0)
            total_scenes = ms.get("total_scenes", 0)
            total_chapters = ms.get("total_chapters", 0)
            
            print(f"\nGenerated Novel Quality:")
            print(f"  Chapters: {total_chapters}")
            print(f"  Scenes: {total_scenes}")
            print(f"  Words: {total_words:,}")
            
            quality = "EXCELLENT" if total_words > 8000 else \
                     "GOOD" if total_words > 5000 else \
                     "ACCEPTABLE" if total_words > 2000 else "POOR"
            print(f"  Quality Rating: {quality}")
            
            if total_chapters > 0:
                avg_words_per_chapter = total_words / total_chapters
                print(f"  Average words per chapter: {avg_words_per_chapter:.0f}")
            
            if total_scenes > 0:
                avg_words_per_scene = total_words / total_scenes  
                print(f"  Average words per scene: {avg_words_per_scene:.0f}")
        
        # Performance summary
        print(f"\nPerformance Summary:")
        if step_results:
            avg_step_time = total_step_time / len([r for r in step_results.values() if r["success"]])
            print(f"  Average successful step time: {avg_step_time:.1f}s")
        
        fastest_step = min(step_results.items(), key=lambda x: x[1]["time"]) if step_results else None
        slowest_step = max(step_results.items(), key=lambda x: x[1]["time"]) if step_results else None
        
        if fastest_step:
            print(f"  Fastest step: Step {fastest_step[0]} ({fastest_step[1]['time']:.1f}s)")
        if slowest_step:
            print(f"  Slowest step: Step {slowest_step[0]} ({slowest_step[1]['time']:.1f}s)")
        
        # Artifacts generated
        artifact_dir = Path(f"artifacts/{created_id}")
        if artifact_dir.exists():
            artifacts = list(artifact_dir.glob("*"))
            print(f"\nArtifacts Generated: {len(artifacts)} files")
            for artifact in sorted(artifacts):
                size_kb = artifact.stat().st_size / 1024
                print(f"  {artifact.name} ({size_kb:.1f} KB)")
        
        # Final verdict
        overall_success = successful_steps == 11 and export_success
        print(f"\n{'=' * 80}")
        print(f"FINAL RESULT: {'COMPLETE SUCCESS' if overall_success else 'PARTIAL SUCCESS' if successful_steps > 8 else 'FAILED'}")
        print(f"{'=' * 80}")
        
        if server_started:
            print(f"\n[MONITORING] Dashboard remains active at http://127.0.0.1:5000")
            print(f"[MONITORING] Press Ctrl+C to stop monitoring")
            
            # Keep server running for inspection
            try:
                print("[MONITORING] Monitoring active - press Enter to stop...")
                input()
            except KeyboardInterrupt:
                pass
        
        return overall_success
        
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test cancelled by user")
        return False
        
    finally:
        # Clean shutdown
        print(f"\n[CLEANUP] Shutting down...")
        try:
            stop_monitoring(project_id)
        except:
            pass
        
        if server_started:
            obs_server.stop()
            print(f"[CLEANUP] Monitoring server stopped")


if __name__ == "__main__":
    print("Snowflake Method Novel Generation - E2E Test with Full Observability")
    print("This test will run the complete pipeline with live monitoring dashboard")
    print("Press Ctrl+C at any time to cancel")
    print()
    
    try:
        success = run_e2e_with_monitoring()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(130)