"""
Comprehensive tests for Screenplay Engine Step 5: The Board (40 Scene Cards)
Tests against Save the Cat! Chapter 5 ("Building The Perfect Beast") rules.

Covers:
  - Validator constants and versions
  - Board structure (4 rows, card counts, row minimums)
  - Per-card validation (conflict, polarity, headings, storylines, characters, beats)
  - Emotional change enforcement (start != end)
  - Scene heading format (INT./EXT. prefix)
  - Beat name validation against canonical BEAT_NAMES
  - Description word count (index card constraint)
  - Card number uniqueness
  - Storyline gap checks (A/B primary, C/D/E secondary)
  - Midpoint/All Is Lost opposite polarity
  - Storyline payoff in Act Three
  - Landmark beat positions
  - Fix suggestions completeness
  - Prompt generation (six things extraction, landmark positions, Snyder quotes)
  - Step implementation (version, validate_only)
"""

import pytest
from src.screenplay_engine.pipeline.validators.step_5_validator import (
    Step5Validator,
    LANDMARK_BEATS,
    LANDMARK_TOLERANCE,
    VALID_STORYLINE_COLORS,
    MAX_STORYLINE_GAP_A,
    MAX_STORYLINE_GAP_B,
    VALID_HEADING_PREFIXES,
    KNOWN_BEAT_NAMES_LOWER,
    MAX_DESCRIPTION_WORDS,
)
from src.screenplay_engine.pipeline.prompts.step_5_prompt import Step5Prompt
from src.screenplay_engine.pipeline.steps.step_5_board import Step5Board
from src.screenplay_engine.models import BEAT_NAMES


# ── Test Helpers ──────────────────────────────────────────────────────────

BEAT_SEQUENCE = [
    "Opening Image", "Theme Stated", "Set-Up", "Set-Up", "Catalyst",
    "Debate", "Debate", "Debate", "Break into Two", "Break into Two",
    "B Story", "Fun and Games", "Fun and Games", "Fun and Games", "Fun and Games",
    "Fun and Games", "Fun and Games", "Fun and Games", "Fun and Games", "Midpoint",
    "Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In",
    "Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In", "All Is Lost",
    "Dark Night of the Soul", "Break into Three",
    "Finale", "Finale", "Finale", "Finale", "Finale",
    "Finale", "Finale", "Finale", "Finale", "Final Image",
]

STORYLINE_SEQUENCE = [
    "A", "B", "A", "B", "A", "C", "B", "A", "B", "A",   # Row 1: 1-10
    "B", "A", "C", "B", "A", "B", "A", "C", "B", "A",   # Row 2: 11-20
    "B", "A", "B", "C", "A", "B", "A", "B", "C", "B",   # Row 3: 21-30
    "A", "B", "C", "A", "B", "A", "B", "C", "A", "B",   # Row 4: 31-40
]


def _make_card(num, row=None, beat=None, storyline="A",
               emotional_start="+", emotional_end="-",
               heading="INT. LOCATION - DAY", conflict="X vs Y; X wins",
               description="Something happens.", characters=None):
    """Create a valid board card dict."""
    if row is None:
        if num <= 10:
            row = 1
        elif num <= 20:
            row = 2
        elif num <= 30:
            row = 3
        else:
            row = 4
    if beat is None:
        beat = BEAT_SEQUENCE[num - 1] if num <= len(BEAT_SEQUENCE) else "Finale"
    if characters is None:
        characters = ["Hero"]
    return {
        "card_number": num,
        "row": row,
        "scene_heading": heading,
        "description": description,
        "beat": beat,
        "emotional_start": emotional_start,
        "emotional_end": emotional_end,
        "conflict": conflict,
        "storyline_color": storyline,
        "characters_present": characters,
    }


def _make_valid_board(card_count=40, cards_per_row=10):
    """Create a fully valid 40-card board artifact."""
    board = {
        "row_1_act_one": [],
        "row_2_act_two_a": [],
        "row_3_act_two_b": [],
        "row_4_act_three": [],
    }
    row_keys = list(board.keys())

    for i in range(card_count):
        num = i + 1
        row_idx = min(i // cards_per_row, 3)
        row_key = row_keys[row_idx]
        # Alternate polarity direction for variety
        if i % 2 == 0:
            e_start, e_end = "+", "-"
        else:
            e_start, e_end = "-", "+"
        storyline = STORYLINE_SEQUENCE[i] if i < len(STORYLINE_SEQUENCE) else "A"
        beat = BEAT_SEQUENCE[i] if i < len(BEAT_SEQUENCE) else "Finale"
        card = _make_card(
            num, row=row_idx + 1, beat=beat, storyline=storyline,
            emotional_start=e_start, emotional_end=e_end,
        )
        board[row_key].append(card)

    # Fix Midpoint and All Is Lost to have opposite ending polarity
    for card in board["row_2_act_two_a"]:
        if card["beat"] == "Midpoint":
            card["emotional_start"] = "-"
            card["emotional_end"] = "+"  # ends positive
    for card in board["row_3_act_two_b"]:
        if card["beat"] == "All Is Lost":
            card["emotional_start"] = "+"
            card["emotional_end"] = "-"  # ends negative (opposite of Midpoint)

    return board


def _make_step_1_artifact():
    """Create a Step 1 logline artifact for prompt tests."""
    return {
        "title": "Blackout",
        "logline": "A disgraced bounty hunter must capture an AI that controls LA's power grid before dawn, or be framed for domestic terrorism.",
    }


def _make_step_2_artifact():
    """Create a Step 2 genre artifact for prompt tests."""
    return {
        "genre": "dude_with_a_problem",
        "genre_label": "Dude with a Problem",
        "working_parts": [
            {"part_name": "ordinary_person", "description": "Rae is a regular bounty hunter."},
            {"part_name": "extraordinary_problem", "description": "An AI frames her for terrorism."},
            {"part_name": "individuality_as_weapon", "description": "Her street smarts and analog skills."},
            {"part_name": "ordinary_day_disrupted", "description": "Routine pickup turns into a citywide manhunt."},
        ],
    }


def _make_step_3_artifact():
    """Create a Step 3 hero artifact for prompt tests."""
    return {
        "hero": {
            "name": "Alex",
            "adjective_descriptor": "resourceful",
            "archetype": "Everyman",
            "stated_goal": "Find the treasure",
            "actual_need": "Find self-worth",
            "save_the_cat_moment": "Helps a lost kid find parents",
            "six_things_that_need_fixing": [
                "Can't trust anyone",
                "Refuses to ask for help",
                "Drinks too much",
                "Neglects family",
                "Lies compulsively",
                "Fear of commitment",
            ],
            "opening_state": "Isolated and bitter",
            "final_state": "Connected and hopeful",
        },
        "antagonist": {
            "name": "Victor",
            "adjective_descriptor": "ruthless",
            "mirror_principle": "Both want control but for different reasons",
        },
        "b_story_character": {
            "name": "Maya",
            "relationship_to_hero": "Love interest",
            "theme_wisdom": "You can't find treasure alone",
        },
    }


def _make_step_4_artifact():
    """Create a Step 4 beat sheet artifact for prompt tests."""
    return {
        "beats": [
            {
                "number": i + 1,
                "name": BEAT_NAMES[i],
                "description": f"Beat {i+1} description.",
                "target_page": str(i * 7 + 1),
                "emotional_direction": "up" if i % 2 == 0 else "down",
                "act_label": (
                    "thesis" if i < 6 else
                    "antithesis" if i < 12 else
                    "synthesis"
                ),
            }
            for i in range(15)
        ],
        "midpoint_polarity": "up",
        "all_is_lost_polarity": "down",
    }


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1: VERSION AND CONSTANTS
# ══════════════════════════════════════════════════════════════════════════

class TestVersionsAndConstants:
    """Test that versions and constants are correct."""

    def test_validator_version(self):
        assert Step5Validator.VERSION == "2.0.0"

    def test_prompt_version(self):
        assert Step5Prompt.VERSION == "5.0.0"

    def test_step_version(self):
        assert Step5Board.VERSION == "3.0.0"

    def test_landmark_beats_count(self):
        assert len(LANDMARK_BEATS) == 5

    def test_landmark_all_is_lost_position(self):
        """All Is Lost ~page 75 = ~card 28 (not 30)."""
        assert LANDMARK_BEATS["All Is Lost"] == 28

    def test_landmark_break_into_three_position(self):
        """Break into Three ~page 85 = ~card 30 (end of Column 3)."""
        assert LANDMARK_BEATS["Break into Three"] == 30

    def test_landmark_catalyst_position(self):
        assert LANDMARK_BEATS["Catalyst"] == 4

    def test_landmark_break_into_two_position(self):
        assert LANDMARK_BEATS["Break into Two"] == 10

    def test_landmark_midpoint_position(self):
        assert LANDMARK_BEATS["Midpoint"] == 20

    def test_landmark_tolerance(self):
        assert LANDMARK_TOLERANCE == 5

    def test_max_storyline_gap_a(self):
        """A storyline max gap is 6 consecutive cards."""
        assert MAX_STORYLINE_GAP_A == 6

    def test_max_storyline_gap_b(self):
        """B storyline max gap is 10 consecutive cards."""
        assert MAX_STORYLINE_GAP_B == 10

    def test_secondary_storylines_no_gap_limit(self):
        """C/D/E subplots have no gap limit -- Row 4 payoff check is enough."""
        # Verify the constant was removed (secondary subplots skip gap checking)
        import src.screenplay_engine.pipeline.validators.step_5_validator as mod
        assert not hasattr(mod, "MAX_STORYLINE_GAP_SECONDARY")

    def test_valid_storyline_colors(self):
        assert VALID_STORYLINE_COLORS == {"A", "B", "C", "D", "E"}

    def test_valid_heading_prefixes(self):
        assert "INT." in VALID_HEADING_PREFIXES
        assert "EXT." in VALID_HEADING_PREFIXES
        assert "INT./EXT." in VALID_HEADING_PREFIXES
        assert "I/E." in VALID_HEADING_PREFIXES

    def test_known_beat_names_matches_model(self):
        """KNOWN_BEAT_NAMES_LOWER must contain all 15 canonical beats."""
        assert len(KNOWN_BEAT_NAMES_LOWER) == 15
        for name in BEAT_NAMES:
            assert name.lower() in KNOWN_BEAT_NAMES_LOWER

    def test_max_description_words(self):
        assert MAX_DESCRIPTION_WORDS == 50


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2: VALID BOARD PASSES
# ══════════════════════════════════════════════════════════════════════════

class TestValidBoard:
    """Test that a properly constructed board passes validation."""

    def test_valid_board_passes(self):
        v = Step5Validator()
        board = _make_valid_board()
        is_valid, errors = v.validate(board)
        assert is_valid, f"Valid board should pass, got errors: {errors}"

    def test_valid_board_no_errors(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        assert len(errors) == 0


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3: BOARD STRUCTURE (rows, totals)
# ══════════════════════════════════════════════════════════════════════════

class TestBoardStructure:
    """Test row presence and card count validation."""

    def test_missing_row_detected(self):
        v = Step5Validator()
        board = _make_valid_board()
        del board["row_3_act_two_b"]
        _, errors = v.validate(board)
        assert any("MISSING_ROW" in e and "row_3_act_two_b" in e for e in errors)

    def test_too_few_cards(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_4_act_three"] = board["row_4_act_three"][:2]
        _, errors = v.validate(board)
        assert any("TOO_FEW_CARDS" in e for e in errors)

    def test_too_many_cards(self):
        v = Step5Validator()
        board = _make_valid_board()
        for i in range(10):
            board["row_1_act_one"].append(
                _make_card(41 + i, row=1, beat="Set-Up")
            )
        _, errors = v.validate(board)
        assert any("TOO_MANY_CARDS" in e for e in errors)

    def test_exact_38_cards_passes(self):
        """38 is minimum acceptable."""
        v = Step5Validator()
        board = _make_valid_board()
        # Remove 2 from row 1 (10 -> 8) = 38 total
        board["row_1_act_one"] = board["row_1_act_one"][:8]
        _, errors = v.validate(board)
        assert not any("TOO_FEW_CARDS" in e for e in errors)

    def test_exact_42_cards_passes(self):
        """42 is maximum acceptable."""
        v = Step5Validator()
        board = _make_valid_board()
        # Add 2 to row 1 (10 -> 12) = 42 total
        board["row_1_act_one"].append(_make_card(41, row=1, beat="Set-Up"))
        board["row_1_act_one"].append(_make_card(42, row=1, beat="Set-Up"))
        _, errors = v.validate(board)
        assert not any("TOO_MANY_CARDS" in e for e in errors)

    def test_row_too_light(self):
        """Each row needs at least 7 cards."""
        v = Step5Validator()
        board = _make_valid_board()
        board["row_2_act_two_a"] = board["row_2_act_two_a"][:3]
        _, errors = v.validate(board)
        assert any("ROW_TOO_LIGHT" in e and "Row 2" in e for e in errors)

    def test_act_three_light(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_4_act_three"] = board["row_4_act_three"][:2]
        _, errors = v.validate(board)
        # Either ROW_TOO_LIGHT or ACT_THREE_LIGHT should fire
        act3_errors = [e for e in errors if "Row 4" in e or "ACT_THREE" in e]
        assert len(act3_errors) > 0


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4: PER-CARD CONFLICT
# ══════════════════════════════════════════════════════════════════════════

class TestConflict:
    """Test conflict field validation."""

    def test_missing_conflict(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["conflict"] = ""
        _, errors = v.validate(board)
        assert any("MISSING_CONFLICT" in e and "Card 1" in e for e in errors)

    def test_none_conflict(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["conflict"] = None
        _, errors = v.validate(board)
        assert any("MISSING_CONFLICT" in e for e in errors)

    def test_whitespace_conflict(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["conflict"] = "   "
        _, errors = v.validate(board)
        assert any("MISSING_CONFLICT" in e for e in errors)

    def test_valid_conflict_passes(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        assert not any("MISSING_CONFLICT" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5: EMOTIONAL POLARITY (start/end and change)
# ══════════════════════════════════════════════════════════════════════════

class TestEmotionalPolarity:
    """Test emotional_start, emotional_end, and change enforcement."""

    def test_invalid_emotional_start(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_start"] = "neutral"
        _, errors = v.validate(board)
        assert any("INVALID_POLARITY_START" in e for e in errors)

    def test_invalid_emotional_end(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_end"] = "X"
        _, errors = v.validate(board)
        assert any("INVALID_POLARITY_END" in e for e in errors)

    def test_missing_emotional_end(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_end"] = ""
        _, errors = v.validate(board)
        assert any("INVALID_POLARITY_END" in e for e in errors)

    def test_no_emotional_change_detected(self):
        """Snyder: emotional tone MUST change from + to - or - to +."""
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_start"] = "+"
        board["row_1_act_one"][0]["emotional_end"] = "+"
        _, errors = v.validate(board)
        assert any("NO_EMOTIONAL_CHANGE" in e for e in errors)

    def test_emotional_change_plus_to_minus(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_start"] = "+"
        board["row_1_act_one"][0]["emotional_end"] = "-"
        _, errors = v.validate(board)
        assert not any("NO_EMOTIONAL_CHANGE" in e and "Card 1" in e for e in errors)

    def test_emotional_change_minus_to_plus(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["emotional_start"] = "-"
        board["row_1_act_one"][0]["emotional_end"] = "+"
        _, errors = v.validate(board)
        assert not any("NO_EMOTIONAL_CHANGE" in e and "Card 1" in e for e in errors)

    def test_fallback_to_emotional_polarity(self):
        """Validator falls back to emotional_polarity if emotional_start missing."""
        v = Step5Validator()
        board = _make_valid_board()
        card = board["row_1_act_one"][0]
        del card["emotional_start"]
        card["emotional_polarity"] = "+"
        card["emotional_end"] = "-"
        _, errors = v.validate(board)
        assert not any("INVALID_POLARITY_START" in e and "Card 1" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6: SCENE HEADING FORMAT
# ══════════════════════════════════════════════════════════════════════════

class TestSceneHeading:
    """Test scene heading validation."""

    def test_missing_heading(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = ""
        _, errors = v.validate(board)
        assert any("MISSING_HEADING" in e for e in errors)

    def test_bad_heading_format(self):
        """Heading must start with INT., EXT., INT./EXT., or I/E."""
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "Some random place"
        _, errors = v.validate(board)
        assert any("BAD_HEADING_FORMAT" in e for e in errors)

    def test_valid_int_heading(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "INT. COFFEE SHOP - NIGHT"
        _, errors = v.validate(board)
        assert not any("BAD_HEADING_FORMAT" in e and "Card 1" in e for e in errors)

    def test_valid_ext_heading(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "EXT. PARKING LOT - DAWN"
        _, errors = v.validate(board)
        assert not any("BAD_HEADING_FORMAT" in e and "Card 1" in e for e in errors)

    def test_valid_int_ext_heading(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "INT./EXT. CAR - MOVING - DAY"
        _, errors = v.validate(board)
        assert not any("BAD_HEADING_FORMAT" in e and "Card 1" in e for e in errors)

    def test_valid_ie_heading(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "I/E. BUILDING - DAY"
        _, errors = v.validate(board)
        assert not any("BAD_HEADING_FORMAT" in e and "Card 1" in e for e in errors)

    def test_heading_case_insensitive(self):
        """Check is case-insensitive."""
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["scene_heading"] = "int. office - day"
        _, errors = v.validate(board)
        assert not any("BAD_HEADING_FORMAT" in e and "Card 1" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7: STORYLINE COLOR
# ══════════════════════════════════════════════════════════════════════════

class TestStorylineColor:
    """Test storyline color validation."""

    def test_invalid_storyline_color(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["storyline_color"] = "X"
        _, errors = v.validate(board)
        assert any("INVALID_STORYLINE" in e for e in errors)

    def test_empty_storyline_color(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["storyline_color"] = ""
        _, errors = v.validate(board)
        assert any("INVALID_STORYLINE" in e for e in errors)

    def test_valid_a_through_e(self):
        v = Step5Validator()
        board = _make_valid_board()
        for letter in ["A", "B", "C", "D", "E"]:
            board["row_1_act_one"][0]["storyline_color"] = letter
            _, errors = v.validate(board)
            assert not any(
                "INVALID_STORYLINE" in e and "Card 1" in e for e in errors
            ), f"Storyline '{letter}' should be valid"

    def test_lowercase_storyline_accepted(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["storyline_color"] = "b"
        _, errors = v.validate(board)
        assert not any("INVALID_STORYLINE" in e and "Card 1" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8: CHARACTERS PRESENT
# ══════════════════════════════════════════════════════════════════════════

class TestCharactersPresent:
    """Test character presence validation."""

    def test_no_characters(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["characters_present"] = []
        _, errors = v.validate(board)
        assert any("NO_CHARACTERS" in e for e in errors)

    def test_characters_not_list(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["characters_present"] = "Hero"
        _, errors = v.validate(board)
        assert any("NO_CHARACTERS" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8b: CHARACTER ARCS VALIDATION (Covenant of the Arc planning)
# ══════════════════════════════════════════════════════════════════════════

class TestCharacterArcsValidation:
    """Test character_arcs field validation on board cards."""

    def test_valid_character_arcs_passes(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["character_arcs"] = {
            "Hero": "Enters confident → humbled by failure → asks for help"
        }
        is_valid, errors = v.validate(board)
        assert not any("CHARACTER_ARCS" in e or "ARC_CHARACTER" in e or "EMPTY_ARC" in e for e in errors)

    def test_character_arcs_not_dict_fails(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["character_arcs"] = "not a dict"
        _, errors = v.validate(board)
        assert any("INVALID_CHARACTER_ARCS" in e for e in errors)

    def test_arc_character_not_in_characters_present(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["characters_present"] = ["Hero"]
        board["row_1_act_one"][0]["character_arcs"] = {
            "Ghost": "Enters invisible → becomes visible"
        }
        _, errors = v.validate(board)
        assert any("ARC_CHARACTER_MISMATCH" in e and "Ghost" in e for e in errors)

    def test_empty_arc_description_fails(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["character_arcs"] = {"Hero": ""}
        _, errors = v.validate(board)
        assert any("EMPTY_ARC_DESCRIPTION" in e for e in errors)

    def test_arc_description_whitespace_only_fails(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["character_arcs"] = {"Hero": "   "}
        _, errors = v.validate(board)
        assert any("EMPTY_ARC_DESCRIPTION" in e for e in errors)

    def test_missing_character_arcs_no_error(self):
        """Cards without character_arcs should not fail (backwards compatible)."""
        v = Step5Validator()
        board = _make_valid_board()
        # Default _make_card doesn't have character_arcs
        is_valid, errors = v.validate(board)
        assert not any("CHARACTER_ARCS" in e or "ARC_CHARACTER" in e or "EMPTY_ARC" in e for e in errors)

    def test_multiple_characters_all_valid(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["characters_present"] = ["Hero", "Villain"]
        board["row_1_act_one"][0]["character_arcs"] = {
            "Hero": "Confident → humbled",
            "Villain": "Calm → aggressive"
        }
        is_valid, errors = v.validate(board)
        assert not any("ARC_CHARACTER" in e or "EMPTY_ARC" in e for e in errors)

    def test_fix_suggestion_for_invalid_arcs(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["character_arcs"] = "not a dict"
        _, errors = v.validate(board)
        suggestions = v.fix_suggestions(errors)
        assert any("character_arcs must be a dict" in s for s in suggestions)

    def test_fix_suggestion_for_arc_mismatch(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["characters_present"] = ["Hero"]
        board["row_1_act_one"][0]["character_arcs"] = {"Ghost": "Appears → vanishes"}
        _, errors = v.validate(board)
        suggestions = v.fix_suggestions(errors)
        assert any("characters_present" in s for s in suggestions)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9: BEAT NAME VALIDATION
# ══════════════════════════════════════════════════════════════════════════

class TestBeatNameValidation:
    """Test that beat names are validated against canonical BEAT_NAMES."""

    def test_invalid_beat_name(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["beat"] = "Random Nonsense"
        _, errors = v.validate(board)
        assert any("INVALID_BEAT" in e and "Random Nonsense" in e for e in errors)

    def test_missing_beat_name(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["beat"] = ""
        _, errors = v.validate(board)
        assert any("MISSING_BEAT" in e for e in errors)

    def test_valid_beat_names(self):
        """All 15 canonical beat names should be accepted."""
        v = Step5Validator()
        for name in BEAT_NAMES:
            board = _make_valid_board()
            board["row_1_act_one"][0]["beat"] = name
            _, errors = v.validate(board)
            assert not any(
                "INVALID_BEAT" in e and "Card 1" in e for e in errors
            ), f"Beat '{name}' should be valid"

    def test_beat_name_case_insensitive(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["beat"] = "opening image"
        _, errors = v.validate(board)
        assert not any("INVALID_BEAT" in e and "Card 1" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 10: DESCRIPTION WORD COUNT
# ══════════════════════════════════════════════════════════════════════════

class TestDescriptionLength:
    """Test description word count enforcement."""

    def test_description_too_long(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["description"] = " ".join(
            ["word"] * (MAX_DESCRIPTION_WORDS + 10)
        )
        _, errors = v.validate(board)
        assert any("DESCRIPTION_TOO_LONG" in e for e in errors)

    def test_description_at_limit(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["description"] = " ".join(
            ["word"] * MAX_DESCRIPTION_WORDS
        )
        _, errors = v.validate(board)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Card 1" in e for e in errors)

    def test_short_description_passes(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0]["description"] = "Hero enters the room."
        _, errors = v.validate(board)
        assert not any("DESCRIPTION_TOO_LONG" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 11: CARD NUMBER UNIQUENESS
# ══════════════════════════════════════════════════════════════════════════

class TestCardNumberUniqueness:
    """Test card number uniqueness enforcement."""

    def test_duplicate_card_number(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][1]["card_number"] = 1  # Duplicate of first card
        _, errors = v.validate(board)
        assert any("DUPLICATE_CARD_NUMBER" in e for e in errors)

    def test_unique_card_numbers_pass(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        assert not any("DUPLICATE_CARD_NUMBER" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 12: STORYLINE GAP
# ══════════════════════════════════════════════════════════════════════════

class TestStorylineGap:
    """Test storyline interleaving checks."""

    def test_a_storyline_gap_exceeds_limit(self):
        """A storyline absent for more than 6 consecutive cards triggers error."""
        v = Step5Validator()
        board = _make_valid_board()
        # Make first 8 cards all B (A absent for 8 consecutive = exceeds limit of 6)
        for i in range(min(8, len(board["row_1_act_one"]))):
            board["row_1_act_one"][i]["storyline_color"] = "B"
        # Ensure A exists later
        board["row_2_act_two_a"][0]["storyline_color"] = "A"
        board["row_3_act_two_b"][0]["storyline_color"] = "A"
        board["row_4_act_three"][0]["storyline_color"] = "A"
        _, errors = v.validate(board)
        gap_errors = [e for e in errors if "STORYLINE_GAP" in e and "'A'" in e]
        assert len(gap_errors) > 0, "A storyline gap of 8 should exceed limit of 6"

    def test_b_storyline_gap_within_limit(self):
        """B storyline can be absent for up to 8 consecutive cards."""
        v = Step5Validator()
        board = _make_valid_board()
        # B appears in the default well-interleaved board
        _, errors = v.validate(board)
        b_gap_errors = [e for e in errors if "STORYLINE_GAP" in e and "'B'" in e]
        assert len(b_gap_errors) == 0, f"B storyline gaps should be within limit: {b_gap_errors}"

    def test_secondary_storyline_gap_never_checked(self):
        """C/D/E subplots should never trigger gap errors (no gap limit)."""
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        cde_gap_errors = [e for e in errors if "STORYLINE_GAP" in e and any(f"'{c}'" in e for c in "CDE")]
        assert len(cde_gap_errors) == 0, f"C/D/E should never get gap errors: {cde_gap_errors}"

    def test_no_gap_error_for_well_interleaved_board(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        gap_errors = [e for e in errors if "STORYLINE_GAP" in e]
        assert len(gap_errors) == 0, f"Well-interleaved board should have no gap errors: {gap_errors}"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 13: MIDPOINT / ALL IS LOST POLARITY
# ══════════════════════════════════════════════════════════════════════════

class TestPolarityCheck:
    """Test Midpoint/All Is Lost opposite polarity enforcement."""

    def test_same_polarity_detected(self):
        v = Step5Validator()
        board = _make_valid_board()
        # Find midpoint and all is lost cards and set same polarity
        for card in board["row_2_act_two_a"]:
            if card["beat"] == "Midpoint":
                card["emotional_end"] = "+"
                card["emotional_start"] = "-"
        for card in board["row_3_act_two_b"]:
            if card["beat"] == "All Is Lost":
                card["emotional_end"] = "+"
                card["emotional_start"] = "-"
        _, errors = v.validate(board)
        assert any("MIDPOINT_AIS_SAME_POLARITY" in e for e in errors)

    def test_opposite_polarity_passes(self):
        v = Step5Validator()
        board = _make_valid_board()
        # Ensure opposite polarity
        for card in board["row_2_act_two_a"]:
            if card["beat"] == "Midpoint":
                card["emotional_start"] = "-"
                card["emotional_end"] = "+"
        for card in board["row_3_act_two_b"]:
            if card["beat"] == "All Is Lost":
                card["emotional_start"] = "+"
                card["emotional_end"] = "-"
        _, errors = v.validate(board)
        assert not any("MIDPOINT_AIS_SAME_POLARITY" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 14: STORYLINE PAYOFF IN ACT THREE
# ══════════════════════════════════════════════════════════════════════════

class TestStorylinePayoff:
    """Test that every storyline used in Acts 1-2 appears in Act Three."""

    def test_storyline_not_paid_off(self):
        """Only A and B storylines require Row 4 payoff. C/D/E are minor subplots."""
        v = Step5Validator()
        board = _make_valid_board()
        # Add a D storyline in row 1 but not in row 4 — should NOT error (minor subplot)
        board["row_1_act_one"][0]["storyline_color"] = "D"
        for card in board["row_4_act_three"]:
            if card["storyline_color"] == "D":
                card["storyline_color"] = "A"
        _, errors = v.validate(board)
        assert not any("STORYLINE_NO_PAYOFF" in e and "D" in e for e in errors)

    def test_primary_storyline_not_paid_off(self):
        """A storyline without Row 4 payoff MUST error — it's a primary storyline."""
        v = Step5Validator()
        board = _make_valid_board()
        # Remove all A storyline cards from row 4
        for card in board["row_4_act_three"]:
            if card["storyline_color"] == "A":
                card["storyline_color"] = "B"
        _, errors = v.validate(board)
        assert any("STORYLINE_NO_PAYOFF" in e and "A" in e for e in errors)

    def test_all_storylines_paid_off(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        assert not any("STORYLINE_NO_PAYOFF" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 15: LANDMARK BEATS
# ══════════════════════════════════════════════════════════════════════════

class TestLandmarkBeats:
    """Test landmark beat presence and position validation."""

    def test_missing_landmark(self):
        v = Step5Validator()
        board = _make_valid_board()
        # Remove Midpoint beat
        for card in board["row_2_act_two_a"]:
            if card["beat"] == "Midpoint":
                card["beat"] = "Fun and Games"
        _, errors = v.validate(board)
        assert any("MISSING_LANDMARK" in e and "Midpoint" in e for e in errors)

    def test_landmark_out_of_position(self):
        v = Step5Validator()
        board = _make_valid_board()
        # Move catalyst to card 40 (way out of position)
        for card in board["row_1_act_one"]:
            if card["beat"] == "Catalyst":
                card["beat"] = "Set-Up"
        board["row_4_act_three"][-1]["beat"] = "Catalyst"
        _, errors = v.validate(board)
        assert any("LANDMARK_POSITION" in e and "Catalyst" in e for e in errors)

    def test_all_landmarks_present_and_positioned(self):
        v = Step5Validator()
        board = _make_valid_board()
        _, errors = v.validate(board)
        assert not any("MISSING_LANDMARK" in e for e in errors)
        assert not any("LANDMARK_POSITION" in e for e in errors)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 16: FIX SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════════

class TestFixSuggestions:
    """Test that fix_suggestions covers all error types."""

    def test_all_error_types_have_suggestions(self):
        """Every error type produced by the validator must have a fix suggestion."""
        v = Step5Validator()
        error_prefixes = [
            "MISSING_ROW", "TOO_FEW_CARDS", "TOO_MANY_CARDS",
            "ROW_TOO_LIGHT", "ACT_THREE_LIGHT",
            "MISSING_CONFLICT", "INVALID_POLARITY_START", "INVALID_POLARITY_END",
            "NO_EMOTIONAL_CHANGE", "MISSING_HEADING", "BAD_HEADING_FORMAT",
            "INVALID_STORYLINE", "NO_CHARACTERS",
            "INVALID_BEAT", "MISSING_BEAT",
            "DESCRIPTION_TOO_LONG", "DUPLICATE_CARD_NUMBER",
            "STORYLINE_GAP", "MIDPOINT_AIS_SAME_POLARITY",
            "STORYLINE_NO_PAYOFF", "MISSING_LANDMARK", "LANDMARK_POSITION",
        ]
        for prefix in error_prefixes:
            error = f"{prefix}: test error"
            suggestions = v.fix_suggestions([error])
            assert len(suggestions) == 1, f"No suggestion for {prefix}"
            assert suggestions[0] != "Review and fix the indicated issue in the Board artifact.", \
                f"Generic suggestion for {prefix} — needs specific handler"

    def test_suggestion_count_matches_error_count(self):
        v = Step5Validator()
        errors = ["MISSING_CONFLICT: Card 1", "NO_CHARACTERS: Card 2", "STORYLINE_GAP: A"]
        suggestions = v.fix_suggestions(errors)
        assert len(suggestions) == len(errors)

    def test_gap_suggestion_mentions_correct_limits(self):
        v = Step5Validator()
        errors = ["STORYLINE_GAP: A disappears for 7 cards"]
        suggestions = v.fix_suggestions(errors)
        assert str(MAX_STORYLINE_GAP_A) in suggestions[0]
        assert str(MAX_STORYLINE_GAP_B) in suggestions[0]

    def test_landmark_suggestion_has_correct_positions(self):
        v = Step5Validator()
        errors = ["MISSING_LANDMARK: No card found with beat 'All Is Lost'"]
        suggestions = v.fix_suggestions(errors)
        assert "28" in suggestions[0], "Should reference card 28 for All Is Lost"
        assert "30" in suggestions[0], "Should reference card 30 for Break into Three"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 17: PROMPT GENERATION
# ══════════════════════════════════════════════════════════════════════════

class TestPromptGeneration:
    """Test prompt template content and generation."""

    def test_prompt_contains_40_card_requirement(self):
        assert "40" in Step5Prompt.USER_PROMPT_TEMPLATE

    def test_prompt_contains_snyder_quotes(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "Forty cards" in template
        assert "Only one conflict per scene" in template
        assert "emotional change" in template

    def test_prompt_landmark_positions_correct(self):
        """All Is Lost at ~card 28, Break into Three at ~card 30."""
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "All Is Lost (~card 28)" in template
        assert "Break into Three (~card 30)" in template

    def test_prompt_requires_emotional_change(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "emotional_start and emotional_end MUST differ" in template

    def test_prompt_requires_scene_heading_format(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "INT./EXT. LOCATION - TIME" in template

    def test_prompt_lists_canonical_beat_names(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        for name in BEAT_NAMES:
            assert name in template, f"Beat name '{name}' missing from prompt"

    def test_prompt_mentions_six_things(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "Six Things That Need Fixing" in template

    def test_prompt_mentions_act_three_payoff(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "paid off" in template.lower()

    def test_prompt_gap_limit_matches_validator(self):
        """Prompt gap limits must match validator constants."""
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "more than 3 consecutive cards" in template
        assert "more than 6 consecutive cards" in template

    def test_prompt_thesis_antithesis_synthesis(self):
        template = Step5Prompt.USER_PROMPT_TEMPLATE
        assert "THESIS" in template
        assert "ANTITHESIS" in template
        assert "SYNTHESIS" in template

    def test_revision_prompt_mentions_emotional_change(self):
        template = Step5Prompt.REVISION_PROMPT_TEMPLATE
        assert "emotional_start and emotional_end MUST differ" in template

    def test_revision_prompt_landmark_positions(self):
        template = Step5Prompt.REVISION_PROMPT_TEMPLATE
        assert "All Is Lost (~28)" in template
        assert "Break into Three (~30)" in template

    def test_revision_prompt_beat_name_requirement(self):
        template = Step5Prompt.REVISION_PROMPT_TEMPLATE
        assert "15 canonical BS2 beats" in template


# ══════════════════════════════════════════════════════════════════════════
# SECTION 18: PROMPT GENERATION WITH ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════

class TestPromptWithArtifacts:
    """Test prompt generation using actual Step 3 and Step 4 artifacts."""

    def test_generate_prompt_returns_all_keys(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result
        assert "version" in result

    def test_prompt_includes_hero_name(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Alex" in result["user"]

    def test_prompt_includes_six_things(self):
        """Six Things That Need Fixing must be in character summary."""
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Can't trust anyone" in result["user"]
        assert "Refuses to ask for help" in result["user"]
        assert "Fear of commitment" in result["user"]

    def test_prompt_includes_antagonist(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Victor" in result["user"]

    def test_prompt_includes_b_story(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Maya" in result["user"]

    def test_prompt_includes_beat_sheet_data(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Opening Image" in result["user"]
        assert "Midpoint polarity: up" in result["user"]

    def test_prompt_includes_hero_states(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert "Isolated and bitter" in result["user"]
        assert "Connected and hopeful" in result["user"]

    def test_revision_prompt_returns_all_keys(self):
        prompt_gen = Step5Prompt()
        result = prompt_gen.generate_revision_prompt(
            {"row_1_act_one": []},
            ["Error 1", "Error 2"],
            ["Fix 1", "Fix 2"],
            _make_step_4_artifact(),
            _make_step_3_artifact(),
            _make_step_1_artifact(),
            _make_step_2_artifact(),
        )
        assert "system" in result
        assert "user" in result
        assert "revision" in result
        assert result["revision"] is True

    def test_prompt_hash_deterministic(self):
        prompt_gen = Step5Prompt()
        result1 = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        result2 = prompt_gen.generate_prompt(
            _make_step_4_artifact(), _make_step_3_artifact(),
            _make_step_1_artifact(), _make_step_2_artifact(),
        )
        assert result1["prompt_hash"] == result2["prompt_hash"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 19: CHARACTER SUMMARY (six things extraction)
# ══════════════════════════════════════════════════════════════════════════

class TestCharacterSummary:
    """Test character summary generation with six things."""

    def test_six_things_extracted(self):
        prompt_gen = Step5Prompt()
        summary = prompt_gen._summarize_characters(_make_step_3_artifact())
        assert "Six Things That Need Fixing" in summary
        assert "1." in summary
        assert "6." in summary

    def test_no_six_things_graceful(self):
        prompt_gen = Step5Prompt()
        artifact = _make_step_3_artifact()
        del artifact["hero"]["six_things_that_need_fixing"]
        summary = prompt_gen._summarize_characters(artifact)
        assert "Six Things" not in summary
        assert "Alex" in summary  # Hero name still present

    def test_empty_six_things_graceful(self):
        prompt_gen = Step5Prompt()
        artifact = _make_step_3_artifact()
        artifact["hero"]["six_things_that_need_fixing"] = []
        summary = prompt_gen._summarize_characters(artifact)
        assert "Six Things" not in summary

    def test_b_story_theme_wisdom_extracted(self):
        prompt_gen = Step5Prompt()
        summary = prompt_gen._summarize_characters(_make_step_3_artifact())
        assert "treasure alone" in summary

    def test_no_character_data(self):
        prompt_gen = Step5Prompt()
        with pytest.raises(ValueError, match="missing required field.*hero"):
            prompt_gen._summarize_characters({})


# ══════════════════════════════════════════════════════════════════════════
# SECTION 20: STEP IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════

class TestStepImplementation:
    """Test Step5Board class."""

    def test_validate_only_valid(self):
        step = Step5Board()
        board = _make_valid_board()
        is_valid, msg = step.validate_only(board)
        assert is_valid
        assert "passes all validation" in msg

    def test_validate_only_invalid(self):
        step = Step5Board()
        board = {"row_1_act_one": []}
        is_valid, msg = step.validate_only(board)
        assert not is_valid
        assert "VALIDATION FAILED" in msg


# ══════════════════════════════════════════════════════════════════════════
# SECTION 21: EDGE CASES
# ══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_artifact(self):
        v = Step5Validator()
        _, errors = v.validate({})
        assert len(errors) > 0
        assert any("MISSING_ROW" in e for e in errors)

    def test_non_dict_card(self):
        v = Step5Validator()
        board = _make_valid_board()
        board["row_1_act_one"][0] = "not a dict"
        _, errors = v.validate(board)
        assert any("INVALID_CARD" in e for e in errors)

    def test_none_values_handled(self):
        v = Step5Validator()
        board = _make_valid_board()
        card = board["row_1_act_one"][0]
        card["conflict"] = None
        card["scene_heading"] = None
        card["storyline_color"] = None
        card["emotional_start"] = None
        card["emotional_end"] = None
        card["beat"] = None
        _, errors = v.validate(board)
        # Should produce multiple errors, not crash
        assert len(errors) > 0

    def test_metadata_field_ignored(self):
        """Metadata should not interfere with validation."""
        v = Step5Validator()
        board = _make_valid_board()
        board["metadata"] = {"version": "2.0.0", "created_at": "2026-02-08"}
        is_valid, errors = v.validate(board)
        assert is_valid, f"Metadata should not cause errors: {errors}"

    def test_beat_sheet_summary_with_act_labels(self):
        """Beat sheet summary should include act_label if present."""
        prompt_gen = Step5Prompt()
        artifact = _make_step_4_artifact()
        summary = prompt_gen._summarize_beat_sheet(artifact)
        assert "[thesis]" in summary
        assert "[antithesis]" in summary
        assert "[synthesis]" in summary

    def test_beat_sheet_summary_no_beats(self):
        prompt_gen = Step5Prompt()
        with pytest.raises(ValueError, match="missing required field.*beats"):
            prompt_gen._summarize_beat_sheet({})
