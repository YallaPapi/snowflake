#!/usr/bin/env python3
"""
Debug Step 7 with direct generation
"""

import json
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

from src.ai.generator import AIGenerator
from src.pipeline.prompts.step_7_prompt import Step7Prompt
from src.pipeline.validators.step_7_validator import Step7Validator

def debug_generation():
    """Debug generation directly"""
    
    # Minimal test data
    step5_artifact = {
        "characters": [
            {
                "name": "John Doe",
                "role": "protagonist",
                "synopsis": "A detective solving crimes."
            }
        ]
    }
    
    print("Creating prompt...")
    prompt_gen = Step7Prompt()
    prompt = prompt_gen.generate_prompt(step5_artifact)
    
    print("\nPrompt preview:")
    print("System:", prompt['system'][:100])
    print("User:", prompt['user'][:200])
    
    print("\nGenerating with OpenAI...")
    generator = AIGenerator(provider="openai")
    
    model_config = {
        "model_name": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 2000
    }
    
    # Generate once without validation loop
    raw_output = generator.generate(prompt, model_config, max_retries=1)
    
    print("\nRaw output (first 500 chars):")
    print(raw_output[:500])
    
    # Check for markdown
    if "```" in raw_output:
        print("\nFound markdown code blocks")
        import re
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print(f"Extracted JSON ({len(json_str)} chars)")
            
            try:
                parsed = json.loads(json_str)
                print(f"Successfully parsed! Keys: {list(parsed.keys())}")
                
                if 'bibles' in parsed:
                    print(f"Found {len(parsed['bibles'])} bibles")
                    
                    # Validate
                    validator = Step7Validator()
                    is_valid, errors = validator.validate(parsed)
                    
                    if is_valid:
                        print("VALIDATION PASSED!")
                    else:
                        print(f"Validation errors: {errors[:3]}")
                        
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
    else:
        print("\nNo markdown found, trying direct JSON parse...")
        try:
            parsed = json.loads(raw_output)
            print(f"Success! Keys: {list(parsed.keys())}")
        except:
            print("Failed to parse as JSON")

if __name__ == "__main__":
    debug_generation()