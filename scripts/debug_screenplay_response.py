"""Debug: Send a simple screenplay prompt to GPT 5.2 and inspect the raw response."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

# Minimal prompt — just 2 scenes to see the format
response = client.chat.completions.create(
    model="gpt-5.2-2025-12-11",
    max_completion_tokens=4000,
    temperature=0.5,
    messages=[
        {"role": "system", "content": "You are a screenwriter. Respond with valid JSON only. No markdown fences."},
        {"role": "user", "content": """Generate a JSON screenplay with exactly 2 scenes. Use this format:
{
    "title": "TEST",
    "logline": "A test screenplay.",
    "genre": "action",
    "format": "feature",
    "total_pages": 3.0,
    "estimated_duration_seconds": 180,
    "scenes": [
        {
            "scene_number": 1,
            "slugline": "INT. ROOM - DAY",
            "beat": "Opening Image",
            "emotional_start": "+",
            "emotional_end": "-",
            "conflict": "Hero vs villain",
            "characters_present": ["Hero"],
            "estimated_duration_seconds": 90,
            "elements": [
                {"element_type": "action", "content": "Hero enters."},
                {"element_type": "character", "content": "HERO"},
                {"element_type": "dialogue", "content": "Here we go."}
            ]
        }
    ]
}
Generate 2 scenes in this exact format. Valid JSON only."""}
    ]
)

content = response.choices[0].message.content
print(f"=== Response length: {len(content) if content else 0} chars ===")
print(f"=== First 500 chars ===")
print(repr(content[:500]) if content else "NONE/EMPTY")
print(f"\n=== Last 500 chars ===")
print(repr(content[-500:]) if content else "NONE/EMPTY")

# Try parsing
try:
    parsed = json.loads(content)
    print(f"\n=== JSON parsed OK! Keys: {list(parsed.keys())} ===")
    print(f"=== Scenes: {len(parsed.get('scenes', []))} ===")
except json.JSONDecodeError as e:
    print(f"\n=== JSON PARSE FAILED: {e} ===")
    # Try finding JSON in content
    import re
    match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', content, re.DOTALL)
    if match:
        print("=== Found JSON in markdown fences ===")
        try:
            parsed = json.loads(match.group(1))
            print(f"=== Fenced JSON parsed! Keys: {list(parsed.keys())} ===")
        except:
            print("=== Fenced JSON also failed ===")
    else:
        print("=== No markdown fences found ===")
