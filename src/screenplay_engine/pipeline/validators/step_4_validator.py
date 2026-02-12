"""
Step 4 Validator: Beat Sheet (BS2)
Validates the 15-beat Blake Snyder Beat Sheet for structural correctness.

v2.0.0 -- Rewritten against Ch.4 of Save the Cat! (2005).
All 15 beats are now content-validated with keyword checks derived from the
book's actual rules. Sentence counting uses abbreviation-safe splitting.
BEAT_PAGE_TARGETS are now enforced. Thesis/Antithesis/Synthesis act labels
are validated. Opening/Final Image opposition is checked.
"""

import re
from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import BEAT_NAMES, BEAT_PAGE_TARGETS


class Step4Validator:
    """Validator for Screenplay Step 4: Beat Sheet (BS2)"""

    VERSION = "2.0.0"

    # ── Keyword lists for per-beat content checks ─────────────────────

    # Beat 6 (Break into Two): hero's proactive choice
    PROACTIVE_KEYWORDS = [
        "chooses", "decides", "commits", "choose", "decide", "commit",
        "chose", "decided", "committed", "choosing", "deciding", "committing",
        "makes the choice", "makes the decision", "takes the leap",
        "steps forward", "volunteers", "accepts the call",
        "proactive", "willingly", "deliberately",
    ]

    # Beat 11 (All Is Lost): whiff of death
    WHIFF_OF_DEATH_KEYWORDS = [
        "whiff of death", "death", "dies", "dying", "dead",
        "mortality", "funeral", "perish", "fatal",
        "kill", "killed", "lethal", "grave", "end of the line",
        "suicide", "murder", "corpse", "buried", "widow",
    ]

    # Beat 14 (Finale): hero applies lessons, dispatches bad guys, changes world
    FINALE_KEYWORDS = [
        "applies", "learned", "lesson", "mastered", "resolved",
        "confronts", "defeats", "dispatches", "overcomes",
        "new world", "changed", "transforms", "new order",
        "showdown", "battle", "fight", "final stand",
        "proactive", "takes action", "leads", "rallies",
        "confrontation", "triumph", "victory",
    ]

    # Beat 4 (Catalyst): external event language
    CATALYST_KEYWORDS = [
        "arrives", "discovers", "receives", "learns", "news",
        "call", "message", "letter", "finds", "told",
        "happens", "event", "telegram", "fired", "killed",
        "dies", "comes", "knock", "arrested", "diagnosed",
        "kidnapped", "appears", "reveals", "announces",
        "crashes", "explodes", "strikes", "hit",
    ]

    # Beat 5 (Debate): must pose a question
    DEBATE_KEYWORDS = [
        "?",  # any question mark in description
        "can ", "should ", "dare ", "will ", "could ",
        "whether", "hesitate", "doubt", "wonder",
        "question", "uncertain", "unsure",
        "what if", "is it possible", "how can",
    ]

    # Beat 7 (B Story): new character, theme, relationship
    B_STORY_KEYWORDS = [
        "character", "love", "mentor", "relationship", "friend",
        "ally", "meets", "introduces", "new", "theme",
        "nurture", "confidant", "guide", "romantic",
        "bond", "partner", "companion",
    ]

    # Beat 8 (Fun and Games): premise, fun, concept — or action words
    # that describe the "promise of the premise" in concrete story terms
    FUN_AND_GAMES_KEYWORDS = [
        "premise", "fun", "promise", "cool", "concept",
        "enjoy", "trailer", "poster", "set piece",
        "fish out of water", "explore", "discover",
        "amusing", "entertaining", "exciting", "adventure",
        # Action/thriller terms for "what's cool about this movie"
        "chase", "hunt", "evade", "outrun", "outsmart",
        "hack", "heist", "showdown", "escape", "infiltrate",
        # Comedy/romance terms
        "hilarious", "romantic", "charming", "awkward",
        # Horror terms
        "terrifying", "stalk", "survive", "hide",
        # General "this is the movie" terms
        "sequence", "montage", "escalate", "navigate",
        "confront", "battle", "clash", "duel", "race",
        "thrill", "spectacular", "ingenious", "resourceful",
    ]

    # Beat 10 (Bad Guys Close In): external AND internal
    BGCI_EXTERNAL_KEYWORDS = [
        "external", "bad guys", "enemy", "threat", "opponent",
        "force", "attack", "close in", "tighten", "regroup",
        "villain", "antagonist", "pressure", "danger",
        "army", "agents", "pursue", "hunt",
    ]
    BGCI_INTERNAL_KEYWORDS = [
        "internal", "doubt", "dissent", "jealousy", "fracture",
        "team", "trust", "betray", "conflict within",
        "distrust", "argue", "split", "blame",
        "insecurity", "fear", "isolation", "alone",
    ]

    # Beat 12 (Dark Night of the Soul): despair and defeat
    DARK_NIGHT_KEYWORDS = [
        "despair", "lowest", "hopeless", "lost", "alone",
        "broken", "dark", "forsaken", "defeated", "nothing",
        "bottom", "rock bottom", "gives up", "surrender",
        "mourns", "weeps", "cries", "devastated",
        "abandoned", "empty", "shattered",
        # Emotional collapse language
        "confession", "confess", "guilt", "ashamed", "shame",
        "breaks down", "breakdown", "collapses", "collapse",
        "failure", "failed", "fail", "admits",
        "tears", "crying", "wept", "vulnerable", "stripped",
        "worst", "doubt", "paralyzed", "frozen",
        "helpless", "powerless", "overwhelm", "crushed",
        "grief", "regret", "remorse", "anguish",
    ]

    # Beat 13 (Break into Three): A+B story merger
    BREAK_INTO_THREE_KEYWORDS = [
        "merge", "combine", "fusion", "realize", "insight",
        "eureka", "idea", "solution", "b story", "b-story",
        "lesson", "together", "connect", "understand",
        "discover", "synthesize", "synthesis", "fuse",
        "click", "dawn", "clue",
        # Natural integration language
        "both", "applies", "converge", "convergence",
        "internal", "external", "meet", "intertwine",
        "wisdom", "truth", "acceptance", "clarity",
        "combines", "newfound", "remembers", "recalls",
        "chooses", "choice", "resolve", "plan",
        "rally", "rallies", "unites", "unite",
        "inspired", "galvanized", "transform",
    ]

    # Expected act labels per beat number
    EXPECTED_ACT_LABELS = {
        1: "thesis", 2: "thesis", 3: "thesis",
        4: "thesis", 5: "thesis", 6: "thesis",
        7: "antithesis", 8: "antithesis", 9: "antithesis",
        10: "antithesis", 11: "antithesis", 12: "antithesis",
        13: "synthesis", 14: "synthesis", 15: "synthesis",
    }

    # Abbreviation pattern for sentence counting (matches Step 1 validator)
    ABBREV_PATTERN = re.compile(
        r'\b(?:Dr|Mr|Mrs|Ms|Jr|Sr|Prof|Rev|Gen|Sgt|Lt|Col|Capt|Cmdr|Adm|'
        r'St|Ave|Blvd|Dept|Est|Inc|Corp|Ltd|Co|vs|etc|approx|ca|U\.S|L\.A)\.',
        re.IGNORECASE,
    )

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the beat sheet artifact against Ch.4 of Save the Cat!

        Structural checks (fatal — block pipeline):
            1.  Exactly 15 beats present
            2.  All beat names match expected names in order
            3.  Each beat has a non-empty description of 1-2 sentences
            4.  midpoint_polarity is "up" or "down"
            5.  all_is_lost_polarity is opposite of midpoint
            8.  Beat 1 and Beat 15 both exist
            10. Each beat has target_page and target_percentage fields
            11. target_page matches BEAT_PAGE_TARGETS
            12. target_percentage matches BEAT_PAGE_TARGETS
            13. emotional_direction is "up", "down", or "neutral"
            14. Opening/Final Image emotional_direction differ
            23. act_label is one of thesis/antithesis/synthesis
            24. act_label matches expected value for beat number

        Content hints (non-fatal — reported as HINT: prefix, don't block pipeline):
            6.  Beat 6 (Break into Two) implies hero's proactive choice
            7.  Beat 11 (All Is Lost) contains whiff of death
            9.  Beat 14 (Finale) references lessons applied / hero action
            15. Beat 2 (Theme Stated) references thematic statement
            16. Beat 4 (Catalyst) describes an external event
            17. Beat 5 (Debate) poses a question
            18. Beat 7 (B Story) references new character/theme
            19. Beat 8 (Fun and Games) references premise/concept
            20. Beat 10 (BGCI) has BOTH internal AND external elements
            21. Beat 12 (Dark Night) shows despair/defeat
            22. Beat 13 (Break into Three) shows A+B merger

        Returns:
            (is_valid, list_of_errors)
            Content hints are prefixed with "HINT:" and do NOT affect is_valid.
        """
        errors: List[str] = []
        hints: List[str] = []

        # -- Check beats list exists --
        beats = artifact.get("beats")
        if not isinstance(beats, list):
            errors.append("MISSING: 'beats' must be a list of 15 beat objects")
            return False, errors

        # 1. Exactly 15 beats
        if len(beats) != 15:
            errors.append(f"BEAT_COUNT: Expected exactly 15 beats, got {len(beats)}")

        # Build lookup by number for targeted checks
        beats_by_number: Dict[int, Dict[str, Any]] = {}
        beats_by_name: Dict[str, Dict[str, Any]] = {}
        for beat in beats:
            num = beat.get("number")
            name = beat.get("name", "")
            if isinstance(num, int):
                beats_by_number[num] = beat
            beats_by_name[name] = beat

        # 2. All beat names match expected names
        actual_names = [b.get("name", "") for b in beats]
        for expected_name in BEAT_NAMES:
            if expected_name not in actual_names:
                errors.append(f"MISSING_BEAT: '{expected_name}' not found in beat names")

        # 3. Each beat: description, sentence count, target fields, emotional_direction, act_label
        for beat in beats:
            num = beat.get("number", "?")
            name = beat.get("name", "Unknown")
            desc = beat.get("description", "")

            # -- Non-empty description --
            if not desc or not isinstance(desc, str) or len(desc.strip()) == 0:
                errors.append(f"EMPTY_DESCRIPTION: Beat {num} ({name}) has no description")
                continue

            # -- Sentence count (abbreviation-safe) --
            errors.extend(self._check_sentence_count(desc, num, name))

            # -- 10. target_page and target_percentage --
            target_page = beat.get("target_page", "")
            target_pct = beat.get("target_percentage", "")
            if not target_page:
                errors.append(
                    f"MISSING_TARGET_PAGE: Beat {num} ({name}) must have a target_page field"
                )
            if not target_pct:
                errors.append(
                    f"MISSING_TARGET_PCT: Beat {num} ({name}) must have a target_percentage field"
                )

            # -- 11-12. target_page/percentage match BEAT_PAGE_TARGETS --
            if isinstance(num, int) and num in BEAT_PAGE_TARGETS:
                expected_page, expected_pct = BEAT_PAGE_TARGETS[num]
                if target_page and target_page != expected_page:
                    errors.append(
                        f"WRONG_TARGET_PAGE: Beat {num} ({name}) target_page is '{target_page}', "
                        f"expected '{expected_page}'"
                    )
                # Normalize: strip "~" prefix before comparing (GPT sometimes omits it)
                norm_pct = target_pct.replace("~", "").strip()
                norm_expected = expected_pct.replace("~", "").strip()
                if target_pct and norm_pct != norm_expected:
                    errors.append(
                        f"WRONG_TARGET_PCT: Beat {num} ({name}) target_percentage is '{target_pct}', "
                        f"expected '{expected_pct}'"
                    )

            # -- 13. emotional_direction validation --
            direction = beat.get("emotional_direction", "")
            if direction and direction not in ("up", "down", "neutral"):
                errors.append(
                    f"INVALID_DIRECTION: Beat {num} ({name}) emotional_direction "
                    f"must be 'up', 'down', or 'neutral', got '{direction}'"
                )

            # -- 23-24. act_label validation --
            act_label = beat.get("act_label", "")
            if act_label and act_label not in ("thesis", "antithesis", "synthesis"):
                errors.append(
                    f"INVALID_ACT_LABEL: Beat {num} ({name}) act_label must be "
                    f"'thesis', 'antithesis', or 'synthesis', got '{act_label}'"
                )
            if isinstance(num, int) and num in self.EXPECTED_ACT_LABELS:
                expected_act = self.EXPECTED_ACT_LABELS[num]
                if act_label and act_label != expected_act:
                    errors.append(
                        f"WRONG_ACT_LABEL: Beat {num} ({name}) act_label is '{act_label}', "
                        f"expected '{expected_act}'"
                    )

        # 4. Midpoint polarity exists and is "up" or "down"
        midpoint_polarity = artifact.get("midpoint_polarity", "")
        if midpoint_polarity not in ("up", "down"):
            errors.append(
                f"MIDPOINT_POLARITY: midpoint_polarity must be 'up' or 'down', "
                f"got '{midpoint_polarity}'"
            )

        # 5. All Is Lost polarity is opposite of midpoint
        all_is_lost_polarity = artifact.get("all_is_lost_polarity", "")
        if all_is_lost_polarity not in ("up", "down"):
            errors.append(
                f"ALL_IS_LOST_POLARITY: all_is_lost_polarity must be 'up' or 'down', "
                f"got '{all_is_lost_polarity}'"
            )
        elif midpoint_polarity in ("up", "down"):
            expected_opposite = "down" if midpoint_polarity == "up" else "up"
            if all_is_lost_polarity != expected_opposite:
                errors.append(
                    f"POLARITY_MISMATCH: All Is Lost polarity ('{all_is_lost_polarity}') "
                    f"must be opposite of Midpoint ('{midpoint_polarity}'). "
                    f"Expected '{expected_opposite}'"
                )

        # ── Per-beat content hints (non-fatal) ────────────────────────
        # These keyword checks guide revision prompts but do NOT block
        # the pipeline. LLM-generated beat descriptions vary too widely
        # for keyword matching to be reliable as a gate.

        # 15. Beat 2 (Theme Stated): thematic statement by non-protagonist
        beat_2 = beats_by_number.get(2) or beats_by_name.get("Theme Stated")
        if beat_2:
            desc_lower = beat_2.get("description", "").lower()
            desc_raw = beat_2.get("description", "")
            theme_kw = ["theme", "question", "truth", "lesson", "message",
                        "stated", "says", "asks", "tells", "argues",
                        "wisdom", "premise", "moral", "about", "meaning",
                        "texts", "mutters", "whispers", "remarks", "comments",
                        "offers", "notes", "blurts", "confides", "warns",
                        "observes", "reminds", "challenges", "declares",
                        "quips", "replies", "responds", "voices", "mentions",
                        "earn", "forgiveness", "real", "choice", "trust",
                        "show up", "showing up"]
            has_quote = ('"' in desc_raw or '\u201c' in desc_raw or
                         '\u2018' in desc_raw or "'" in desc_raw)
            if not has_quote and not any(kw in desc_lower for kw in theme_kw):
                hints.append(
                    "HINT: BEAT_2_NO_THEME: Theme Stated description should reference a thematic "
                    "statement, question, or message spoken by a non-protagonist character."
                )

        # 16. Beat 4 (Catalyst): external event
        beat_4 = beats_by_number.get(4) or beats_by_name.get("Catalyst")
        if beat_4:
            desc_lower = beat_4.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.CATALYST_KEYWORDS):
                hints.append(
                    "HINT: BEAT_4_NO_EVENT: Catalyst description should describe a single external "
                    "event (e.g., 'arrives', 'discovers', 'receives news', 'learns')."
                )

        # 17. Beat 5 (Debate): poses a question
        beat_5 = beats_by_number.get(5) or beats_by_name.get("Debate")
        if beat_5:
            desc = beat_5.get("description", "")
            desc_lower = desc.lower()
            if not any(kw in desc_lower for kw in self.DEBATE_KEYWORDS):
                hints.append(
                    "HINT: BEAT_5_NO_QUESTION: Debate description should pose a question or reference "
                    "hesitation/doubt. Snyder: 'the Debate section must ask a question of some kind.'"
                )

        # 6. Beat 6 (Break into Two) implies hero's proactive choice
        beat_6 = beats_by_number.get(6) or beats_by_name.get("Break into Two")
        if beat_6:
            desc_lower = beat_6.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.PROACTIVE_KEYWORDS):
                hints.append(
                    "HINT: BEAT_6_NO_CHOICE: Break into Two description should imply hero's "
                    "proactive choice (use words like 'chooses', 'decides', 'commits'). "
                    "Snyder: 'The Hero cannot be lured, tricked or drift into Act Two.'"
                )

        # 18. Beat 7 (B Story): new character and theme
        beat_7 = beats_by_number.get(7) or beats_by_name.get("B Story")
        if beat_7:
            desc_lower = beat_7.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.B_STORY_KEYWORDS):
                hints.append(
                    "HINT: BEAT_7_NO_CHARACTER: B Story description should reference a new character "
                    "or relationship that carries the theme."
                )

        # 19. Beat 8 (Fun and Games): premise/concept
        beat_8 = beats_by_number.get(8) or beats_by_name.get("Fun and Games")
        if beat_8:
            desc_lower = beat_8.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.FUN_AND_GAMES_KEYWORDS):
                hints.append(
                    "HINT: BEAT_8_NO_PREMISE: Fun and Games description should reference the "
                    "premise, concept, or the 'promise of the premise.'"
                )

        # 7. Beat 11 (All Is Lost) contains whiff of death reference
        beat_11 = beats_by_number.get(11) or beats_by_name.get("All Is Lost")
        if beat_11:
            desc_lower = beat_11.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.WHIFF_OF_DEATH_KEYWORDS):
                hints.append(
                    "HINT: BEAT_11_NO_DEATH: All Is Lost description should reference "
                    "'whiff of death' or mortality. Snyder: 'stick in something, anything "
                    "that involves a death.'"
                )

        # 20. Beat 10 (Bad Guys Close In): external AND internal
        beat_10 = beats_by_number.get(10) or beats_by_name.get("Bad Guys Close In")
        if beat_10:
            desc_lower = beat_10.get("description", "").lower()
            has_external = any(kw in desc_lower for kw in self.BGCI_EXTERNAL_KEYWORDS)
            has_internal = any(kw in desc_lower for kw in self.BGCI_INTERNAL_KEYWORDS)
            if not has_external and not has_internal:
                hints.append(
                    "HINT: BEAT_10_NO_THREATS: Bad Guys Close In should reference both external "
                    "threats AND internal problems. Snyder: 'internal dissent, doubt and "
                    "jealousy begin to disintegrate the Hero's team.'"
                )
            elif not has_external:
                hints.append(
                    "HINT: BEAT_10_NO_EXTERNAL: Bad Guys Close In should reference external threats "
                    "(bad guys, enemies, forces closing in)."
                )
            elif not has_internal:
                hints.append(
                    "HINT: BEAT_10_NO_INTERNAL: Bad Guys Close In should reference internal problems "
                    "(doubt, dissent, team fracture, isolation)."
                )

        # 21. Beat 12 (Dark Night of the Soul): despair/defeat
        beat_12 = beats_by_number.get(12) or beats_by_name.get("Dark Night of the Soul")
        if beat_12:
            desc_lower = beat_12.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.DARK_NIGHT_KEYWORDS):
                hints.append(
                    "HINT: BEAT_12_NO_DESPAIR: Dark Night of the Soul should show the hero's "
                    "despair, defeat, or hopelessness. Snyder: 'the darkness right before the dawn.'"
                )

        # 22. Beat 13 (Break into Three): A+B merger
        beat_13 = beats_by_number.get(13) or beats_by_name.get("Break into Three")
        if beat_13:
            desc_lower = beat_13.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.BREAK_INTO_THREE_KEYWORDS):
                hints.append(
                    "HINT: BEAT_13_NO_MERGER: Break into Three description should reference A+B story "
                    "merger, realization, or the key insight. Snyder: 'Both in the external "
                    "story and the internal story which now meet and intertwine.'"
                )

        # ── Structural checks (fatal) ────────────────────────────────────

        # 8. Beat 1 (Opening Image) and Beat 15 (Final Image) both exist
        beat_1 = beats_by_number.get(1) or beats_by_name.get("Opening Image")
        beat_15 = beats_by_number.get(15) or beats_by_name.get("Final Image")
        if not beat_1:
            errors.append("MISSING_OPENING_IMAGE: Beat 1 (Opening Image) is required")
        if not beat_15:
            errors.append("MISSING_FINAL_IMAGE: Beat 15 (Final Image) is required")

        # 14. Opening/Final Image opposition check
        if beat_1 and beat_15:
            dir_1 = beat_1.get("emotional_direction", "")
            dir_15 = beat_15.get("emotional_direction", "")
            if dir_1 and dir_15 and dir_1 == dir_15:
                errors.append(
                    f"IMAGE_SAME_DIRECTION: Opening Image and Final Image both have "
                    f"emotional_direction='{dir_1}'. They should be opposites -- "
                    f"Snyder: 'bookends, a plus and a minus.'"
                )

        # 9. Beat 14 (Finale): lessons applied, hero action, new world
        beat_14 = beats_by_number.get(14) or beats_by_name.get("Finale")
        if beat_14:
            desc_lower = beat_14.get("description", "").lower()
            if not any(kw in desc_lower for kw in self.FINALE_KEYWORDS):
                hints.append(
                    "HINT: BEAT_14_NO_RESOLUTION: Finale should reference lessons applied, hero "
                    "taking action, or a new world order. Snyder: 'the lessons learned are "
                    "applied... the Hero must change the world.'"
                )

        # Combine: errors are fatal, hints are informational
        all_messages = errors + hints
        return len(errors) == 0, all_messages

    def _check_sentence_count(
        self, description: str, beat_num: Any, beat_name: str
    ) -> List[str]:
        """
        Count sentences in a beat description using abbreviation-safe splitting.
        Book rule: 1-2 sentences MAX. We allow up to 3 for punctuation tolerance.
        """
        errors: List[str] = []
        cleaned = description.strip()
        if not cleaned:
            return errors

        # Strip known abbreviations before counting
        cleaned = self.ABBREV_PATTERN.sub("ABBR", cleaned)
        # Strip ellipsis
        cleaned = re.sub(r'\.{2,}', '', cleaned)
        # Strip em-dash patterns
        cleaned = re.sub(r'[\u2014\u2013]', ' ', cleaned)

        # Count sentence-ending punctuation groups
        sentence_endings = re.findall(r'[.!?]+', cleaned)
        sentence_count = len(sentence_endings)

        if sentence_count > 3:
            errors.append(
                f"DESCRIPTION_TOO_LONG: Beat {beat_num} ({beat_name}) has ~{sentence_count} "
                f"sentences (max 2). Snyder: 'if I can't fill in the blank in one or two "
                f"sentences, I don't have the beat yet.'"
            )
        return errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each validation error."""
        suggestions: List[str] = []
        for error in errors:
            if "BEAT_COUNT" in error:
                suggestions.append(
                    "Ensure the 'beats' array contains exactly 15 beat objects, "
                    "numbered 1 through 15."
                )
            elif "MISSING_BEAT" in error:
                suggestions.append(
                    "Use the exact beat name from the BS2 list: " + ", ".join(BEAT_NAMES)
                )
            elif "EMPTY_DESCRIPTION" in error:
                suggestions.append(
                    "Write 1-2 specific sentences describing what happens at this beat."
                )
            elif "DESCRIPTION_TOO_LONG" in error:
                suggestions.append(
                    "Trim to 1-2 sentences maximum. Snyder uses a one-page form where "
                    "each beat gets one or two sentences at most."
                )
            elif "MIDPOINT_POLARITY" in error:
                suggestions.append(
                    "Set midpoint_polarity to 'up' (false victory) or 'down' (false defeat)."
                )
            elif "ALL_IS_LOST_POLARITY" in error:
                suggestions.append(
                    "Set all_is_lost_polarity to 'up' or 'down'."
                )
            elif "POLARITY_MISMATCH" in error:
                suggestions.append(
                    "All Is Lost polarity MUST be opposite of Midpoint. "
                    "If Midpoint is 'up', All Is Lost must be 'down' and vice versa."
                )
            elif "BEAT_6_NO_CHOICE" in error:
                suggestions.append(
                    "Rewrite Beat 6 to show the hero making a proactive choice "
                    "(use 'chooses', 'decides', or 'commits')."
                )
            elif "BEAT_11_NO_DEATH" in error:
                suggestions.append(
                    "Add a 'whiff of death' to Beat 11 -- literal death, symbolic death, "
                    "or mention of mortality/loss."
                )
            elif "MISSING_OPENING_IMAGE" in error:
                suggestions.append(
                    "Add Beat 1 (Opening Image) showing the hero's 'before' state visually."
                )
            elif "MISSING_FINAL_IMAGE" in error:
                suggestions.append(
                    "Add Beat 15 (Final Image) showing visual opposite of Opening Image."
                )
            elif "BEAT_14_NO" in error:
                suggestions.append(
                    "Rewrite Beat 14 (Finale) to show lessons applied, hero taking action, "
                    "and a new world order being created."
                )
            elif "MISSING_TARGET_PAGE" in error:
                suggestions.append(
                    "Add a target_page string matching the BS2 page targets."
                )
            elif "MISSING_TARGET_PCT" in error:
                suggestions.append(
                    "Add a target_percentage string matching the BS2 percentage targets."
                )
            elif "WRONG_TARGET_PAGE" in error:
                suggestions.append(
                    "Fix the target_page to match the BS2 standard page targets."
                )
            elif "WRONG_TARGET_PCT" in error:
                suggestions.append(
                    "Fix the target_percentage to match the BS2 standard percentages."
                )
            elif "INVALID_DIRECTION" in error:
                suggestions.append(
                    "Set emotional_direction to 'up', 'down', or 'neutral'."
                )
            elif "IMAGE_SAME_DIRECTION" in error:
                suggestions.append(
                    "Opening and Final Image must have opposite emotional_direction. "
                    "They are bookends showing dramatic change."
                )
            elif "BEAT_2_NO_THEME" in error:
                suggestions.append(
                    "Rewrite Beat 2 to reference a thematic statement or question "
                    "spoken by someone other than the hero."
                )
            elif "BEAT_4_NO_EVENT" in error:
                suggestions.append(
                    "Rewrite Beat 4 to describe a single external event "
                    "(news, discovery, arrival, etc.)."
                )
            elif "BEAT_5_NO_QUESTION" in error:
                suggestions.append(
                    "Rewrite Beat 5 to pose a question or show the hero's hesitation/doubt."
                )
            elif "BEAT_7_NO_CHARACTER" in error:
                suggestions.append(
                    "Rewrite Beat 7 to introduce a new character or relationship "
                    "that carries the theme."
                )
            elif "BEAT_8_NO_PREMISE" in error:
                suggestions.append(
                    "Rewrite Beat 8 to reference the premise, concept, or "
                    "'promise of the premise.'"
                )
            elif "BEAT_10_NO" in error:
                suggestions.append(
                    "Rewrite Beat 10 to include BOTH external threats (bad guys, danger) "
                    "AND internal problems (doubt, dissent, team fracture)."
                )
            elif "BEAT_12_NO_DESPAIR" in error:
                suggestions.append(
                    "Rewrite Beat 12 to show the hero's despair, hopelessness, or defeat."
                )
            elif "BEAT_13_NO_MERGER" in error:
                suggestions.append(
                    "Rewrite Beat 13 to show A+B story merger -- the hero realizes "
                    "the solution through the B-story insight."
                )
            elif "INVALID_ACT_LABEL" in error:
                suggestions.append(
                    "Set act_label to 'thesis', 'antithesis', or 'synthesis'."
                )
            elif "WRONG_ACT_LABEL" in error:
                suggestions.append(
                    "Fix act_label: beats 1-6 = 'thesis', 7-12 = 'antithesis', "
                    "13-15 = 'synthesis'."
                )
            else:
                suggestions.append(
                    "Review the BS2 beat sheet structure and ensure all 15 beats "
                    "are present with correct names, fields, and content."
                )
        return suggestions
