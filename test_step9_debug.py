#!/usr/bin/env python3
"""Debug Step 9 generation to see what AI is producing"""

import json as json_module
from pathlib import Path
from src.pipeline.steps.step_9_scene_briefs import Step9SceneBriefs

def test_step_9_debug():
    # Load existing Step 8 artifact
    step8_path = Path("artifacts/smoketestnovel_20250819_153616/step_8_scene_list.json")
    
    with open(step8_path, "r", encoding="utf-8") as f:
        step8_artifact = json_module.load(f)
    
    print(f"Loaded Step 8 with {len(step8_artifact.get('scenes', []))} scenes")
    
    # Initialize Step 9
    step9 = Step9SceneBriefs(project_dir="test_artifacts")
    
    # Bypass validation temporarily to see what's generated
    from src.ai.generator import AIGenerator
    from src.pipeline.prompts.step_9_prompt import Step9Prompt
    
    generator = AIGenerator()
    prompt_gen = Step9Prompt()
    
    # Generate for first batch only
    scenes = step8_artifact.get("scenes", [])[:5]
    prompt = prompt_gen.generate_batch_prompt(step8_artifact, scenes, 0)
    
    print("\nGenerating batch of 5 scene briefs...")
    print("\nPROMPT:")
    print(prompt["user"][:500] + "...")
    
    response = generator.generate(prompt, {"temperature": 0.3, "max_tokens": 2000})
    
    print("\nRESPONSE:")
    print(response[:1000])
    
    # Try to parse
    try:
        data = json_module.loads(response)
        print(f"\nParsed {len(data)} briefs")
        for i, brief in enumerate(data[:2]):
            print(f"\nBrief {i+1}:")
            print(json_module.dumps(brief, indent=2)[:500])
    except:
        print("\nCouldn't parse as JSON, raw response shown above")

if __name__ == "__main__":
    test_step_9_debug()