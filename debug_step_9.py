#!/usr/bin/env python3
"""Debug Step 9 to find the exact error"""

from src.pipeline.steps.step_9_scene_briefs import Step9SceneBriefs
from pathlib import Path
import json
import traceback

# Load Step 8 artifact
project_id = "smoketestnovel_20250819_153616"
step8_path = Path(f"artifacts/{project_id}/step_8_scene_list.json")

with open(step8_path, 'r') as f:
    step8_artifact = json.load(f)

print(f"Step 8 has {len(step8_artifact.get('scenes', []))} scenes")

# Create Step 9 executor
step9 = Step9SceneBriefs()

# Generate prompt
try:
    prompt = step9.prompt_generator.generate_prompt(step8_artifact)
    print(f"Prompt generated successfully")
    print(f"Prompt is asking for {prompt['user'].count('scene_count')} scene briefs")
except Exception as e:
    print(f"Error generating prompt: {e}")
    traceback.print_exc()
    exit(1)

# Try to generate
model_config = {
    "temperature": 0.4,
    "max_tokens": 4000
}

print("\nAttempting generation...")
try:
    # First try raw generation to see what we get
    raw_output = step9.generator.generate(prompt, model_config)
    print(f"Raw output type: {type(raw_output)}")
    print(f"Raw output length: {len(str(raw_output))}")
    
    if isinstance(raw_output, str):
        # Try to parse
        if raw_output.strip().startswith('{'):
            try:
                parsed = json.loads(raw_output)
                print(f"Parsed as JSON. Keys: {list(parsed.keys())}")
                if 'scene_briefs' in parsed:
                    print(f"scene_briefs is a {type(parsed['scene_briefs'])}")
                    if isinstance(parsed['scene_briefs'], list):
                        print(f"Has {len(parsed['scene_briefs'])} briefs")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
    
    # Now try with validation
    print("\nTrying with validation...")
    content = step9.generator.generate_with_validation(
        prompt,
        step9.validator,
        model_config,
        max_attempts=1
    )
    print(f"Content type: {type(content)}")
    if isinstance(content, dict):
        print(f"Content keys: {list(content.keys())}")
    
except Exception as e:
    print(f"Error during generation: {e}")
    print(f"Error type: {type(e)}")
    traceback.print_exc()