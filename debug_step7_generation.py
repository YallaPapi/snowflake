#!/usr/bin/env python3
"""
Debug Step 7 generation to see what AI is producing
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from src.pipeline.prompts.step_7_prompt import Step7Prompt
from src.ai.generator import AIGenerator

def debug_step7():
    """Debug what Step 7 is generating"""
    
    # Load existing Step 5
    source_project = "smoketestnovel_20250819_153616"
    artifact_dir = Path("artifacts") / source_project
    
    with open(artifact_dir / "step_5_character_synopses.json", "r") as f:
        step5_artifact = json.load(f)
    
    print("Step 5 Characters:")
    for char in step5_artifact.get('characters', []):
        print(f"  - {char.get('name', 'Unknown')}: {char.get('role', 'Unknown')}")
    
    # Generate prompt
    prompt_gen = Step7Prompt()
    prompt = prompt_gen.generate_prompt(step5_artifact)
    
    print("\n" + "="*60)
    print("GENERATED PROMPT:")
    print("="*60)
    print("SYSTEM:", prompt['system'][:200] + "...")
    print("\nUSER:", prompt['user'][:500] + "...")
    
    # Try generating with OpenAI
    print("\n" + "="*60)
    print("GENERATING WITH OPENAI...")
    print("="*60)
    
    generator = AIGenerator(provider="openai")
    
    model_config = {
        "model_name": "gpt-4o",
        "temperature": 0.5,
        "max_tokens": 4000
    }
    
    try:
        # Generate raw text
        raw_response = generator.generate(prompt, model_config)
        print("\nRAW RESPONSE (first 1000 chars):")
        print(raw_response[:1000])
        
        # Try to parse as JSON
        print("\n" + "="*60)
        print("PARSING AS JSON...")
        print("="*60)
        
        try:
            parsed = json.loads(raw_response)
            print("Successfully parsed JSON!")
            print(f"Keys in response: {list(parsed.keys())}")
            
            if 'bibles' in parsed:
                print(f"Found 'bibles' with {len(parsed['bibles'])} entries")
                for bible in parsed['bibles'][:2]:
                    print(f"\nBible for: {bible.get('name', 'Unknown')}")
                    print(f"  Keys: {list(bible.keys())}")
            else:
                print("No 'bibles' key found in response")
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print("\nTrying to extract JSON from text...")
            
            # Try to find JSON in the text
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    print("Found and parsed JSON!")
                    print(f"Keys: {list(parsed.keys())}")
                except:
                    print("Still couldn't parse extracted JSON")
            
    except Exception as e:
        print(f"Generation failed: {e}")

if __name__ == "__main__":
    debug_step7()