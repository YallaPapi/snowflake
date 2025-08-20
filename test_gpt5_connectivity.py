#!/usr/bin/env python3
"""
Test GPT-5 connectivity and basic functionality
"""
import os
import sys
sys.path.append('.')

from src.ai.bulletproof_generator import get_bulletproof_generator
from src.ai.model_selector import ModelSelector

def test_gpt5_basic():
    """Test basic GPT-5 connectivity"""
    print("Testing GPT-5 connectivity...")
    
    # Get bulletproof generator
    generator = get_bulletproof_generator()
    
    # Simple test prompt
    prompt = {
        "system": "You are a helpful AI assistant. Respond concisely.",
        "user": "Please respond with exactly: 'GPT-5 is working correctly!'"
    }
    
    # Configure for OpenAI GPT-5
    config = {
        "model_name": "gpt-5",
        "provider": "openai",
        "temperature": 0.3,
        "max_tokens": 100
    }
    
    try:
        result = generator.generate_guaranteed(prompt, config)
        print(f"✅ GPT-5 Response: {result}")
        return True
    except Exception as e:
        print(f"❌ GPT-5 Test Failed: {e}")
        return False

def test_model_selector_gpt5():
    """Test model selector with GPT-5 configuration"""
    print("\nTesting Model Selector GPT-5 configuration...")
    
    # Test different step configurations
    for step in [0, 3, 6, 9, 10]:
        config = ModelSelector.get_model_config(step, provider="openai")
        print(f"Step {step}: {config['model_name']} (tier: {config['tier']})")
        
        if config['model_name'] != 'gpt-5':
            print(f"❌ Expected gpt-5, got {config['model_name']}")
            return False
    
    print("✅ All step configurations use GPT-5")
    return True

def test_snowflake_step_with_gpt5():
    """Test a simple snowflake step with GPT-5"""
    print("\nTesting Snowflake Step 1 with GPT-5...")
    
    try:
        from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
        
        step1 = Step1OneSentenceSummary()
        
        # Test input
        test_input = {
            "category": "Science Fiction",
            "target_audience": "Adult",
            "story_kind": "Character-driven thriller",
            "delight_statement": "A brilliant scientist discovers the secret to immortality but realizes the devastating cost to humanity"
        }
        
        # Override to use GPT-5
        result = step1.execute(test_input, model_override={"provider": "openai", "model_name": "gpt-5"})
        
        print(f"✅ Step 1 with GPT-5 Result: {result.get('one_sentence_summary', 'No result')}")
        return True
        
    except Exception as e:
        print(f"❌ Step 1 GPT-5 Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("GPT-5 Connectivity Test Suite")
    print("=" * 40)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ OpenAI API Key found")
    
    # Run tests
    tests = [
        test_gpt5_basic,
        test_model_selector_gpt5,
        test_snowflake_step_with_gpt5
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All GPT-5 tests passed! System ready to use GPT-5.")
    else:
        print("⚠️  Some tests failed. Check configuration.")