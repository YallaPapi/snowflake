#!/usr/bin/env python3
"""
Quick test of Step 7 generation
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

from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles

def quick_test():
    """Quick test of Step 7"""
    
    # Create minimal test data
    step5_artifact = {
        "characters": [
            {
                "name": "Sarah Chen",
                "role": "protagonist",
                "synopsis": "Sarah is a 32-year-old journalist haunted by past failures. She struggles with trust but must learn to rely on others to expose a conspiracy."
            },
            {
                "name": "Marcus Vale",
                "role": "antagonist", 
                "synopsis": "Marcus is a 45-year-old tech billionaire who believes his authoritarian vision will save humanity. His childhood trauma drives his need for control."
            }
        ]
    }
    
    print("Testing Step 7 Character Bibles...")
    print(f"Input: {len(step5_artifact['characters'])} characters")
    
    step7 = Step7CharacterBibles()
    
    # Use OpenAI with lower token limit for speed
    model_config = {
        "model_name": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 3000
    }
    
    print(f"Using model: {model_config['model_name']}")
    print("Generating...")
    
    success, artifact, message = step7.execute(
        step5_artifact=step5_artifact,
        project_id="quick_test_step7",
        model_config=model_config
    )
    
    if success:
        print(f"\nSUCCESS: {message}")
        
        bibles = artifact.get('bibles', [])
        print(f"Generated {len(bibles)} bibles")
        
        for bible in bibles:
            name = bible.get('name', 'Unknown')
            
            # Quick completeness check
            sections = ['physical', 'personality', 'environment', 'psychology']
            filled = sum(1 for s in sections if bible.get(s))
            
            print(f"\n  {name}:")
            print(f"    - Sections filled: {filled}/4")
            print(f"    - Voice notes: {len(bible.get('voice_notes', []))}")
            
            # Check if detailed fields exist
            if isinstance(bible.get('physical'), dict):
                phys_fields = len([k for k,v in bible['physical'].items() if v])
                print(f"    - Physical fields: {phys_fields}")
            
            if isinstance(bible.get('psychology'), dict):
                psych_fields = len([k for k,v in bible['psychology'].items() if v])
                print(f"    - Psychology fields: {psych_fields}")
        
        return True
    else:
        print(f"\nFAILED: {message}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)