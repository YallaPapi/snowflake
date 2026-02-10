"""
LLM Evaluation of Step 6 Screenplay against Save the Cat Ch.5/Ch.7 criteria.
Evaluates the written screenplay — not the board (that's eval_step5.py).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()
from src.ai.generator import AIGenerator

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

# Load the screenplay
with open(os.path.join(ARTIFACTS_DIR, "step6_test_live", "sp_step_8_screenplay.json"), "r", encoding="utf-8") as f:
    screenplay = json.load(f)

# Build screenplay text for evaluation
scenes = screenplay.get("scenes", [])
total_pages = screenplay.get("total_pages", 0)

screenplay_text = ""
for scene in scenes:
    num = scene.get("scene_number", "?")
    slug = scene.get("slugline", "?")
    beat = scene.get("beat", "?")
    e_start = scene.get("emotional_start", "?")
    e_end = scene.get("emotional_end", "?")
    conflict = scene.get("conflict", "?")
    chars = ", ".join(scene.get("characters_present", []))

    screenplay_text += f"\n--- SCENE {num} [{beat}] ({e_start}->{e_end}) ---\n"
    screenplay_text += f"Characters: {chars}\n"
    screenplay_text += f"Conflict: {conflict}\n"

    for elem in scene.get("elements", []):
        etype = elem.get("element_type", "")
        content = elem.get("content", "")
        if etype == "slugline":
            screenplay_text += f"\n{content}\n\n"
        elif etype == "action":
            screenplay_text += f"{content}\n"
        elif etype == "character":
            screenplay_text += f"                    {content}\n"
        elif etype == "parenthetical":
            screenplay_text += f"               ({content})\n"
        elif etype == "dialogue":
            screenplay_text += f"          {content}\n\n"
        elif etype == "transition":
            screenplay_text += f"                                        {content}\n\n"

eval_prompt = {
    "system": """You are a screenwriting professor and Save the Cat expert evaluating a complete screenplay.
Score each criterion 1-10 with specific evidence. Be rigorous — a 7 means good but with clear issues,
an 8 means strong with minor notes, a 9 means excellent, and 10 means textbook perfect.
Quote specific dialogue lines and cite scene numbers as evidence.""",
    "user": f"""Evaluate this complete screenplay for "WANTED: BLACKOUT" ({len(scenes)} scenes, {total_pages:.0f} pages).

Genre: Dude with a Problem (DwaP) — innocent hero thrust into life-and-death survival.

SCREENPLAY:
{screenplay_text}

Score each criterion 1-10 with 2-3 sentences of evidence (cite specific scenes):

1. **Hero Leads (Ch.7 Check #1)**: Is the hero PROACTIVE throughout? Does she make statements, give
   commands, and drive action? Or does she ask questions and get dragged through the plot? Count
   question marks from the hero in representative scenes.

2. **Talking the Plot (Ch.7 Check #2)**: Does dialogue SHOW through subtext and conflict, or TELL
   through exposition? Any "as you know" moments? Are characters explaining what the audience can see?

3. **Bad Guy Badder (Ch.7 Check #3)**: Does the antagonist escalate? Does the antagonist have a slight
   edge throughout? Is the antagonist formidable enough to make the hero's victory meaningful?

4. **Turn Turn Turn (Ch.7 Check #4)**: Is the story accelerating? Does each act push faster and harder
   than the last? Or is it flat — same difficulty level repeated?

5. **Emotional Color Wheel (Ch.7 Check #5)**: What emotions are present? (lust, fear, joy, hope,
   despair, anger, tenderness, surprise, longing, regret, frustration, near-miss anxiety, triumph,
   human foible.) Are at least 8 different emotions represented across the screenplay?

6. **Hi How Are You (Ch.7 Check #6)**: Do characters sound distinct? Cover the names — can you tell
   who's speaking? Does each character have their own vocabulary, sentence length, rhythm?

7. **Take a Step Back (Ch.7 Check #7)**: Does the hero start far enough back? Is the growth visible?
   Is the hero clearly NOT the person they'll become at the start?

8. **Limp and Eye Patch (Ch.7 Check #8)**: Do recurring characters have distinctive visual/behavioral
   identifiers? Can you remember each character by a physical trait, habit, or prop?

9. **Is It Primal (Ch.7 Check #9)**: Does the story tap into universal, primitive instinct? Survival,
   fear of death, protection of loved ones? Would a caveman understand the stakes?

10. **Scene Quality**: Are scenes proper mini-movies with beginning, middle, end? Is there emotional
    change (+/- or -/+) in each scene? Do scenes SHOW through visual action, not tell through dialogue?

11. **Page Count & Pacing**: Is the screenplay feature-length (90-120 pages)? Are beats at proper
    page targets? Opening Image ~p1, Catalyst ~p12, Midpoint ~p55, All Is Lost ~p75?

12. **Dialogue Quality**: Are dialogue exchanges sustained (3+ back-and-forth)? Is dialogue serving
    conflict, not exposition? Are there memorable lines?

Output format:
CRITERION: score/10
Evidence: [2-3 sentences with specific scene/line citations]

Then: TOTAL: X/120
Then: TOP 3 STRENGTHS and TOP 3 WEAKNESSES with specific scene references.
"""
}

gen = AIGenerator()
print(f"Sending screenplay ({len(scenes)} scenes, {total_pages:.0f} pages) to LLM for evaluation...")
result = gen.generate(eval_prompt, {"temperature": 0.0, "max_tokens": 8000})
print(result)
