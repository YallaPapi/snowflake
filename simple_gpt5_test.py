#!/usr/bin/env python3
"""
Simple GPT-5 connectivity test without Unicode characters
"""
import os
import sys
sys.path.append('.')

# Load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not available, using system environment")

def test_gpt5_basic():
    """Test basic GPT-5 connectivity"""
    print("Testing GPT-5 connectivity...")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    print("OpenAI API Key found")
    
    try:
        from openai import OpenAI
        client = OpenAI()
        
        # Simple test with GPT-5 (very minimal parameters)
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )
        
        print(f"Full response: {response}")
        print(f"Choices: {response.choices}")
        print(f"Choice 0: {response.choices[0]}")
        print(f"Message: {response.choices[0].message}")
        
        result = response.choices[0].message.content
        print(f"GPT-5 Response: '{result}'")
        print(f"Response type: {type(result)}")
        print(f"Response length: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print("SUCCESS: GPT-5 connectivity test passed")
            return True
        else:
            print("ERROR: GPT-5 returned empty response")
            return False
            
    except Exception as e:
        print(f"ERROR: GPT-5 Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("GPT-5 Simple Connectivity Test")
    print("=" * 40)
    success = test_gpt5_basic()
    if success:
        print("Test completed successfully")
    else:
        print("Test failed")