#!/usr/bin/env python3
"""Debug Step 6 generation to see what's actually happening"""

from src.pipeline.steps.step_6_long_synopsis import Step6LongSynopsis
from pathlib import Path
import json

# Load Step 4 artifact
project_id = "smoketestnovel_20250819_153616"
step4_path = Path(f"artifacts/{project_id}/step_4_one_page_synopsis.json")

with open(step4_path, 'r') as f:
    step4_artifact = json.load(f)

print("Step 4 artifact loaded")
print(f"Step 4 has {len(str(step4_artifact))} chars total")

# Create Step 6 executor
step6 = Step6LongSynopsis()

# Generate prompt
prompt = step6.prompt_generator.generate_prompt(step4_artifact)
print("\n" + "="*60)
print("PROMPT BEING SENT:")
print("="*60)
print(f"System: {prompt['system'][:200]}...")
print(f"\nUser: {prompt['user'][:500]}...")

# Try to generate with explicit config
model_config = {
    "temperature": 0.5,
    "max_tokens": 4000
}

print("\n" + "="*60)
print("GENERATING WITH AI...")
print("="*60)

# Generate directly without validation first to see raw output
raw_output = step6.generator.generate(prompt, model_config)

print(f"\nRaw output type: {type(raw_output)}")
print(f"Raw output length: {len(raw_output) if isinstance(raw_output, str) else 'N/A'}")

if isinstance(raw_output, str):
    print(f"\nFirst 500 chars of raw output:")
    print(raw_output[:500])
    
    # Try to parse as JSON
    try:
        parsed = json.loads(raw_output)
        print(f"\nParsed as JSON successfully")
        if "long_synopsis" in parsed:
            synopsis_len = len(parsed["long_synopsis"])
            print(f"long_synopsis length: {synopsis_len} chars")
            print(f"Word count estimate: {len(parsed['long_synopsis'].split())} words")
        else:
            print(f"Keys in parsed JSON: {list(parsed.keys())}")
    except json.JSONDecodeError as e:
        print(f"\nFailed to parse as JSON: {e}")
        print("Will be treated as plain text")

# Now try with validation
print("\n" + "="*60)
print("TRYING WITH VALIDATION...")
print("="*60)

try:
    content = step6.generator.generate_with_validation(
        prompt, 
        step6.validator, 
        model_config,
        max_attempts=1  # Just one attempt for debugging
    )
    
    print(f"Content type after validation: {type(content)}")
    print(f"Content keys: {list(content.keys()) if isinstance(content, dict) else 'N/A'}")
    
    if "long_synopsis" in content:
        print(f"long_synopsis exists: {len(content['long_synopsis'])} chars")
    elif "content" in content:
        print(f"content exists: {len(content['content'])} chars")
    
    # Run validation
    artifact = {"long_synopsis": content.get("long_synopsis", content.get("content", ""))}
    is_valid, errors = step6.validator.validate(artifact)
    
    print(f"\nValidation result: {is_valid}")
    if not is_valid:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
            
except Exception as e:
    print(f"Error during generation: {e}")
    import traceback
    traceback.print_exc()