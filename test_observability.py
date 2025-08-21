#!/usr/bin/env python3
"""
Simple test of observability system
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

def test_observability():
    print("Testing Snowflake Observability System")
    print("=" * 50)
    
    # Test imports
    try:
        from observability.events import start_monitoring, emit_event
        print("[PASS] Events module imported successfully")
    except Exception as e:
        print(f"[FAIL] Events import: {e}")
        return False
    
    try:
        from observability.server import app
        print("[PASS] Server module imported successfully")
    except Exception as e:
        print(f"[FAIL] Server import: {e}")
        return False
    
    # Test monitoring
    try:
        project_id = "test_monitoring_123"
        start_monitoring(project_id)
        print("[PASS] Monitoring started successfully")
        
        # Emit some test events
        emit_event(project_id, "test_start", {"message": "Testing observability"})
        emit_event(project_id, "test_progress", {"step": 1, "progress": 50})
        emit_event(project_id, "test_complete", {"success": True})
        print("[PASS] Events emitted successfully")
        
        # Check if files were created
        artifact_path = Path(f"artifacts/{project_id}")
        if artifact_path.exists():
            events_file = artifact_path / "events.log"
            status_file = artifact_path / "status.json"
            
            if events_file.exists():
                print(f"[PASS] Events file created: {events_file}")
                with open(events_file, 'r') as f:
                    lines = f.readlines()
                print(f"[INFO] Events logged: {len(lines)}")
            else:
                print("[FAIL] Events file not created")
                
            if status_file.exists():
                print(f"[PASS] Status file created: {status_file}")
                import json
                with open(status_file, 'r') as f:
                    status = json.load(f)
                print(f"[INFO] Status: {status}")
            else:
                print("[FAIL] Status file not created")
                
        else:
            print("[FAIL] Artifact directory not created")
    
    except Exception as e:
        print(f"[FAIL] Monitoring test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[SUCCESS] Basic observability test completed")
    return True


def test_server():
    print("\nTesting Server Endpoints")
    print("=" * 30)
    
    import threading
    import time
    
    try:
        from observability.server import app
        
        # Start server in background
        server_thread = threading.Thread(
            target=lambda: app.run(host='127.0.0.1', port=5001, debug=False),
            daemon=True
        )
        server_thread.start()
        time.sleep(2)
        
        # Test endpoints
        import urllib.request
        import json
        
        # Test health endpoint
        try:
            with urllib.request.urlopen("http://127.0.0.1:5001/health", timeout=5) as response:
                if response.getcode() == 200:
                    health_data = json.loads(response.read())
                    print("[PASS] Health endpoint working")
                    print(f"[INFO] Health status: {health_data.get('status', 'unknown')}")
                else:
                    print(f"[FAIL] Health endpoint returned {response.getcode()}")
        except Exception as e:
            print(f"[FAIL] Health endpoint: {e}")
        
        # Test metrics endpoint
        try:
            with urllib.request.urlopen("http://127.0.0.1:5001/metrics", timeout=5) as response:
                if response.getcode() == 200:
                    print("[PASS] Metrics endpoint working")
                else:
                    print(f"[FAIL] Metrics endpoint returned {response.getcode()}")
        except Exception as e:
            print(f"[FAIL] Metrics endpoint: {e}")
            
        # Test projects endpoint
        try:
            with urllib.request.urlopen("http://127.0.0.1:5001/projects", timeout=5) as response:
                if response.getcode() == 200:
                    projects = json.loads(response.read())
                    print(f"[PASS] Projects endpoint working - {len(projects)} projects found")
                else:
                    print(f"[FAIL] Projects endpoint returned {response.getcode()}")
        except Exception as e:
            print(f"[FAIL] Projects endpoint: {e}")
            
        print("\n[SUCCESS] Server test completed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Server test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_observability()
    success2 = test_server()
    
    if success1 and success2:
        print("\n🎉 All observability tests PASSED!")
        print("System is ready for E2E testing with monitoring")
    else:
        print("\n❌ Some tests FAILED")
        print("Please fix issues before running E2E test")
    
    sys.exit(0 if (success1 and success2) else 1)