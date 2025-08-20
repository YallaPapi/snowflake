#!/usr/bin/env python3
"""
Test GPT-5 with the Snowflake pipeline
"""
import os
import sys
sys.path.append('.')

def test_gpt5_step_0():
    """Test Step 0 with GPT-5"""
    print("Testing Step 0 with GPT-5...")
    
    try:
        from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
        
        step0 = Step0FirstThingsFirst()
        
        # Test input
        story_brief = "A brilliant scientist discovers the secret to immortality but realizes the devastating cost to humanity when everyone stops dying and society collapses."
        
        # Use GPT-5 via model config
        model_config = {
            "provider": "openai", 
            "model_name": "gpt-5",
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        success, result, error = step0.execute(story_brief, model_config=model_config)
        
        if not success:
            print(f"❌ Step 0 failed: {error}")
            return None
        
        print(f"✅ Step 0 with GPT-5 Success!")
        print(f"Category: {result.get('category', 'N/A')}")
        print(f"Target Audience: {result.get('target_audience', 'N/A')}")
        print(f"Story Kind: {result.get('story_kind', 'N/A')}")
        print(f"Delight Statement: {result.get('delight_statement', 'N/A')}")
        return result
        
    except Exception as e:
        print(f"❌ Step 0 GPT-5 Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_gpt5_step_1(step_0_result):
    """Test Step 1 with GPT-5"""
    if not step_0_result:
        print("❌ Skipping Step 1 - Step 0 failed")
        return None
        
    print("\nTesting Step 1 with GPT-5...")
    
    try:
        from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
        
        step1 = Step1OneSentenceSummary()
        
        # Use GPT-5 via model config
        model_config = {
            "provider": "openai",
            "model_name": "gpt-5", 
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        success, result, error = step1.execute(step_0_result, model_config=model_config)
        
        if not success:
            print(f"❌ Step 1 failed: {error}")
            return None
        
        print(f"✅ Step 1 with GPT-5 Success!")
        print(f"One Sentence Summary: {result.get('one_sentence_summary', 'N/A')}")
        return result
        
    except Exception as e:
        print(f"❌ Step 1 GPT-5 Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("GPT-5 Snowflake Pipeline Test")
    print("=" * 40)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ OpenAI API Key found")
    
    # Test Step 0
    step_0_result = test_gpt5_step_0()
    
    # Test Step 1
    step_1_result = test_gpt5_step_1(step_0_result)
    
    if step_0_result and step_1_result:
        print(f"\n🎉 GPT-5 successfully working with Snowflake pipeline!")
        print("Ready to generate novels with GPT-5.")
    else:
        print(f"\n⚠️  Some tests failed. Check configuration.")