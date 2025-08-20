#!/usr/bin/env python3
"""
Test GPT-5 directly with AIGenerator configured for OpenAI
"""
import os
import sys
sys.path.append('.')

def test_ai_generator_openai():
    """Test AIGenerator with OpenAI provider"""
    print("Testing AIGenerator with OpenAI provider...")
    
    try:
        from src.ai.generator import AIGenerator
        
        # Create AIGenerator with OpenAI provider
        generator = AIGenerator(provider="openai")
        
        # Simple test prompt
        prompt_data = {
            "system": "You are a helpful AI assistant.",
            "user": "Say 'GPT-5 via AIGenerator works!'"
        }
        
        # Configure for GPT-5 (must use temperature=1)
        model_config = {
            "model_name": "gpt-5",
            "temperature": 1.0,
            "max_tokens": 50
        }
        
        result = generator.generate(prompt_data, model_config)
        print(f"✅ GPT-5 via AIGenerator: {result}")
        return True
        
    except Exception as e:
        print(f"❌ AIGenerator OpenAI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_0_with_openai_generator():
    """Test Step 0 with AIGenerator configured for OpenAI"""
    print("\nTesting Step 0 with OpenAI AIGenerator...")
    
    try:
        from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
        from src.ai.generator import AIGenerator
        
        # Create step with OpenAI generator
        step0 = Step0FirstThingsFirst()
        step0.generator = AIGenerator(provider="openai")  # Override the generator
        
        story_brief = "A brilliant scientist discovers immortality but learns it destroys humanity."
        
        model_config = {
            "model_name": "gpt-5",
            "temperature": 1.0,  # GPT-5 only supports temperature=1
            "max_tokens": 1000
        }
        
        success, result, error = step0.execute(story_brief, model_config=model_config)
        
        if success:
            print(f"✅ Step 0 with GPT-5 success!")
            print(f"Category: {result.get('category', 'N/A')}")
            print(f"Target Audience: {result.get('target_audience', 'N/A')}")
            return result
        else:
            print(f"❌ Step 0 failed: {error}")
            return None
        
    except Exception as e:
        print(f"❌ Step 0 OpenAI test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("GPT-5 Direct AIGenerator Test")
    print("=" * 40)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ OpenAI API Key found")
    
    # Test AIGenerator directly
    ai_test = test_ai_generator_openai()
    
    # Test Step 0 with OpenAI generator
    step_test = test_step_0_with_openai_generator()
    
    if ai_test and step_test:
        print(f"\n🎉 GPT-5 working with Snowflake via OpenAI AIGenerator!")
    else:
        print(f"\n⚠️  Tests failed. Check configuration.")