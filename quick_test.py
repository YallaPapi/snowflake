#!/usr/bin/env python3
"""
Quick test for just the first 3 steps
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.ai.generator import AIGenerator

def test_step_by_step():
    """Test individual steps"""
    
    generator = AIGenerator(provider="openai")
    
    print("Testing GPT-5 step by step...")
    
    # Test Step 0
    print("\n=== STEP 0 ===")
    step0_prompt = {
        "system": "Generate story categorization data in JSON format.",
        "user": "Based on this story concept: A satirical near-future novel about time-debt. Return JSON with: category, story_kind, audience_delight"
    }
    
    # Test GPT-5-mini first
    print("\n=== TESTING GPT-5-MINI ===")
    try:
        result = generator.generate(step0_prompt, model_config={"model_name": "gpt-5-mini"})
        print(f"GPT-5-mini Success: {result[:200]}...")
    except Exception as e:
        print(f"GPT-5-mini Failed: {e}")
        
    # Test regular GPT-5 
    print("\n=== TESTING GPT-5 ===")
    try:
        result = generator.generate(step0_prompt, model_config={"model_name": "gpt-5"})
        print(f"GPT-5 Success: {result[:200]}...")
    except Exception as e:
        print(f"GPT-5 Failed: {e}")

if __name__ == "__main__":
    test_step_by_step()