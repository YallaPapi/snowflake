"""
Checkpoint Configuration: Which diagnostic checks apply at each pipeline step.

Maps each Save the Cat pipeline step to the subset of Ch.7 diagnostic checks
that can be meaningfully evaluated given the artifacts available at that point.

IMPORTANT: Each check has step-specific evaluation criteria because the same
check means different things when evaluating a logline vs. a full screenplay.
"""

from typing import Dict, List


# Which checks apply after each step (step_number -> list of check_numbers)
CHECKPOINT_CONFIG: Dict[int, List[int]] = {
    # Step 1 (Logline): Only logline exists. Check if foundation implies
    # a proactive hero and connects to a primal drive.
    1: [1, 9],

    # Step 2 (Genre): Genre added. Check if genre supports emotional range.
    2: [5],

    # Step 3 (Hero): Hero/antagonist/B-story added.
    3: [1, 3, 7, 8, 9],

    # Step 4 (Beat Sheet): 15 beats added.
    4: [1, 3, 4, 5, 7, 9],

    # Step 5 (Board): 40 scene cards.
    5: [1, 3, 4, 5, 6, 7, 8, 9],

    # Step 6 (Screenplay): Full screenplay. All 9 checks apply.
    6: [1, 2, 3, 4, 5, 6, 7, 8, 9],
}


# Step-specific evaluation guidance for each check.
# Tells the AI what CAN be evaluated at this step vs what CANNOT.
# Key: (step_number, check_number) -> guidance string
STEP_SPECIFIC_GUIDANCE: Dict[tuple, str] = {
    # -- Check 1: The Hero Leads --
    (1, 1): (
        "At the LOGLINE stage, you can only check: Does the logline imply the hero will be "
        "proactive (drives the plot) rather than reactive (things happen to them)? Does it "
        "suggest the hero has a clear goal? You CANNOT check for spoken dialogue, question "
        "marks, or goal restatements — the screenplay doesn't exist yet."
    ),
    (3, 1): (
        "At the HERO DESIGN stage, check: Is the hero designed with a clear goal and proactive "
        "nature? Is the hero's motivation described as active pursuit, not passive discovery? "
        "Does the design imply the hero will drive the plot? You CANNOT evaluate actual "
        "dialogue or scene behavior yet."
    ),
    (4, 1): (
        "At the BEAT SHEET stage, check: Does the hero drive beat transitions through their "
        "choices? Is the hero's goal clear in the beat descriptions? Does the hero seek "
        "information rather than passively receiving it? You can evaluate beat descriptions "
        "but NOT actual dialogue."
    ),
    (5, 1): (
        "At the BOARD stage, check: Do scene cards show the hero initiating actions? Does "
        "the hero drive scene-to-scene progression? Is the hero's goal referenced in card "
        "descriptions? You can evaluate scene card descriptions and quoted lines."
    ),
    (6, 1): (
        "At the SCREENPLAY stage, evaluate fully: Is the hero's goal spoken aloud in Set-Up "
        "and restated? Does the hero SEEK information? Does the hero TELL others what to do? "
        "Count question marks in hero dialogue — there should be few."
    ),

    # -- Check 3: Make the Bad Guy Badder --
    (3, 3): (
        "At the HERO DESIGN stage, check: Is the antagonist designed to be more powerful than "
        "the hero? Is there a mirror relationship? Does the antagonist's design suggest they "
        "will escalate? You CANNOT evaluate escalation in action yet."
    ),
    (4, 3): (
        "At the BEAT SHEET stage, check: Do the beats show the antagonist escalating across "
        "the story? Is the antagonist's power increasing beat by beat? Is there a mirror "
        "principle visible in the beat structure?"
    ),
    (5, 3): (
        "At the BOARD stage, check: Do scene cards show progressive antagonist escalation? "
        "Is each antagonist move more threatening than the last? Is the mirror with the hero "
        "visible in scene-level conflicts?"
    ),

    # -- Check 5: Emotional Color Wheel --
    (2, 5): (
        "At the GENRE stage, check: Does the chosen genre naturally support a wide emotional "
        "range? Does the genre's working parts suggest multiple emotions will be triggered? "
        "You CANNOT evaluate specific scenes yet — just whether the genre choice supports "
        "emotional diversity."
    ),
    (4, 5): (
        "At the BEAT SHEET stage, check: Do the 15 beats collectively cover a wide emotional "
        "range? Look for: fear, joy, hope, despair, anger, tenderness, surprise. Flag if "
        "the beats are emotionally monotone (all tension, no contrast)."
    ),
    (5, 5): (
        "At the BOARD stage, check: Do the 40 scene cards collectively cover the full palette? "
        "Look for designed moments of: lust, fear, joy, hope, despair, anger, tenderness, "
        "surprise, longing, regret, frustration, near-miss anxiety, triumph, human foible."
    ),

    # -- Check 7: Take a Step Back --
    (3, 7): (
        "At the HERO DESIGN stage, check: Is the hero designed with enough starting flaws "
        "and distance from their end-state? Is the bow-and-arrow distance maximized? Does "
        "the hero start far enough back that growth will be visible?"
    ),
    (4, 7): (
        "At the BEAT SHEET stage, check: Do early beats show the hero in a flawed state? "
        "Is there visible growth distance between Opening Image and Final Image? Do beat "
        "transitions show character transformation?"
    ),
    (5, 7): (
        "At the BOARD stage, check: Do early cards show the hero's starting flaws in action? "
        "Is the arc visible across the board rows? Is the transformation gradual and earned?"
    ),

    # -- Check 8: Limp and Eye Patch --
    (3, 8): (
        "At the HERO DESIGN stage, check: Are distinctive physical/behavioral traits assigned "
        "to the hero, antagonist, and B-story character? Does each have a memorable identifier?"
    ),
    (5, 8): (
        "At the BOARD stage, check: Are character identifiers referenced consistently across "
        "scene cards? Can you tell characters apart by their described traits? Do identifiers "
        "appear each time a character enters a scene?"
    ),

    # -- Check 6: Hi How Are You --
    (5, 6): (
        "At the BOARD stage, check: Do scene card descriptions suggest distinct character "
        "voices? If dialogue is quoted on cards, do characters sound different? You CANNOT "
        "fully evaluate this without actual screenplay dialogue."
    ),
}


# Canonical check names (must match step_7_validator.py REQUIRED_CHECK_NAMES)
CHECK_NAMES: Dict[int, str] = {
    1: "The Hero Leads",
    2: "Talking the Plot",
    3: "Make the Bad Guy Badder",
    4: "Turn Turn Turn",
    5: "Emotional Color Wheel",
    6: "Hi How Are You I'm Fine",
    7: "Take a Step Back",
    8: "Limp and Eye Patch",
    9: "Is It Primal",
}


# Full check definitions with Snyder quotes and criteria.
# Extracted from step_7_prompt.py so checkpoint prompts use identical standards.
CHECK_DEFINITIONS: Dict[int, Dict[str, str]] = {
    1: {
        "name": "The Hero Leads",
        "description": (
            'Snyder: "The hero must be proactive. It\'s the Law. If he\'s not, he\'s '
            'not a hero." A common rough-draft mistake is the inactive hero -- "dragged '
            'through the story, showing up when he\'s supposed to but for no reason."'
        ),
        "sub_checks": (
            "a) Is the hero's goal clearly stated in the set-up, spoken aloud, and restated throughout?\n"
            "b) Does the hero SEEK information or just receive it passively?\n"
            "c) Is the hero active or passive? Everything must spring from burning desire.\n"
            'd) Does the hero TELL others what to do, or do others tell HIM? "A hero never asks '
            'questions" -- count question marks in hero dialogue; there should be few.'
        ),
        "fail_criteria": (
            "Hero is reactive, receives exposition, asks too many questions, has no clear goal."
        ),
        "fix_template": (
            "Clarify the hero's goal stated early and restated throughout. Make the hero pursue "
            "information actively. Reduce question marks in hero dialogue."
        ),
    },
    2: {
        "name": "Talking the Plot",
        "description": (
            'Snyder: "Your characters don\'t serve you, they serve themselves." Bad dialogue '
            'that explains plot is a "dead giveaway that the writer is green." '
            '"Show, Don\'t Tell": "Movies are stories told in pictures." '
            '"Character is revealed by action taken not by words spoken."'
        ),
        "sub_checks": (
            "* Show a husband eyeing a pretty young thing instead of three pages of marriage counseling\n"
            "* Show team pictures on the wall, give a limp from the accident\n"
            "* Have characters talk about anything BUT the exposition target\n"
            '* "Be more concerned with what\'s happening now than what happened before the story started"'
        ),
        "fail_criteria": (
            "Characters explain things the listener already knows; backstory delivered through "
            "unnatural dialogue; emotions are TOLD not SHOWN."
        ),
        "fix_template": (
            "Move exposition out of dialogue into visual action, behavior, or environmental "
            "storytelling. Reveal character through action, not words."
        ),
    },
    3: {
        "name": "Make the Bad Guy Badder",
        "description": (
            'Snyder: "Making the bad guy badder automatically makes the hero bigger." '
            'Hero and bad guy are "two halves of the same person struggling for supremacy" '
            "-- the mirror principle. Hero and bad guy must be of equal skill, with the bad "
            'guy having a slight edge because he is "willing to go to any lengths to win."'
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Antagonist is weaker than hero, not a mirror, not threatening enough."
        ),
        "fix_template": (
            "Ratchet up antagonist's power and invincibility. Ensure hero and antagonist are "
            "reflections of each other. Give the edge to the bad guy."
        ),
    },
    4: {
        "name": "Turn Turn Turn",
        "description": (
            'Snyder: "It\'s not enough for the plot to go forward, it must go forward faster, '
            'and with more complexity, to the climax." '
            '"More must be revealed along every step of the plot about your characters and '
            'what all this action means." Show "flaws, reveal treacheries, doubts, and fears '
            'of the heroes -- and threats to them."'
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Pacing is flat after Midpoint, no escalation, repetitive obstacles, no new "
            "character revelations at each turning point."
        ),
        "fix_template": (
            "Add complications at each act break. Reveal new facets of characters (flaws, fears, "
            "hidden powers) at each turning point. Make the plot intensify after Midpoint."
        ),
    },
    5: {
        "name": "Emotional Color Wheel",
        "description": (
            'Snyder: "Whether it\'s a comedy or a drama, wringing out the emotions of the '
            'audience is the name of the game." A good movie is "like a roller coaster ride" '
            "-- lust, fear, joy, hope, despair, anger, tenderness, surprise, longing, regret, "
            "frustration, near-miss anxiety, triumph, human foible."
        ),
        "sub_checks": (
            "Check for ALL of these: lust, fear, joy, hope, despair, anger, tenderness, surprise, "
            "longing, regret, frustration, near-miss anxiety, triumph, human foible."
        ),
        "fail_criteria": (
            "Story is emotionally monotone or missing key emotions from the palette."
        ),
        "fix_template": (
            "Tag scenes with missing emotions. Use the recoloring technique to change emotional "
            "tone while keeping the same action and conflict structure."
        ),
    },
    6: {
        "name": "Hi How Are You I'm Fine",
        "description": (
            'Snyder: "In a good script, every character must speak differently. Every character '
            'must have a unique way of saying even the most mundane chat." '
            'The Bad Dialogue Test: "Cover up the names of the people speaking. Read the repartee '
            'back and forth. Can you tell who is speaking without seeing the name?"'
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Characters sound the same, interchangeable dialogue, all have the writer's voice."
        ),
        "fix_template": (
            "Give each character a verbal tic, unique vocabulary, sentence length, and speech "
            "rhythm. Differentiate through how they say things, not just what."
        ),
    },
    7: {
        "name": "Take a Step Back",
        "description": (
            'Snyder: "We couldn\'t see that what we needed to do was take our hero back as far '
            'as possible, so that the story would be about his growth." Bow-and-arrow metaphor: '
            '"By drawing the bow back to its very quivering end point, the flight of the arrow '
            'is its strongest, longest, best flight." '
            '"Take A Step Back applies to ALL your characters."'
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Hero (or any character) already IS the person they're supposed to become at the start. "
            "Arc is shortcut or told, not shown. Supporting characters don't start far enough back."
        ),
        "fix_template": (
            "Take the hero AND all characters back as far as possible emotionally. Show the "
            "complete flight of the arrow from start to finish."
        ),
    },
    8: {
        "name": "Limp and Eye Patch",
        "description": (
            'Snyder: "Make sure every character has \'A Limp and an Eyepatch.\' The reader '
            "has to have a visual clue, often a running visual reminder, that makes remembering "
            'them easier." Every character needs "something memorable that will stick them in '
            "the reader's mind.\""
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Recurring characters lack distinctive traits, are generic, forgettable, or hard "
            "to tell apart."
        ),
        "fix_template": (
            "Assign each recurring character one distinctive physical, behavioral, or verbal trait. "
            "Reference it each time the character appears."
        ),
    },
    9: {
        "name": "Is It Primal",
        "description": (
            'Snyder: "\'Is it primal?\' is a question I ask from the beginning to the end of '
            'a project." "To ask Is it Primal? or Would a Caveman Understand? is to ask if '
            'you are connecting with the audience at a basic level." '
            "The 5 primal drives: survival, hunger, sex, protection of loved ones, fear of death."
        ),
        "sub_checks": "",
        "fail_criteria": (
            "Hero's motivation is too intellectual, abstract, or modern to be primal. "
            "Characters not driven by basic biological/primal needs."
        ),
        "fix_template": (
            "Reframe the hero's goal so it connects to one of the 5 primal drives at its root. "
            "Ground each character's motivation in a primal drive."
        ),
    },
}


# Artifact keys expected at each step
STEP_ARTIFACT_KEYS: Dict[int, List[str]] = {
    1: ["step_1"],
    2: ["step_1", "step_2"],
    3: ["step_1", "step_2", "step_3"],
    4: ["step_1", "step_2", "step_3", "step_4"],
    5: ["step_1", "step_2", "step_3", "step_4", "step_5"],
    6: ["step_1", "step_2", "step_3", "step_4", "step_5", "screenplay"],
}


def get_applicable_checks(step_number: int) -> List[int]:
    """Return the list of check numbers applicable after a given step."""
    return CHECKPOINT_CONFIG.get(step_number, [])


def get_check_definitions(check_numbers: List[int]) -> List[Dict[str, str]]:
    """Return check definitions for the given check numbers."""
    return [
        {"check_number": n, **CHECK_DEFINITIONS[n]}
        for n in check_numbers
        if n in CHECK_DEFINITIONS
    ]


def get_check_name(check_number: int) -> str:
    """Return the canonical check name for a check number."""
    return CHECK_NAMES.get(check_number, f"Unknown Check {check_number}")
