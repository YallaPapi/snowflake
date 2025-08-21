#!/usr/bin/env python3
"""
Real-time monitoring test with immediate feedback
"""
import sys
import os
import time
import threading
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.ai.generator import AIGenerator

def monitor_progress(project_dir, project_name):
    """Monitor project directory for changes in real-time"""
    print("[MONITOR] Starting real-time file monitoring...")
    
    project_path = Path(project_dir) / project_name
    last_files = set()
    
    while True:
        time.sleep(2)  # Check every 2 seconds
        
        if project_path.exists():
            current_files = set(f.name for f in project_path.glob("*"))
            new_files = current_files - last_files
            
            for new_file in new_files:
                print(f"[MONITOR] NEW FILE: {new_file}")
                
                # Show status updates
                if new_file == "status.json":
                    try:
                        import json
                        status_file = project_path / "status.json"
                        with open(status_file) as f:
                            status = json.load(f)
                            current_step = status.get("current_step", "unknown")
                            print(f"[MONITOR] STATUS: Currently on step {current_step}")
                    except:
                        pass
            
            last_files = current_files

def test_with_monitoring():
    """Test GPT-5 with real-time monitoring"""
    
    print("REAL-TIME MONITORING TEST")
    print("=" * 50)
    
    generator = AIGenerator(provider="openai")
    
    # Start monitoring in background
    project_name = f"monitor_test_{int(time.time())}"
    monitor_thread = threading.Thread(target=monitor_progress, args=("artifacts", project_name))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    print(f"[TEST] Starting test with project: {project_name}")
    print("[TEST] Monitor thread started")
    print()
    
    # Test individual steps with immediate feedback
    step0_prompt = {
        "system": "Generate story categorization data in JSON format.",
        "user": "Story concept: Time-debt satire. Return JSON with: category, story_kind, audience_delight"
    }
    
    try:
        print("[TEST] === STEP 0 TEST ===")
        print("[TEST] Starting GPT-5-mini request...")
        
        start_time = time.time()
        result = generator.generate(step0_prompt, model_config={"model_name": "gpt-5-mini"})
        duration = time.time() - start_time
        
        print(f"[TEST] COMPLETED in {duration:.1f}s")
        print(f"[TEST] Result: {result[:150]}...")
        print()
        
        print("[TEST] === STEP 1 TEST ===")
        step1_prompt = {
            "system": "Create a one-sentence story summary (max 25 words).",
            "user": "Story: Casey sells 10 years of life, must steal them back from time-repo agents."
        }
        
        print("[TEST] Starting GPT-5-mini request...")
        start_time = time.time()
        result = generator.generate(step1_prompt, model_config={"model_name": "gpt-5-mini"})
        duration = time.time() - start_time
        
        print(f"[TEST] COMPLETED in {duration:.1f}s")
        print(f"[TEST] Result: {result}")
        print()
        
        print("[TEST] All tests completed successfully!")
        
    except Exception as e:
        print(f"[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Keep monitoring for a bit
    print("[TEST] Monitoring for 10 more seconds...")
    time.sleep(10)

if __name__ == "__main__":
    test_with_monitoring()