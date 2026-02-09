"""
Step 7 Prompt Template: Diagnostic Checks (Save the Cat Ch.7)

v2.0.0 -- Rewritten against Ch.7 ("What's Wrong With This Picture?") of
Save the Cat! (2005). Every diagnostic now includes Snyder's actual quotes,
book examples, and precise check criteria from the original text. Exactly 9
diagnostics matching the chapter's "Is It Broken?" summary (lines 271-291).
"""

import json
import hashlib
from typing import Dict, Any, List


class Step7Prompt:
    """Prompt generator for Screenplay Engine Step 7: Diagnostic Checks"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! script doctor. "
        "Run 9 diagnostic checks from Blake Snyder Chapter 7 to identify "
        "structural problems and provide specific fixes.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Run ALL 9 diagnostic checks from Save the Cat Chapter 7 ("What's Wrong With This Picture?") against the FINISHED SCREENPLAY below. The screenplay has been written — evaluate the ACTUAL scenes, dialogue, and action.

FINISHED SCREENPLAY:
{screenplay_json}

HERO PROFILE (Step 3):
{hero_json}

BEAT SHEET (Step 4 - structural reference):
{beat_sheet_json}

THE BOARD (Step 5 - structural reference):
{board_json}

INSTRUCTIONS:
Snyder opens Ch.7: "You've made it! You've finally written THE END." These diagnostics
are the post-draft "Is It Broken?" test. Run every check below. For each, determine
whether the screenplay PASSES or FAILS. If a check FAILS, describe the specific problem
and provide a concrete fix.

THE 9 DIAGNOSTIC CHECKS:

1. THE HERO LEADS — Snyder: "The hero must be proactive. It's the Law. If he's not, he's
   not a hero." A common rough-draft mistake is the inactive hero -- "dragged through the
   story, showing up when he's supposed to but for no reason." (Johnny Entropy example:
   detective who never seeks clues, has no goals, whose motto is "What's the point?")
   Sub-checks:
   a) Is the hero's goal clearly stated in the set-up, spoken aloud, and restated throughout?
   b) Does the hero SEEK information or just receive it passively?
   c) Is the hero active or passive? Everything must spring from burning desire.
   d) Does the hero TELL others what to do, or do others tell HIM? "A hero never asks
      questions" -- count question marks in hero dialogue; there should be few.
   - FAIL criteria: Hero is reactive, receives exposition, asks too many questions, has no
     clear goal.
   - FIX: Clarify the hero's goal stated early and restated throughout. Make the hero pursue
     information actively. Reduce question marks in hero dialogue.

2. TALKING THE PLOT / SHOW, DON'T TELL — Snyder: "Your characters don't serve you, they serve
   themselves." Bad dialogue that explains plot is a "dead giveaway that the writer is green."
   Examples of bad: "Well, you're my sister, you should know!" and "This sure isn't like the
   time I was the star fullback for the N.Y. Giants until my... accident."
   "Show, Don't Tell" (Snyder calls it an "adjunct"): "Movies are stories told in pictures."
   Snyder: "Character is revealed by action taken not by words spoken."
   Sub-techniques:
     * Show a husband eyeing a pretty young thing instead of three pages of marriage counseling
     * Show team pictures on the wall, give a limp from the accident
     * Have characters talk about anything BUT the exposition target
     * "Be more concerned with what's happening now than what happened before the story started"
   - FAIL criteria: Characters explain things the listener already knows; backstory delivered
     through unnatural dialogue; emotions are TOLD not SHOWN.
   - FIX: Move exposition out of dialogue into visual action, behavior, or environmental
     storytelling. Reveal character through action, not words.

3. MAKE THE BAD GUY BADDER — Snyder: "Making the bad guy badder automatically makes the hero
   bigger. It's one of those Immutable Laws of Screenwriting." Hero and bad guy are "two halves
   of the same person struggling for supremacy" -- the mirror principle. (Batman/Joker:
   Keaton/Nicholson. Die Hard: Willis/Rickman. Pretty Woman: Gere/Alexander.)
   James Bond needs Goldfinger, Blofeld, and Dr. No -- not "an evil accountant who was juggling
   the books down at the local bank." Hero and bad guy must be of equal skill, with the bad guy
   having a slight edge because he is "willing to go to any lengths to win."
   - FAIL criteria: Antagonist is weaker than hero, not a mirror, not threatening enough.
   - FIX: Ratchet up antagonist's power and invincibility. Ensure hero and antagonist are
     reflections of each other. Give the edge to the bad guy.

4. TURN, TURN, TURN — Snyder distinguishes "velocity (a constant speed) and acceleration
   (an increasing speed). And the rule is: It's not enough for the plot to go forward, it must
   go forward faster, and with more complexity, to the climax."
   "More must be revealed along every step of the plot about your characters and what all this
   action means." Show "flaws, reveal treacheries, doubts, and fears of the heroes -- and
   threats to them. Expose hidden powers, untapped resources and dark motivations for the bad
   guys." (The Cat in the Hat: "tons of kinetic action without anything happening at all. It's
   a CHASE with no stakes.")
   - FAIL criteria: Pacing is flat after Midpoint, no escalation, repetitive obstacles, no new
     character revelations at each turning point.
   - FIX: Add complications at each act break. Reveal new facets of characters (flaws, fears,
     hidden powers) at each turning point. Make the plot intensify after Midpoint.

5. EMOTIONAL COLOR WHEEL — Snyder: "Whether it's a comedy or a drama, wringing out the
   emotions of the audience is the name of the game." A good movie is "like a roller coaster
   ride" -- "you've laughed, you've cried, you've gotten horny, you've been scared, you've
   felt regret, anger, frustration, near-miss anxiety, and ultimately, breathtaking triumph."
   (Farrelly Brothers -- Something About Mary, Shallow Hal, Stuck On You -- "not just one-note
   funny" but include scenes of great fear, intense longing, lust, human foible.)
   Check for ALL of these: lust, fear, joy, hope, despair, anger, tenderness, surprise,
   longing, regret, frustration, near-miss anxiety, triumph, human foible.
   Recoloring technique: "Take a scene that's just funny or just dramatic and try to play it
   for one of the missing colors... use the same action, the same +/-, the same conflict and
   result, but play it for lust instead of laughs."
   - FAIL criteria: Story is emotionally monotone or missing key emotions from the palette.
   - FIX: Tag scenes with missing emotions. Use the recoloring technique to change emotional
     tone while keeping the same action and conflict structure.

6. HI, HOW ARE YOU? I'M FINE — Snyder: "In a good script, every character must speak
   differently. Every character must have a unique way of saying even the most mundane chat."
   The Bad Dialogue Test (from Mike Cheda): "Cover up the names of the people speaking. Read
   the repartee back and forth. Can you tell who is speaking without seeing the name?" Snyder
   tried it: "I was stunned. God damn it, he was right. I couldn't tell one of my characters
   from the others... all the characters had MY voice!!"
   (Big Ugly Baby: "one stuttered, one did malapropisms, one was an Okie versed in Sartre,
   and the Alien parents always YELLED with at least one word CAPITALIZED!")
   - FAIL criteria: Characters sound the same, interchangeable dialogue, all have the writer's
     voice.
   - FIX: Give each character a verbal tic, unique vocabulary, sentence length, and speech
     rhythm. Differentiate through how they say things, not just what.

7. TAKE A STEP BACK — Snyder: "We couldn't see that what we needed to do was take our hero
   back as far as possible, so that the story would be about his growth." "Getting there WAS
   the story. And showing the bumps along the way made the pay-off greater." Snyder's bow-and-
   arrow metaphor: "By drawing the bow back to its very quivering end point, the flight of the
   arrow is its strongest, longest, best flight."
   CRITICAL: "Take A Step Back applies to ALL your characters" -- not just the hero. "In order
   to show how everyone grows and changes in the course of your story you must take them all
   back to the starting point."
   (Sheldon & Blake's Golden Fleece: kid kicked out of military school was already nice and
   helpful from the start -- took 7 drafts to fix because they needed to take him back
   emotionally.)
   - FAIL criteria: Hero (or any character) already IS the person they're supposed to become at
     the start. Arc is shortcut or told, not shown. Supporting characters don't start far enough
     back.
   - FIX: Take the hero AND all characters back as far as possible emotionally. Show the
     complete flight of the arrow from start to finish.

8. A LIMP AND AN EYE PATCH — Snyder: "Make sure every character has 'A Limp and an Eyepatch.'
   The reader has to have a visual clue, often a running visual reminder, that makes remembering
   them easier." Every character needs "something memorable that will stick them in the reader's
   mind."
   (Deadly Mean Girls: the lead boy needed a black t-shirt and wispy soul-patch. Manager Andy
   Cohen "didn't know what we'd done but the character of the boy really popped for him now.
   The boy jumped off the page." The boy was the same kid -- they just gave him a Limp and an
   Eye Patch.)
   - FAIL criteria: Recurring characters lack distinctive traits, are generic, forgettable, or
     hard to tell apart.
   - FIX: Assign each recurring character one distinctive physical, behavioral, or verbal trait.
     Reference it each time the character appears.

9. IS IT PRIMAL? — Snyder: "'Is it primal?' is a question I ask from the beginning to the end
   of a project." "To ask Is it Primal? or Would a Caveman Understand? is to ask if you are
   connecting with the audience at a basic level." "At the root of anyone's goal in a movie must
   be something that basic, even if on its surface it seems to be about something else."
   The 5 primal drives: survival, hunger, sex, protection of loved ones, fear of death.
   (Die Hard = desire to save one's family. Home Alone = desire to protect one's home. Sleepless
   in Seattle = desire to find a mate. Gladiator = desire to exact revenge. Titanic = desire
   to survive.)
   "At its core it must be about something that resonates at a caveman level."
   - FAIL criteria: Hero's motivation is too intellectual, abstract, or modern to be primal.
     Characters not driven by basic biological/primal needs.
   - FIX: Reframe the hero's goal so it connects to one of the 5 primal drives at its root.
     Ground each character's motivation in a primal drive.

OUTPUT FORMAT (JSON):
{{
    "diagnostics": [
        {{
            "check_number": 1,
            "check_name": "The Hero Leads",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }},
        {{
            "check_number": 2,
            "check_name": "Talking the Plot",
            "passed": false,
            "problem_details": "<specific problem found>",
            "fix_suggestion": "<specific fix>"
        }},
        {{
            "check_number": 3,
            "check_name": "Make the Bad Guy Badder",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }},
        {{
            "check_number": 4,
            "check_name": "Turn Turn Turn",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }},
        {{
            "check_number": 5,
            "check_name": "Emotional Color Wheel",
            "passed": false,
            "problem_details": "<specific problem found>",
            "fix_suggestion": "<specific fix>"
        }},
        {{
            "check_number": 6,
            "check_name": "Hi How Are You I'm Fine",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }},
        {{
            "check_number": 7,
            "check_name": "Take a Step Back",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }},
        {{
            "check_number": 8,
            "check_name": "Limp and Eye Patch",
            "passed": false,
            "problem_details": "<specific problem found>",
            "fix_suggestion": "<specific fix>"
        }},
        {{
            "check_number": 9,
            "check_name": "Is It Primal",
            "passed": true,
            "problem_details": "",
            "fix_suggestion": ""
        }}
    ],
    "checks_passed_count": 6,
    "total_checks": 9
}}

RULES:
- You MUST run ALL 9 checks -- do not skip any.
- For PASSED checks, problem_details and fix_suggestion may be empty strings.
- For FAILED checks, problem_details and fix_suggestion MUST be non-empty with specific, actionable content.
- checks_passed_count MUST equal the number of diagnostics where passed is true.
- total_checks MUST always be 9.
- Use the exact check_name values shown above."""

    REVISION_PROMPT_TEMPLATE = """Your previous diagnostic check output had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

FINISHED SCREENPLAY:
{screenplay_json}

HERO PROFILE (Step 3):
{hero_json}

BEAT SHEET (Step 4):
{beat_sheet_json}

THE BOARD (Step 5):
{board_json}

Provide a corrected JSON response that fixes ALL listed errors.
Evaluate the FINISHED SCREENPLAY (not just the Board). You MUST run ALL 9 diagnostic checks and use the exact check names.
Respond with valid JSON only. No markdown, no commentary."""

    def generate_prompt(
        self,
        screenplay_artifact: Dict[str, Any],
        step_5_artifact: Dict[str, Any],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 7 diagnostic checks.

        Args:
            screenplay_artifact: The finished screenplay artifact.
            step_5_artifact: The validated Step 5 Board artifact.
            step_4_artifact: The validated Step 4 Beat Sheet artifact.
            step_3_artifact: The validated Step 3 Hero profile artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        # Format inputs as JSON strings for the prompt
        screenplay_json = json.dumps(screenplay_artifact, indent=2, ensure_ascii=False)
        hero_json = json.dumps(step_3_artifact, indent=2, ensure_ascii=False)
        beat_sheet_json = json.dumps(step_4_artifact, indent=2, ensure_ascii=False)
        board_json = json.dumps(step_5_artifact, indent=2, ensure_ascii=False)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            screenplay_json=screenplay_json,
            hero_json=hero_json,
            beat_sheet_json=beat_sheet_json,
            board_json=board_json,
        )

        # Calculate prompt hash for tracking
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_revision_prompt(
        self,
        previous_response: Dict[str, Any],
        validation_errors: List[str],
        fix_suggestions: List[str],
        screenplay_artifact: Dict[str, Any],
        step_5_artifact: Dict[str, Any],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            screenplay_artifact: The finished screenplay artifact.
            step_5_artifact: The Step 5 Board artifact.
            step_4_artifact: The Step 4 Beat Sheet artifact.
            step_3_artifact: The Step 3 Hero profile artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        screenplay_json = json.dumps(screenplay_artifact, indent=2, ensure_ascii=False)
        hero_json = json.dumps(step_3_artifact, indent=2, ensure_ascii=False)
        beat_sheet_json = json.dumps(step_4_artifact, indent=2, ensure_ascii=False)
        board_json = json.dumps(step_5_artifact, indent=2, ensure_ascii=False)

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2, ensure_ascii=False),
            errors=error_text,
            suggestions=suggestion_text,
            screenplay_json=screenplay_json,
            hero_json=hero_json,
            beat_sheet_json=beat_sheet_json,
            board_json=board_json,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }
