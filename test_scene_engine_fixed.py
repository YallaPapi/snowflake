#!/usr/bin/env python3
"""
Test Scene Engine after fixing import issues
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_imports():
    """Test all critical imports are working"""
    print("=" * 60)
    print("TESTING SCENE ENGINE IMPORT FIXES")
    print("=" * 60)
    
    errors = []
    
    # Test Step 9 v2
    try:
        from src.pipeline.steps.step_9_scene_briefs_v2 import Step9SceneBriefsV2
        print("[PASS] Step 9 v2 imports successfully")
    except Exception as e:
        errors.append(f"Step 9 v2 import failed: {e}")
        print(f"[FAIL] Step 9 v2 import: {e}")
    
    # Test Step 10
    try:
        from src.pipeline.steps.step_10_first_draft import Step10FirstDraft
        print("[PASS] Step 10 imports successfully")
    except Exception as e:
        errors.append(f"Step 10 import failed: {e}")
        print(f"[FAIL] Step 10 import: {e}")
    
    # Test Orchestrator
    try:
        from src.pipeline.orchestrator import SnowflakePipeline
        print("[PASS] Orchestrator imports successfully")
    except Exception as e:
        errors.append(f"Orchestrator import failed: {e}")
        print(f"[FAIL] Orchestrator import: {e}")
    
    # Test Scene Engine models
    try:
        from src.scene_engine.models import SceneCard, SceneType
        print("[PASS] Scene Engine models import successfully")
    except Exception as e:
        errors.append(f"Scene Engine models import failed: {e}")
        print(f"[FAIL] Scene Engine models import: {e}")
    
    # Test Scene Engine Master
    try:
        from src.scene_engine.integration.master_service import SceneEngineMaster
        print("[PASS] Scene Engine Master imports successfully")
    except Exception as e:
        errors.append(f"Scene Engine Master import failed: {e}")
        print(f"[FAIL] Scene Engine Master import: {e}")
    
    # Test Scene Engine integration module
    try:
        from src.scene_engine.integration import (
            SceneEngineMaster,
            EngineConfiguration,
            EventSystem,
            SceneEngineAPI
        )
        print("[PASS] Scene Engine integration module imports successfully")
    except Exception as e:
        errors.append(f"Scene Engine integration import failed: {e}")
        print(f"[FAIL] Scene Engine integration import: {e}")
    
    print("=" * 60)
    
    if errors:
        print(f"\n{len(errors)} IMPORT ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\nALL IMPORTS WORKING! Scene Engine is ready.")
        return True

def test_instantiation():
    """Test that we can instantiate the main components"""
    print("\n" + "=" * 60)
    print("TESTING COMPONENT INSTANTIATION")
    print("=" * 60)
    
    errors = []
    
    # Test Step 9 instantiation
    try:
        from src.pipeline.steps.step_9_scene_briefs_v2 import Step9SceneBriefsV2
        step9 = Step9SceneBriefsV2()
        print("[PASS] Step 9 v2 instantiated successfully")
    except Exception as e:
        errors.append(f"Step 9 v2 instantiation failed: {e}")
        print(f"[FAIL] Step 9 v2 instantiation: {e}")
    
    # Test Step 10 instantiation
    try:
        from src.pipeline.steps.step_10_first_draft import Step10FirstDraft
        step10 = Step10FirstDraft()
        print("[PASS] Step 10 instantiated successfully")
    except Exception as e:
        errors.append(f"Step 10 instantiation failed: {e}")
        print(f"[FAIL] Step 10 instantiation: {e}")
    
    # Test Orchestrator instantiation
    try:
        from src.pipeline.orchestrator import SnowflakePipeline
        pipeline = SnowflakePipeline()
        print("[PASS] Orchestrator instantiated successfully")
    except Exception as e:
        errors.append(f"Orchestrator instantiation failed: {e}")
        print(f"[FAIL] Orchestrator instantiation: {e}")
    
    print("=" * 60)
    
    if errors:
        print(f"\n{len(errors)} INSTANTIATION ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\nALL COMPONENTS CAN BE INSTANTIATED!")
        return True

def main():
    """Run all tests"""
    print("\nSCENE ENGINE IMPORT FIX VERIFICATION")
    print("=" * 60)
    
    # Run import tests
    imports_ok = test_imports()
    
    # Run instantiation tests
    instantiation_ok = test_instantiation()
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    if imports_ok and instantiation_ok:
        print("[SUCCESS] All import issues have been fixed!")
        print("\nThe Scene Engine is now ready for use with:")
        print("  - Step 9 using the v2 implementation")
        print("  - Step 10 with all required dependencies")
        print("  - Orchestrator with correct imports")
        print("  - Scene Engine integration layer functional")
        return 0
    else:
        print("[FAILED] Some issues remain. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())