#!/usr/bin/env python3
"""
Test which models we can access
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Test OpenAI models
if os.getenv("OPENAI_API_KEY"):
    print("Testing OpenAI models...")
    from openai import OpenAI
    
    client = OpenAI()
    
    test_models = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
    
    for model in test_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'yes' if you work"}],
                max_tokens=10
            )
            print(f"  OK: {model} - {response.choices[0].message.content}")
        except Exception as e:
            print(f"  FAIL: {model} - {str(e)[:50]}")

# Test Anthropic models
if os.getenv("ANTHROPIC_API_KEY"):
    print("\nTesting Anthropic models...")
    from anthropic import Anthropic
    
    client = Anthropic()
    
    test_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    for model in test_models:
        try:
            response = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'yes' if you work"}],
                max_tokens=10
            )
            print(f"  OK: {model} - {response.content[0].text}")
        except Exception as e:
            print(f"  FAIL: {model} - {str(e)[:50]}")