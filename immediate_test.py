#!/usr/bin/env python3
"""
Immediate feedback test - no waiting, instant results
"""
import sys
import os
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.ai.generator import AIGenerator

def main():
    print("IMMEDIATE FEEDBACK TEST - GPT-5 VARIANTS")
    print("=" * 50)
    
    generator = AIGenerator(provider="openai")
    
    # Simple test prompt
    prompt = {
        "system": "You are helpful. Respond concisely.",
        "user": "Say hello and tell me what model you are."
    }
    
    models_to_test = ["gpt-5-mini", "gpt-5"]
    
    for model in models_to_test:
        print(f"\nTESTING: {model}")
        print("-" * 30)
        
        try:
            print(f"[START] {model} request initiated")
            start = time.time()
            
            result = generator.generate(prompt, model_config={"model_name": model})
            
            duration = time.time() - start
            print(f"[DONE] {model} completed in {duration:.1f}s")
            print(f"[RESULT] {result}")
            
        except Exception as e:
            print(f"[ERROR] {model} failed: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()