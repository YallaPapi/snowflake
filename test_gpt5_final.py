#!/usr/bin/env python3
"""
Final verification that GPT-5 is working as the primary model
"""
import os
import sys
sys.path.append('.')

def test_default_provider():
    """Test that OpenAI is now the default provider"""
    print("Testing default provider selection...")
    
    try:
        from src.ai.generator import AIGenerator
        
        # Create default AIGenerator (should auto-select OpenAI)
        generator = AIGenerator()
        
        print(f"✅ Default provider: {generator.provider}")
        print(f"✅ Default model: {generator.default_model}")
        
        if generator.provider == "openai" and generator.default_model == "gpt-5":
            return True
        else:
            print(f"❌ Expected OpenAI/GPT-5, got {generator.provider}/{generator.default_model}")
            return False
        
    except Exception as e:
        print(f"❌ Default provider test failed: {e}")
        return False

def test_model_selector_gpt5():
    """Test model selector configurations"""
    print("\nTesting ModelSelector with GPT-5...")
    
    try:
        from src.ai.model_selector import ModelSelector
        
        configs = []
        for step in [0, 3, 6, 9]:
            config = ModelSelector.get_model_config(step, provider="openai")
            configs.append((step, config))
            print(f"Step {step}: {config['model_name']} (temp: {config['temperature']})")
        
        # Verify all use GPT-5 with temperature=1.0
        for step, config in configs:
            if config['model_name'] != 'gpt-5':
                print(f"❌ Step {step} not using GPT-5")
                return False
            if config['temperature'] != 1.0:
                print(f"❌ Step {step} temperature not 1.0")
                return False
        
        print("✅ All steps configured for GPT-5 with correct temperature")
        return True
        
    except Exception as e:
        print(f"❌ ModelSelector test failed: {e}")
        return False

def test_simple_generation():
    """Test simple generation with GPT-5"""
    print("\nTesting simple generation...")
    
    try:
        from src.ai.generator import AIGenerator
        
        generator = AIGenerator()
        
        prompt_data = {
            "system": "You are a helpful assistant.",
            "user": "Respond with exactly: 'GPT-5 is ready for novel generation!'"
        }
        
        result = generator.generate(prompt_data)
        print(f"✅ Generation result: {result.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("GPT-5 Final Configuration Test")
    print("=" * 40)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ OpenAI API Key found")
    
    # Run tests
    tests = [
        test_default_provider,
        test_model_selector_gpt5,
        test_simple_generation
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
        print("🎉 GPT-5 fully configured and ready for Snowflake novel generation!")
        print("🚀 You can now run: python generate_immortality_tax.py")
    else:
        print("⚠️  Some tests failed. Check configuration.")