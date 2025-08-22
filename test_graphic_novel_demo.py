"""
Demo of graphic novel generation with visible panels and dialogue
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_demo_manuscript():
    """Create a short demo manuscript for testing"""
    return {
        "metadata": {
            "step": 10,
            "step_name": "first_draft",
            "project_id": "demo_graphic_novel",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "manuscript": {
            "title": "The Last Guardian",
            "author": "Demo Author",
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Discovery",
                    "scenes": [
                        {
                            "scene_index": 0,
                            "pov": "Maya",
                            "location": "Ancient Temple Ruins",
                            "type": "proactive",
                            "summary": "Maya discovers the ancient artifact",
                            "content": """Maya pushed through the heavy vines covering the temple entrance. Her flashlight cut through the darkness, revealing intricate carvings on the walls.
                            
                            "This is it," she whispered to herself, her heart racing with excitement. "The Temple of the Last Guardian."
                            
                            As she stepped inside, a strange blue glow emanated from the center of the chamber. There, floating above a stone pedestal, was the Crystal of Eternia - the artifact she'd been searching for her entire career.
                            
                            "Professor Chen was right," she said, reaching for her radio. "It's real. The legends were all true."
                            
                            Suddenly, the ground began to shake. Dust fell from the ceiling as an ancient mechanism activated.
                            
                            "Oh no," Maya gasped, backing away. "It's a trap!"
                            
                            A deep voice echoed through the chamber: "WHO DARES DISTURB THE GUARDIAN'S SLUMBER?"
                            
                            Maya's eyes widened as a massive stone figure began to move, its eyes glowing with the same blue light as the crystal.""",
                            "word_count": 150
                        }
                    ],
                    "word_count": 150
                }
            ],
            "total_word_count": 150
        }
    }

def create_demo_character_bibles():
    """Create character descriptions for visual consistency"""
    return {
        "metadata": {
            "step": 7,
            "step_name": "character_bibles",
            "project_id": "demo_graphic_novel",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "character_bibles": [
            {
                "name": "Maya",
                "role": "protagonist",
                "physical": {
                    "age": "28",
                    "height": "5'6\"",
                    "build": "Athletic",
                    "hair": "Black, ponytail",
                    "eyes": "Brown",
                    "distinguishing_features": "Explorer outfit, backpack, flashlight"
                },
                "personality": {
                    "traits": ["Brave", "Curious", "Determined"],
                    "strengths": ["Archaeological knowledge", "Athletic", "Quick thinking"],
                    "weaknesses": ["Impulsive", "Overconfident"]
                }
            },
            {
                "name": "The Guardian",
                "role": "antagonist",
                "physical": {
                    "age": "Ancient",
                    "height": "12 feet",
                    "build": "Massive stone",
                    "hair": "None",
                    "eyes": "Glowing blue",
                    "distinguishing_features": "Stone golem, ancient carvings, blue crystal embedded in chest"
                },
                "personality": {
                    "traits": ["Ancient", "Protective", "Powerful"],
                    "strengths": ["Immense strength", "Magic", "Immortal"],
                    "weaknesses": ["Slow", "Bound to temple"]
                }
            }
        ]
    }

def create_demo_comic_script():
    """Create a properly formatted comic script with panels and dialogue"""
    
    # This simulates what Step 11 would generate
    comic_script = {
        "metadata": {
            "step": 11,
            "step_name": "manuscript_to_script",
            "project_id": "demo_graphic_novel",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "script_format": "full_script",
        "total_pages": 2,
        "total_panels": 8,
        "character_designs": {
            "Maya": "Young archaeologist, athletic build, black ponytail, explorer outfit with backpack",
            "The Guardian": "Massive stone golem, 12 feet tall, glowing blue eyes, ancient carvings on body"
        },
        "pages": [
            {
                "page_number": 1,
                "scene_index": 0,
                "panel_count": 4,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "ESTABLISHING SHOT: Ancient temple ruins covered in vines, jungle setting. Maya pushing through vegetation at the entrance.",
                        "dialogue": [
                            {"character": "Caption", "type": "caption", "text": "The Lost Temple of Eternia. After years of searching..."}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "mysterious",
                        "transition_type": "scene_to_scene",
                        "characters": ["Maya"],
                        "word_count": 10
                    },
                    {
                        "panel_number": 2,
                        "description": "MEDIUM SHOT: Maya inside the temple entrance, flashlight beam cutting through darkness, revealing ancient wall carvings.",
                        "dialogue": [
                            {"character": "Maya", "type": "whisper", "text": "This is it..."},
                            {"character": "Maya", "type": "thought", "text": "The Temple of the Last Guardian."}
                        ],
                        "shot_type": "medium_shot",
                        "mood": "tense",
                        "transition_type": "action_to_action",
                        "characters": ["Maya"],
                        "word_count": 9
                    },
                    {
                        "panel_number": 3,
                        "description": "WIDE SHOT: Interior chamber revealed. A brilliant blue crystal floating above a stone pedestal, casting ethereal light throughout the room.",
                        "dialogue": [
                            {"character": "Maya", "type": "balloon", "text": "The Crystal of Eternia!"},
                            {"character": "Maya", "type": "balloon", "text": "Professor Chen was right!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "awe",
                        "transition_type": "subject_to_subject",
                        "characters": ["Maya"],
                        "word_count": 8
                    },
                    {
                        "panel_number": 4,
                        "description": "CLOSE-UP: Maya's hand reaching for her radio, excitement on her face.",
                        "dialogue": [
                            {"character": "Maya", "type": "balloon", "text": "It's real. The legends were all true."}
                        ],
                        "shot_type": "close_up",
                        "mood": "excited",
                        "transition_type": "action_to_action",
                        "characters": ["Maya"],
                        "word_count": 8
                    }
                ]
            },
            {
                "page_number": 2,
                "scene_index": 0,
                "panel_count": 4,
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "MEDIUM SHOT: The ground shaking violently. Maya stumbling, dust falling from ceiling. Ancient mechanisms activating with grinding sounds.",
                        "dialogue": [
                            {"character": "SFX", "type": "sfx", "text": "RUMMMMBLE!"},
                            {"character": "Maya", "type": "balloon", "text": "Oh no..."}
                        ],
                        "shot_type": "medium_shot",
                        "mood": "danger",
                        "transition_type": "action_to_action",
                        "characters": ["Maya"],
                        "word_count": 2
                    },
                    {
                        "panel_number": 2,
                        "description": "WIDE SHOT: Maya backing away in fear as the temple shakes. Rocks falling, ancient mechanisms moving.",
                        "dialogue": [
                            {"character": "Maya", "type": "balloon", "text": "It's a trap!"}
                        ],
                        "shot_type": "wide_shot",
                        "mood": "panic",
                        "transition_type": "action_to_action",
                        "characters": ["Maya"],
                        "word_count": 3
                    },
                    {
                        "panel_number": 3,
                        "description": "DRAMATIC LOW ANGLE: A massive stone guardian beginning to move, eyes starting to glow with blue light. Pieces of stone falling as it awakens.",
                        "dialogue": [
                            {"character": "Guardian", "type": "balloon_bold", "text": "WHO DARES DISTURB THE GUARDIAN'S SLUMBER?"}
                        ],
                        "shot_type": "low_angle",
                        "mood": "menacing",
                        "transition_type": "action_to_action",
                        "characters": ["The Guardian"],
                        "word_count": 7
                    },
                    {
                        "panel_number": 4,
                        "description": "CLOSE-UP: Maya's terrified face, eyes wide with fear, sweat on her brow.",
                        "dialogue": [
                            {"character": "Maya", "type": "thought", "text": "What have I done?"}
                        ],
                        "shot_type": "close_up",
                        "mood": "terror",
                        "transition_type": "moment_to_moment",
                        "characters": ["Maya"],
                        "word_count": 4
                    }
                ]
            }
        ]
    }
    
    return comic_script

def display_comic_panels(comic_script):
    """Display the comic panels in a readable format"""
    
    print("\n" + "="*70)
    print("THE LAST GUARDIAN - COMIC SCRIPT")
    print("="*70)
    
    for page in comic_script["pages"]:
        print(f"\nPAGE {page['page_number']}")
        print("-" * 60)
        
        for panel in page["panels"]:
            print(f"\nPANEL {panel['panel_number']} ({panel['shot_type'].upper().replace('_', ' ')})")
            print(f"   Mood: {panel['mood']}")
            print(f"   Transition: {panel['transition_type'].replace('_', ' ')}")
            print()
            
            # Visual description
            print(f"   VISUAL: {panel['description']}")
            print()
            
            # Dialogue and text
            if panel["dialogue"]:
                print("   DIALOGUE:")
                for dialogue in panel["dialogue"]:
                    char = dialogue["character"]
                    text = dialogue["text"]
                    dtype = dialogue["type"]
                    
                    if dtype == "caption":
                        print(f"      [CAPTION]: {text}")
                    elif dtype == "thought":
                        print(f"      {char} (thinking): *{text}*")
                    elif dtype == "whisper":
                        print(f"      {char} (whisper): \"{text}\"")
                    elif dtype == "balloon_bold":
                        print(f"      {char}: **{text.upper()}**")
                    elif dtype == "sfx":
                        print(f"      [SFX]: {text}")
                    else:
                        print(f"      {char}: \"{text}\"")
            else:
                print("   [Silent panel]")
            
            print()
            print("   " + "-" * 50)

def save_formatted_script(comic_script):
    """Save a human-readable version of the script"""
    
    artifacts_dir = Path(f"artifacts/graphic_novel_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON version
    with open(artifacts_dir / "comic_script.json", "w") as f:
        json.dump(comic_script, f, indent=2)
    
    # Save readable text version
    with open(artifacts_dir / "comic_script_readable.txt", "w", encoding="utf-8") as f:
        f.write("THE LAST GUARDIAN - COMIC SCRIPT\n")
        f.write("=" * 70 + "\n\n")
        
        for page in comic_script["pages"]:
            f.write(f"PAGE {page['page_number']}\n")
            f.write("-" * 60 + "\n\n")
            
            for panel in page["panels"]:
                f.write(f"PANEL {panel['panel_number']} - {panel['shot_type'].upper().replace('_', ' ')}\n")
                f.write(f"Mood: {panel['mood']} | Transition: {panel['transition_type'].replace('_', ' ')}\n\n")
                f.write(f"VISUAL: {panel['description']}\n\n")
                
                if panel["dialogue"]:
                    f.write("DIALOGUE:\n")
                    for dialogue in panel["dialogue"]:
                        if dialogue["type"] == "caption":
                            f.write(f"  [CAPTION]: {dialogue['text']}\n")
                        elif dialogue["type"] == "thought":
                            f.write(f"  {dialogue['character']} (thinking): {dialogue['text']}\n")
                        elif dialogue["type"] == "whisper":
                            f.write(f"  {dialogue['character']} (whisper): {dialogue['text']}\n")
                        elif dialogue["type"] == "balloon_bold":
                            f.write(f"  {dialogue['character']}: {dialogue['text'].upper()}\n")
                        elif dialogue["type"] == "sfx":
                            f.write(f"  [SFX]: {dialogue['text']}\n")
                        else:
                            f.write(f"  {dialogue['character']}: {dialogue['text']}\n")
                else:
                    f.write("[Silent panel]\n")
                
                f.write("\n" + "-" * 40 + "\n\n")
    
    print(f"\n[OK] Script saved to: {artifacts_dir}")
    return artifacts_dir

def main():
    """Run the demo"""
    
    # Create the comic script
    comic_script = create_demo_comic_script()
    
    # Display the panels
    display_comic_panels(comic_script)
    
    # Save artifacts
    artifacts_dir = save_formatted_script(comic_script)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total Pages: {comic_script['total_pages']}")
    print(f"Total Panels: {comic_script['total_panels']}")
    print(f"Script Format: {comic_script['script_format']}")
    print("\nCharacter Designs:")
    for char, desc in comic_script["character_designs"].items():
        print(f"  - {char}: {desc}")
    
    print("\nDemo complete! The comic script has been generated with proper panel")
    print("descriptions and dialogue formatting ready for an artist to illustrate.")

if __name__ == "__main__":
    main()