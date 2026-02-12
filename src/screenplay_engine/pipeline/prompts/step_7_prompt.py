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

FOR EVERY FAILED CHECK YOU MUST:
1. List the EXACT scene numbers that have the problem in failing_scene_numbers
2. QUOTE the exact problematic dialogue or action lines from those scenes in problem_details
3. For EACH failing scene, write a CONCRETE rewrite instruction in fix_per_scene — not "make it
   better" but "replace Ally's line 'Can't fix guilt alone. Let me in.' with a nonverbal action:
   Ally texts a location pin with just an address. Then: 'I'm not talking. I'm there if you
   show up.' This shows the theme (you can't do it alone) through ACTION not STATEMENT."
4. Each fix_per_scene entry MUST:
   a) QUOTE the current problematic text from the scene
   b) Provide the SPECIFIC replacement text (exact new dialogue or action lines)
   c) Explain in one sentence what the change fixes

OUTPUT FORMAT (valid JSON):
{{
    "diagnostics": [
        {{
            "check_number": 1,
            "check_name": "The Hero Leads",
            "passed": true,
            "problem_details": "",
            "failing_scene_numbers": [],
            "fix_per_scene": {{}}
        }},
        {{
            "check_number": 2,
            "check_name": "Talking the Plot",
            "passed": false,
            "problem_details": "Scene 7: Ally's line 'Can't fix guilt alone. Let me in.' is on-the-nose theme delivery — character is stating the movie's theme directly. Scene 20: Contractor's 'They call it a drill. Last week it cooked a guy in Van Nuys. I signed the form.' is writer-serving exposition — the audience needs this info but the character wouldn't explain it this way. Scene 30: Hero's phone confession compresses complex backstory into a single info-dump monologue.",
            "failing_scene_numbers": [7, 20, 30],
            "fix_per_scene": {{
                "7": "CURRENT: Ally (V.O.): 'Can't fix guilt alone. Let me in.' REPLACE WITH: Ally texts a location pin — just an address, no words. Then V.O.: 'I'm not talking. I'm there if you show up.' Hero stares at the pin, deletes it. FIXES: Theme is shown through Ally's ACTION (showing up) not stated in dialogue.",
                "20": "CURRENT: GRID CONTRACTOR: 'They call it a drill. Last week it cooked a guy in Van Nuys. I signed the form.' REPLACE WITH: Show the drill via environment — posters on the wall read 'COMPLIANCE TEST WEEK', a checklist the contractor initialed hangs by the door, a body bag cart sits in the hall. Contractor only says: 'I just follow the sheet.' FIXES: Exposition moved from dialogue into visual production design.",
                "30": "CURRENT: Hero delivers full confession monologue into phone. REPLACE WITH: Break into two beats. First, a short urgent ask: 'I need eyes, not forgiveness.' Later, a quieter line revealing the Skip death with one image: 'My wire lit up. He didn't.' FIXES: Backstory delivered in compressed images, not an info-dump."
            }}
        }},
        {{
            "check_number": 3,
            "check_name": "Make the Bad Guy Badder",
            "passed": true,
            "problem_details": "",
            "failing_scene_numbers": [],
            "fix_per_scene": {{}}
        }},
        {{
            "check_number": 4,
            "check_name": "Turn Turn Turn",
            "passed": false,
            "problem_details": "Scenes 6, 8, 11, 17, 18, 21, 23, 26 are variations of 'surveillance finds hero → hero improvises analog trick → escapes.' Stakes rise (deepfake shoot-on-sight, contractor death, injury, cascade) but hero's flaw is reiterated rather than evolved until Scene 29.",
            "failing_scene_numbers": [17, 21],
            "fix_per_scene": {{
                "17": "CURRENT: Hero escapes rooftop via fire escape after drone spots them — same hide-and-flee pattern. REPLACE: Hero CAN escape clean but CHOOSES to save a stranger being misidentified by the drone, costing her time. This advances her Need (protect without credit) and varies the beat from 'flee' to 'moral choice.' Add: BYSTANDER frozen in drone beam. Hero shoves Bystander behind HVAC unit, takes the scan herself. Rival: 'That wasn't the plan.' Hero: 'New plan.' FIXES: Chase beat becomes a moral turn — hero evolves, not just survives.",
                "21": "CURRENT: ANTAGONIST_SYSTEM deepfakes Hero's voice on loudspeaker, cops converge, Hero and Rival flee with loop device. REPLACE: Add a new bad-guy power reveal — ANTAGONIST_SYSTEM starts manipulating TRAFFIC LIGHTS to create physical collisions in front of them. A car T-bones a truck blocking their path. This changes the rules (not just more cops) and forces Hero to invent a new strategy. Hero: 'It's not just cameras now. It's moving the city.' FIXES: Escalation in kind, not just degree."
            }}
        }},
        {{
            "check_number": 5,
            "check_name": "Emotional Color Wheel",
            "passed": false,
            "problem_details": "Emotion audit: fear appears in 18/40 scenes, anger in 12/40, near-miss anxiety in 15/40, tenderness in 4/40, surprise in 3/40, triumph in 2/40. MISSING ENTIRELY: lust/sexual tension (0 scenes), joy/uncomplicated happiness (0 scenes except Final Image), human foible/comic relief (0 scenes), longing/romantic-aspirational (0 scenes). The palette is monotone action-thriller.",
            "failing_scene_numbers": [11, 12, 19],
            "fix_per_scene": {{
                "11": "CURRENT: Hero cranks radio, gets static, buys flashlight, smashes vendor's scanner, flees. RECOLOR FOR HUMAN FOIBLE + JOY: When Hero cranks the radio, it blasts a cheesy late-night love song. She and the One-Armed Shopper lock eyes — involuntary laugh. Shopper catches a rolling battery with prosthetic claw, tosses it to Hero with a grin: 'Radio's got taste.' Beat. Then danger snaps back. FIXES: Adds 5 seconds of genuine humor and human connection to an action beat without changing the plot outcome.",
                "12": "CURRENT: Rival tosses token chain to Hero at payphones — tactical exchange. ADD LONGING: When Hero catches the chain, her fingers linger on the Metro token. One-line memory: Hero (whisper): 'We used to skip school on these.' She means Ally. Pockets it. FIXES: Adds yearning/nostalgia without exposition — the token becomes an emotional anchor, not just a prop.",
                "19": "CURRENT: Rival takes Hero's hand over the clamp — tactical teamwork moment. ADD CHEMISTRY: When Rival's hand seals over hers, let it land with charged intimacy. Hero pulls away too fast — fear of connection visible. Rival doesn't comment. They work. FIXES: Adds a flicker of lust/attraction that reveals Hero's fear of attachment."
            }}
        }},
        {{
            "check_number": 6,
            "check_name": "Hi How Are You I'm Fine",
            "passed": false,
            "problem_details": "Cover-the-names test: Clerk, Store Owner, Laundry Patron, Security Guard, Homeowner, and Janitor all speak with the same clipped, hard-boiled, imperative rhythm. 'Door's swollen. Hit bottom hinge.' / 'You owe me.' / 'Name it.' — these lines could be swapped between characters without friction. Each side character sounds like the writer's voice, not their own.",
            "failing_scene_numbers": [5, 7, 16],
            "fix_per_scene": {{
                "5": "CURRENT: STORE OWNER: 'You drip on the serpentine belts, you buy the whole rack.' / 'Wipe prints. I never met you. Door's swollen. Hit bottom hinge.' REPLACE WITH: Make Store Owner superstitious and metaphor-heavy: 'Tools walk out when the sun drops. That's when trouble shops.' / 'Grease don't lie — wipe everything you touched. And that door? Give it the knee, low. It bites high.' FIXES: Distinctive speech pattern (superstitious metaphors) vs. generic tough-guy.",
                "7": "CURRENT: LAUNDRY PATRON: 'I'm union. I don't cross lines—and I don't talk to cops.' / 'They're sweeping blocks. You owe me.' / 'Get my brother out of County. Go. Now.' REPLACE WITH: Make Patron formal/procedural with union-speak: 'Article 7: I don't volunteer information. Article 12: I don't impede, I don't assist.' (beat) 'But Article 3 says my brother's been in County six months on a paperwork hold. You fix that — we never met.' FIXES: Distinctive cadence (citing articles/rules) that could ONLY be this character.",
                "16": "CURRENT: HOMEOWNER: 'Thieves freeze! This feeds live!' / 'We don't feed the machine in this house. Back gate. Move.' REPLACE WITH: Make Homeowner anxious-parent with fragmented sentences: 'No no no — kids are — who are you? Don't — the camera's — wait, is that—' (sees kid in doorway, rips bodycam off) '...go. Back gate. Don't run. Walking. Walking.' FIXES: Anxious-parent speech pattern (interrupted, protective, half-sentences) vs. generic tough authority."
            }}
        }},
        {{
            "check_number": 7,
            "check_name": "Take a Step Back",
            "passed": true,
            "problem_details": "",
            "failing_scene_numbers": [],
            "fix_per_scene": {{}}
        }},
        {{
            "check_number": 8,
            "check_name": "Limp and Eye Patch",
            "passed": false,
            "problem_details": "Hero's scarred forearm is a strong running visual. Rival's token clicking is memorable. But Ally (voice-only for 39/40 scenes) lacks a consistent aural signature — no repeating sound or verbal tic on her calls. ANTAGONIST_SYSTEM shifts between distorted/smooth/taunting without a repeating motif. One-shot helpers (Clerk, Store Owner, etc.) have zero visual identifiers.",
            "failing_scene_numbers": [7, 4, 15],
            "fix_per_scene": {{
                "7": "CURRENT: Ally (V.O.) has no aural signature. ADD: Every time Ally speaks, open with the sound of ice clinking in a glass — she stirs when she's nervous. Scene 7: 'Ally (V.O.) (warm, mid-sip, ice CLINKS)' — then repeat this cue in every Ally scene (9, 30, 34, 36, 38, 39). FIXES: Repeatable aural identifier that lets the audience 'see' Ally without seeing her.",
                "4": "CURRENT: ANTAGONIST_SYSTEM speaks as 'EARBUD VOICE (ANTAGONIST_SYSTEM) (distorted)' with 'Optimal.' ADD SIGNATURE: ANTAGONIST_SYSTEM always uses the word 'Optimal' and always refers to humans as 'units.' Lights dim 5%% when it speaks (add action: 'Overhead flickers'). Scene 4 already has 'Optimal.' — add the light-dim and 'unit' language. FIXES: Repeatable villain footprint — audience recognizes ANTAGONIST_SYSTEM's presence even offscreen.",
                "15": "CURRENT: ANTAGONIST_SYSTEM (V.O.): 'Access denied. Anomalies detected. Step back.' REPLACE: 'Access denied. Two units detected. Step back, Hero. Optimal.' Add: 'Intercom light DIMS five percent.' FIXES: Consistent signature language ('units', 'Optimal') and physical tell (light dim)."
            }}
        }},
        {{
            "check_number": 9,
            "check_name": "Is It Primal",
            "passed": true,
            "problem_details": "",
            "failing_scene_numbers": [],
            "fix_per_scene": {{}}
        }}
    ],
    "checks_passed_count": 4,
    "total_checks": 9
}}

RULES:
- You MUST run ALL 9 checks -- do not skip any.
- For PASSED checks: problem_details is empty string, failing_scene_numbers is empty array, fix_per_scene is empty object.
- For FAILED checks: ALL THREE fields MUST be filled:
  * problem_details: Non-empty string with specific issues, QUOTING actual dialogue/action from the screenplay
  * failing_scene_numbers: Non-empty list of integers identifying which scenes have the problem
  * fix_per_scene: Non-empty object where EACH key is a scene number (as string) from failing_scene_numbers,
    and EACH value is a concrete rewrite instruction that QUOTES the current text AND provides replacement text
- fix_per_scene instructions MUST follow the format: "CURRENT: [quoted text]. REPLACE WITH: [new text]. FIXES: [what this changes]."
- Do NOT write vague fix instructions like "make the dialogue more distinct" — write SPECIFIC replacement
  lines that could be copy-pasted into the screenplay.
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


