#!/usr/bin/env python3
"""Debug Step 4 validation issues"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.steps.step_4_one_page_synopsis import Step4OnePageSynopsis

step2_artifact = {
    'paragraph': 'A burned-out teacher discovers a student is being trafficked. When reporting it gets the teacher fired and threatened, they must work alone. The teacher uncovers a trafficking ring run by school board members. With police paid off and nowhere to turn, only vigilante justice remains. The teacher saves the children but dies stopping the ring.',
    'sentences': {
        'setup': 'A burned-out teacher discovers a student is being trafficked.',
        'disaster_1': 'When reporting it gets the teacher fired and threatened, forcing them to work alone.',
        'disaster_2': 'The teacher uncovers a trafficking ring run by school board members.',
        'disaster_3': 'With police paid off and nowhere to turn, only vigilante justice remains.',
        'resolution': 'The teacher saves the children but dies stopping the ring.'
    },
    'moral_premise': 'Apathy enables evil, but personal courage can save the innocent.'
}

print("Testing Step 4 Generation and Validation")
print("-" * 50)

step4 = Step4OnePageSynopsis()

# Generate content
prompt_data = step4.prompt_generator.generate_prompt(step2_artifact)
print("Prompt includes forcing function instruction:", "forcing function" in prompt_data['system'].lower())

# Generate with bulletproof
raw_content = step4.bulletproof_generator.generate_guaranteed(prompt_data, {'temperature': 0.3})

# Parse content
parsed = step4._parse_synopsis_content_bulletproof(raw_content)

if 'synopsis_paragraphs' in parsed:
    print("\nGenerated paragraphs:")
    for i in range(1, 6):
        key = f'paragraph_{i}'
        if key in parsed['synopsis_paragraphs']:
            para = parsed['synopsis_paragraphs'][key]
            print(f"\n{key} ({len(para)} chars):")
            
            # Check for forcing keywords in P2
            if i == 2:
                p2_lower = para.lower()
                forcing_keywords = ["forces", "no way back", "cannot retreat", "irreversible", 
                                  "must", "trapped", "committed", "no choice", "no escape", 
                                  "point of no return", "can't turn back", "locked in"]
                found = [kw for kw in forcing_keywords if kw in p2_lower]
                print(f"  Forcing keywords found: {found if found else 'NONE'}")
                if not found:
                    print(f"  First 200 chars: {para[:200]}...")
            
            # Check for pivot keywords in P3
            if i == 3:
                p3_lower = para.lower()
                pivot_keywords = ["pivot", "new tactic", "changes tactic", "moral premise",
                                 "realizes", "understands", "learns", "discovers", "shift",
                                 "transformation", "new approach", "different way", "changes course"]
                found = [kw for kw in pivot_keywords if kw in p3_lower]
                print(f"  Pivot keywords found: {found if found else 'NONE'}")
            
            # Check for bottleneck keywords in P4
            if i == 4:
                p4_lower = para.lower()
                bottleneck_keywords = ["bottleneck", "only path", "no options", "collapse",
                                      "final", "last chance", "one way", "single choice",
                                      "narrowing", "closing in", "cornered", "ultimatum"]
                found = [kw for kw in bottleneck_keywords if kw in p4_lower]
                print(f"  Bottleneck keywords found: {found if found else 'NONE'}")

# Create artifact and validate
artifact = {"synopsis_paragraphs": parsed.get("synopsis_paragraphs", {})}
is_valid, errors = step4.validator.validate(artifact)

print("\n" + "-" * 50)
print(f"Validation: {'PASSED' if is_valid else 'FAILED'}")
if not is_valid:
    print("Errors:")
    for error in errors:
        print(f"  - {error}")