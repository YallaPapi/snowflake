#!/usr/bin/env python3
"""
Direct test of OpenAI client configuration
"""
import os

def test_openai_client():
    """Test OpenAI client directly"""
    print("Testing OpenAI client...")
    
    try:
        from openai import OpenAI
        print("✅ OpenAI import successful")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OpenAI API key found")
            return False
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Try to create client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        # Try a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Start with a known working model
            messages=[
                {"role": "user", "content": "Say 'Hello from GPT!'"}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        print(f"✅ OpenAI API call successful: {response.choices[0].message.content}")
        
        # Now try GPT-5
        try:
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "user", "content": "Say 'Hello from GPT-5!'"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            print(f"✅ GPT-5 API call successful: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"❌ GPT-5 specific error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_openai_client()