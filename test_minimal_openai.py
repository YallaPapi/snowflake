#!/usr/bin/env python3
"""
Minimal OpenAI test to isolate the issue
"""
import os

# Clear any proxy-related environment variables
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
for var in proxy_vars:
    if var in os.environ:
        print(f"Clearing {var}: {os.environ[var]}")
        del os.environ[var]

try:
    print("Testing with minimal imports...")
    import httpx
    print(f"httpx version: {httpx.__version__}")
    
    # Test httpx client directly first
    print("Testing httpx client...")
    client = httpx.Client()
    print("✅ httpx client works")
    client.close()
    
    # Now test OpenAI
    from openai import OpenAI
    print("✅ OpenAI import works")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key")
        exit(1)
    
    # Try to create OpenAI client with minimal parameters
    print("Creating OpenAI client...")
    openai_client = OpenAI(api_key=api_key)
    print("✅ OpenAI client created successfully!")
    
    # Test a simple call
    print("Testing GPT-3.5-turbo...")
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'test'"}],
        max_tokens=5
    )
    print(f"✅ GPT-3.5-turbo works: {response.choices[0].message.content}")
    
    # Now test GPT-5
    print("Testing GPT-5...")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Say 'GPT-5 works'"}],
            max_completion_tokens=10
        )
        print(f"✅ GPT-5 works: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ GPT-5 error: {e}")
        if "does not exist" in str(e) or "invalid model" in str(e).lower():
            print("💡 GPT-5 may not be available yet, trying o1-preview instead...")
            try:
                response = openai_client.chat.completions.create(
                    model="o1-preview",
                    messages=[{"role": "user", "content": "Say 'o1-preview works'"}],
                    max_completion_tokens=10
                )
                print(f"✅ o1-preview works: {response.choices[0].message.content}")
            except Exception as e2:
                print(f"❌ o1-preview error: {e2}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()