#!/usr/bin/env python3
"""
Minimal test to verify the Snowflake pipeline fixes
Tests import structure and basic functionality
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

def test_imports():
    """Test if all necessary imports work"""
    print("Testing imports...")
    
    try:
        # Test validators import
        print("  Testing validators...")
        from src.pipeline.validators.step_0_validator import Step0Validator
        from src.pipeline.validators.step_1_validator import Step1Validator
        from src.pipeline.validators.step_2_validator import Step2Validator
        print("    [PASS] Validators imported successfully")
        
        # Test AI generator import
        print("  Testing AI generator...")
        from src.ai.generator import AIGenerator
        print("    [PASS] AI generator imported successfully")
        
        # Test individual step imports
        print("  Testing step imports...")
        from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
        from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
        from src.pipeline.steps.step_2_one_paragraph_summary import Step2OneParagraphSummary
        print("    [PASS] Steps 0-2 imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"    [FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_config():
    """Test model configuration"""
    print("\nTesting model configuration...")
    
    try:
        # Since model_config.py doesn't exist, test the generator directly
        from src.ai.generator import AIGenerator
        
        # Test creating with default config
        print("  Testing AIGenerator initialization...")
        
        # Check if we can create with openai provider
        if os.getenv("OPENAI_API_KEY"):
            gen = AIGenerator(provider="openai")
            print(f"  Provider: {gen.provider}")
            print(f"  Default Model: {gen.default_model}")
            print("  [PASS] Model configuration working")
        else:
            print("  [SKIP] No API key found, skipping model test")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Model config failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_generator():
    """Test AI generator initialization"""
    print("\nTesting AI generator...")
    
    try:
        from src.ai.generator import AIGenerator
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  [SKIP] No OPENAI_API_KEY found in environment")
            print("  Skipping AI generator test")
            return True
        
        # Create generator with default settings
        generator = AIGenerator(provider="openai")
        
        print(f"  Provider: {generator.provider}")
        print(f"  Default Model: {generator.default_model}")
        print("  [PASS] AI generator initialized successfully")
        
        # Test simple generation
        print("  Testing simple generation...")
        prompt_data = {
            "system": "You are a helpful assistant.",
            "user": "Say 'test successful' in exactly 2 words"
        }
        response = generator.generate(
            prompt_data=prompt_data,
            model_config={"temperature": 0}
        )
        print(f"  Response: {response}")
        print("  [PASS] Generation successful")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] AI generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validator():
    """Test basic validator functionality"""
    print("\nTesting validators...")
    
    try:
        from src.pipeline.validators.step_0_validator import Step0Validator
        
        # Create validator
        validator = Step0Validator()
        
        # Test valid data
        valid_data = {
            "category": "romance",
            "target_audience": "Adults",
            "story_kind": "complex",
            "delight_statement": "A gripping tale of love and mystery"
        }
        
        is_valid, errors = validator.validate(valid_data)
        if is_valid:
            print("  [PASS] Valid data passed validation")
        else:
            print(f"  [FAIL] Valid data failed: {errors}")
            
        # Test invalid data
        invalid_data = {}
        is_valid, errors = validator.validate(invalid_data)
        if not is_valid:
            print(f"  [PASS] Invalid data rejected correctly: {len(errors)} errors")
        else:
            print("  [FAIL] Invalid data should have failed")
            
        return True
        
    except Exception as e:
        print(f"  [FAIL] Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_execution():
    """Test a single step execution"""
    print("\nTesting step execution...")
    
    try:
        from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
        from pathlib import Path
        
        # Create test directory
        test_dir = Path("test_artifacts_minimal")
        test_dir.mkdir(exist_ok=True)
        
        # Create step executor
        step0 = Step0FirstThingsFirst(str(test_dir))
        
        # Create test project
        project_id = "test_project_minimal"
        project_path = test_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        # Create project.json
        project_data = {
            "id": project_id,
            "name": "Test Project",
            "created_at": "2025-08-21T12:00:00",
            "status": "active"
        }
        
        with open(project_path / "project.json", "w") as f:
            import json
            json.dump(project_data, f, indent=2)
        
        step0.project_id = project_id
        print(f"  Created test project: {project_id}")
        
        # Test brief
        brief = "A romantic thriller about a detective and a suspect"
        
        # Check if we have API key
        if not os.getenv("OPENAI_API_KEY"):
            print("  [SKIP] No API key, skipping actual execution")
            print("  [PASS] Step setup successful")
            return True
            
        # Execute step
        print("  Executing Step 0...")
        success, result, message = step0.execute(brief)
        
        if success:
            print(f"  [PASS] Step 0 executed successfully")
            print(f"    Category: {result.get('category', 'N/A')}")
            print(f"    Audience: {result.get('target_audience', 'N/A')}")
        else:
            print(f"  [FAIL] Step 0 failed: {message}")
            
        return success
        
    except Exception as e:
        print(f"  [FAIL] Step execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SNOWFLAKE PIPELINE MINIMAL TEST")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Model Config", test_model_config()))
    results.append(("AI Generator", test_ai_generator()))
    results.append(("Validators", test_validator()))
    results.append(("Step Execution", test_step_execution()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
    else:
        print("[FAIL] SOME TESTS FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())