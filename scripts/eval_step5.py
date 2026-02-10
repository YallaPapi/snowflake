"""
LLM Evaluation of Step 5 Board against Save the Cat Ch.5 criteria.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()
from src.ai.generator import AIGenerator

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

# Load the board
with open(os.path.join(ARTIFACTS_DIR, "step5_test_live", "sp_step_5_board.json"), "r", encoding="utf-8") as f:
    board = json.load(f)

# Load upstream artifacts for context
with open(os.path.join(ARTIFACTS_DIR, "step4_test_live", "sp_step_4_beat_sheet.json"), "r", encoding="utf-8") as f:
    beats = json.load(f)

# Build board summary for evaluation
board_text = ""
row_labels = {
    "row_1_act_one": "ROW 1 (ACT ONE)",
    "row_2_act_two_a": "ROW 2 (ACT TWO A)",
    "row_3_act_two_b": "ROW 3 (ACT TWO B)",
    "row_4_act_three": "ROW 4 (ACT THREE)",
}
for key, label in row_labels.items():
    board_text += f"\n{label}:\n"
    for card in board.get(key, []):
        num = card.get("card_number", "?")
        heading = card.get("scene_heading", "")
        beat = card.get("beat", "")
        e_start = card.get("emotional_start", "?")
        e_end = card.get("emotional_end", "?")
        color = card.get("storyline_color", "?")
        desc = card.get("description", "")
        conflict = card.get("conflict", "")
        chars = ", ".join(card.get("characters_present", []))
        board_text += f"  [{num}] {heading} | Beat: {beat} | [{e_start}/{e_end}] | Color: {color}\n"
        board_text += f"       {desc}\n"
        board_text += f"       Conflict: {conflict}\n"
        board_text += f"       Characters: {chars}\n\n"

# Build beats summary
beats_text = ""
for b in beats.get("beats", []):
    beats_text += f"  {b.get('number')}. {b.get('name')} (p.{b.get('target_page')}) - {b.get('description', '')[:80]}\n"

eval_prompt = {
    "system": """You are a screenwriting professor and Save the Cat expert evaluating a 40-card scene board.
Score each criterion 1-10 with specific evidence. Be rigorous — a 7 means good but with clear issues,
an 8 means strong with minor notes, a 9 means excellent, and 10 means textbook perfect.""",
    "user": f"""Evaluate this 40-card Board (Save the Cat Ch.5) for the screenplay "WANTED: BLACKOUT".

Genre: Dude with a Problem (DwaP) — innocent hero thrust into life-and-death survival.

BEAT SHEET (15 beats from Step 4):
{beats_text}

BOARD (40 Scene Cards):
{board_text}

Score each criterion 1-10 with 2-3 sentences of evidence:

1. **Card Count & Row Distribution**: Exactly 40 cards, 10 per row? Proper act structure?
2. **Landmark Beat Placement**: Catalyst at ~card 4, Break into Two at ~9-10, B Story at ~11, Midpoint at ~20, All Is Lost at ~28, Dark Night at ~29, Break into Three at ~30?
3. **Opening Image / Final Image Mirror**: Does card 1 establish a thesis and card 40 its antithesis? Do they bookend the transformation?
4. **Emotional Polarity Per Card**: Does EVERY card have emotional change (+/- or -/+)? Are adjacent cards contrasting? Is there variety?
5. **Storyline Color Coding**: Are A/B/C/D/E storylines tracked? Is the A storyline dominant? Does B storyline (Mateo/theme) weave properly? Max 3 consecutive same color?
6. **Fun and Games (Row 2)**: Does Row 2 deliver the "promise of the premise" — the DwaP survival set pieces? Is this where the audience gets what they paid for?
7. **Bad Guys Close In (Row 3)**: Does the antagonist escalate? Does the team fracture? Do internal and external forces converge?
8. **Conflict Format & Quality**: Does every card have specific "X >< Y over Z; winner" conflict? Are conflicts concrete and visual, not abstract?
9. **Genre Fidelity (DwaP)**: Escalating survival set pieces? Resourcefulness under pressure? Net tightening? Hero's individuality as weapon in Finale?
10. **Description Quality**: Are descriptions concrete, visual, screenable? Can you picture each scene? Are they actions, not summaries?
11. **Character Presence**: Is the hero in most/all scenes? Do supporting characters (Mateo, Sloane, NYX) appear at appropriate frequencies?
12. **Three-Act Finale Structure**: Does Act Three have a proper "storming the castle" with team gathering, lieutenants dispatched, and high tower confrontation?

Output format:
CRITERION: score/10
Evidence: [2-3 sentences]

Then: TOTAL: X/120
Then: TOP 3 STRENGTHS and TOP 3 WEAKNESSES with specific card references.
"""
}

gen = AIGenerator()
print("Sending board to LLM for evaluation...")
result = gen.generate(eval_prompt, {"temperature": 0.0, "max_tokens": 8000})
print(result)
