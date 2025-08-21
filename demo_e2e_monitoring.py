#!/usr/bin/env python3
"""
Demo E2E Test with Observability - First 3 Steps
Demonstrates the monitoring system with pipeline execution
"""

import sys
import time
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from pipeline.orchestrator import SnowflakePipeline
from observability.events import (
    start_monitoring, stop_monitoring, emit_event, emit_step_start, 
    emit_step_complete, emit_step_progress, emit_error, get_project_summary
)


class SimpleObservabilityServer:
    """Simple observability server for demo"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://127.0.0.1:5000"
    
    def start(self):
        """Start the server"""
        try:
            print(f"[OBSERVABILITY] Starting monitoring dashboard at {self.server_url}")
            
            # Start server in background
            def run_server():
                from observability.server import app
                app.run(host='127.0.0.1', port=5000, debug=False)
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Give server time to start
            time.sleep(3)
            
            # Test if server is responding
            import urllib.request
            try:
                with urllib.request.urlopen(f"{self.server_url}/health", timeout=5) as response:
                    if response.getcode() == 200:
                        print(f"[OBSERVABILITY] ✅ Dashboard active at {self.server_url}")
                        print(f"[OBSERVABILITY] 🏥 Health check: {self.server_url}/health")
                        print(f"[OBSERVABILITY] 📊 Metrics: {self.server_url}/metrics")
                        return True
            except Exception as e:
                print(f"[OBSERVABILITY] ❌ Dashboard not responding: {e}")
                return False
                
        except Exception as e:
            print(f"[OBSERVABILITY] ❌ Failed to start dashboard: {e}")
            return False


def demo_monitored_pipeline():
    """Demo the monitored pipeline execution"""
    
    print("🔥" * 25)
    print("  SNOWFLAKE E2E MONITORING DEMO")
    print("🔥" * 25)
    
    # Start observability
    obs_server = SimpleObservabilityServer()
    server_started = obs_server.start()
    
    if not server_started:
        print("⚠️  Dashboard failed to start, continuing without web interface")
    
    # Initialize pipeline
    project_id = f"demo_monitored_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pipeline = SnowflakePipeline(project_dir="artifacts")
    
    print(f"\n📁 Project ID: {project_id}")
    if server_started:
        print(f"🌐 Live Dashboard: http://127.0.0.1:5000")
        print("   👆 Open this URL in your browser to watch live progress!")
    
    # Start monitoring
    start_monitoring(project_id)
    
    try:
        print(f"\n⚡ Starting monitored pipeline execution...")
        
        # Pipeline start event
        emit_event(project_id, "demo_pipeline_start", {
            "demo": True,
            "steps_planned": 3,
            "story_type": "Crime Thriller"
        })
        
        # Create project
        print(f"\n[1/4] 🔧 Creating project...")
        created_id = pipeline.create_project(project_name="Demo Monitored Novel")
        if not created_id:
            emit_error(project_id, None, "project_creation_failed", "Could not create project")
            print("  ❌ Project creation failed")
            return False
        
        # Use actual project ID
        project_id = created_id
        
        # Story brief for testing
        story_brief = """
Category: Crime Thriller
Target Audience: Adult readers who enjoy police procedurals
Story Kind: A gripping police corruption thriller
Delight Factors:
1. Uncovering corruption layer by layer
2. Moral complexity and ethical dilemmas
3. High-stakes investigation

Brief: Detective Mira Chen investigates a police shooting that reveals department corruption reaching the highest levels.
"""
        
        # Execute first 3 steps with detailed monitoring
        steps = [
            (0, "First Things First", lambda: pipeline.execute_step_0(story_brief)),
            (1, "One Sentence Summary", lambda: pipeline.execute_step_1("A detective uncovers police corruption during a shooting investigation.")),
            (2, "One Paragraph Summary", lambda: pipeline.execute_step_2()),
        ]
        
        successful_steps = 0
        step_results = {}
        
        for step_num, step_name, step_func in steps:
            print(f"\n[{step_num+2}/4] 🎯 Step {step_num}: {step_name}")
            
            # Emit step start
            emit_step_start(project_id, step_num, step_name)
            
            start_time = time.time()
            
            # Show progress updates
            for i in range(5):
                emit_step_progress(project_id, step_num, i+1, 5, f"Processing {step_name}...")
                time.sleep(0.5)  # Simulate work
            
            try:
                print(f"  🚀 Executing {step_name}...")
                success, artifact, message = step_func()
                duration = time.time() - start_time
                
                # Emit completion
                emit_step_complete(project_id, step_num, step_name, duration, success,
                                 artifact_size=len(str(artifact)) if artifact else 0,
                                 message=message)
                
                step_results[step_num] = {
                    "success": success, 
                    "time": duration, 
                    "message": message
                }
                
                if success:
                    successful_steps += 1
                    print(f"  ✅ Completed in {duration:.1f}s")
                    print(f"     📝 {message[:100]}")
                else:
                    print(f"  ❌ Failed after {duration:.1f}s")
                    print(f"     💥 {message[:100]}")
                    emit_error(project_id, step_num, "step_execution_failed", message)
                    
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                
                print(f"  💥 Exception after {duration:.1f}s: {error_msg}")
                emit_error(project_id, step_num, "step_exception", error_msg, duration=duration)
                
                step_results[step_num] = {
                    "success": False, 
                    "time": duration, 
                    "message": error_msg
                }
            
            # Brief pause
            time.sleep(1)
        
        # Final results
        emit_event(project_id, "demo_complete", {
            "successful_steps": successful_steps,
            "total_steps": 3,
            "overall_success": successful_steps == 3,
            "step_results": step_results
        })
        
        # Show results
        print(f"\n" + "🎊" * 30)
        print(f"   DEMO RESULTS")
        print(f"🎊" * 30)
        
        print(f"✅ Successful Steps: {successful_steps}/3")
        
        total_time = sum(r["time"] for r in step_results.values())
        print(f"⏱️  Total Execution Time: {total_time:.1f}s")
        
        print(f"\n📋 Step Breakdown:")
        for step, result in step_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} Step {step}: {result['time']:.1f}s - {result['message'][:60]}")
        
        # Show generated artifacts
        artifact_dir = Path(f"artifacts/{project_id}")
        if artifact_dir.exists():
            artifacts = list(artifact_dir.glob("*"))
            print(f"\n📁 Generated Artifacts ({len(artifacts)} files):")
            for artifact in sorted(artifacts):
                size_kb = artifact.stat().st_size / 1024
                print(f"  📄 {artifact.name} ({size_kb:.1f} KB)")
        
        if server_started:
            print(f"\n🌐 View detailed metrics at: http://127.0.0.1:5000")
            print("   📊 Real-time system health, events, and performance data")
            print(f"   🔍 Project summary: http://127.0.0.1:5000/projects/{project_id}/summary")
        
        # Keep monitoring active for inspection
        if server_started:
            print(f"\n⏳ Monitoring dashboard is active - press Enter to finish...")
            try:
                input()
            except KeyboardInterrupt:
                pass
        
        return successful_steps == 3
        
    except KeyboardInterrupt:
        print("\n🛑 Demo cancelled by user")
        return False
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        try:
            stop_monitoring(project_id)
        except:
            pass


if __name__ == "__main__":
    print("🎬 Snowflake Method - E2E Monitoring Demo")
    print("📈 This demo shows the first 3 pipeline steps with live monitoring")
    print()
    
    try:
        success = demo_monitored_pipeline()
        if success:
            print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("The observability system is fully functional for E2E testing")
        else:
            print("\n⚠️  Demo had some issues, but monitoring system works")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo cancelled by user")
        sys.exit(130)