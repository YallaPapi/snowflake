"""
Comprehensive tests for Screenplay Engine Step 4: Beat Sheet (BS2)
Tests v2.0.0 of prompt, validator, and step implementation against
Ch.4 of Save the Cat! (2005).

Coverage targets:
  - All 28 validator checks
  - Sentence counting with abbreviations
  - Prompt generation and field mapping
  - Edge cases: missing fields, wrong types, partial artifacts
  - All keyword lists (per-beat content checks)
  - Thesis/Antithesis/Synthesis act label validation
  - BEAT_PAGE_TARGETS enforcement
  - Opening/Final Image opposition
"""

import pytest
from src.screenplay_engine.pipeline.validators.step_4_validator import Step4Validator
from src.screenplay_engine.pipeline.prompts.step_4_prompt import Step4Prompt
from src.screenplay_engine.models import BEAT_NAMES, BEAT_PAGE_TARGETS


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

def _make_beat(
    number, name, description,
    act_label=None, target_page=None, target_percentage=None,
    emotional_direction="neutral", snowflake_mapping=""
):
    """Helper to create a single beat dict with correct defaults."""
    if act_label is None:
        if number <= 6:
            act_label = "thesis"
        elif number <= 12:
            act_label = "antithesis"
        else:
            act_label = "synthesis"
    if target_page is None:
        target_page = BEAT_PAGE_TARGETS.get(number, ("", ""))[0]
    if target_percentage is None:
        target_percentage = BEAT_PAGE_TARGETS.get(number, ("", ""))[1]
    return {
        "number": number,
        "name": name,
        "act_label": act_label,
        "target_page": target_page,
        "target_percentage": target_percentage,
        "description": description,
        "snowflake_mapping": snowflake_mapping,
        "emotional_direction": emotional_direction,
    }


def _make_valid_beat_sheet():
    """Create a fully valid beat sheet artifact that passes all checks."""
    return {
        "beats": [
            _make_beat(1, "Opening Image",
                       "A lonely figure sits in a dark apartment, surrounded by empty bottles.",
                       emotional_direction="down"),
            _make_beat(2, "Theme Stated",
                       "His neighbor says 'you can't save others until you save yourself' -- the theme of the movie."),
            _make_beat(3, "Set-Up",
                       "We meet the hero's estranged family and Six Things That Need Fixing are planted."),
            _make_beat(4, "Catalyst",
                       "He receives news that his daughter has been kidnapped."),
            _make_beat(5, "Debate",
                       "Can he pull it off? Should he go alone or call the police?"),
            _make_beat(6, "Break into Two",
                       "He decides to go alone and commits to the rescue mission."),
            _make_beat(7, "B Story",
                       "He meets a new ally -- a former cop who becomes his mentor and guide."),
            _make_beat(8, "Fun and Games",
                       "The promise of the premise: a father exploring the criminal underworld to find his daughter."),
            _make_beat(9, "Midpoint",
                       "A false victory -- he finds a lead and it seems like he'll rescue her.",
                       emotional_direction="up"),
            _make_beat(10, "Bad Guys Close In",
                       "External forces tighten: the villain sends assassins. Internal doubt fractures his trust in his ally."),
            _make_beat(11, "All Is Lost",
                       "His mentor is killed -- a whiff of death. Everything he built crumbles.",
                       emotional_direction="down"),
            _make_beat(12, "Dark Night of the Soul",
                       "Alone and defeated, he sits in despair, wondering if he'll ever see his daughter again."),
            _make_beat(13, "Break into Three",
                       "He realizes the lesson his mentor taught him -- the A and B stories merge into a solution."),
            _make_beat(14, "Finale",
                       "He confronts the villain and defeats his lieutenants, then the Boss -- lessons learned are applied.",
                       emotional_direction="up"),
            _make_beat(15, "Final Image",
                       "He holds his daughter in bright sunlight, surrounded by family -- transformed.",
                       emotional_direction="up"),
        ],
        "midpoint_polarity": "up",
        "all_is_lost_polarity": "down",
    }


def _make_step_1_artifact():
    """Minimal Step 1 artifact for prompt generation."""
    return {
        "logline": "A retired detective chooses to rescue his kidnapped daughter from a criminal empire.",
        "title": "Blood Promise",
        "character_type": "retired detective",
        "ironic_element": "a man of the law must break it",
        "time_frame": "48 hours",
        "target_audience": "adults 25-54",
    }


def _make_step_2_artifact():
    """Minimal Step 2 artifact for prompt generation."""
    return {
        "genre": "Dude with a Problem",
        "rules": ["Innocent hero", "Sudden event", "Life-or-death stakes"],
        "core_question": "Can he survive the impossible situation?",
    }


def _make_step_3_artifact():
    """Minimal Step 3 artifact for prompt generation."""
    return {
        "hero": {
            "name": "Jack Morrow",
            "archetype": "Reluctant Hero",
            "primal_motivation": "protect family",
            "stated_goal": "rescue his daughter",
            "actual_need": "reconnect with his humanity",
            "save_the_cat_moment": "helps a stranger fix a flat tire",
            "six_things_that_need_fixing": [
                "alcoholism", "isolation", "guilt", "anger", "distrust", "pride"
            ],
            "opening_state": "broken, drinking alone",
            "final_state": "healed, reunited with family",
        },
        "antagonist": {
            "name": "Viktor Sokolov",
            "power_level": "crime lord with an army",
            "mirror_principle": "both will do anything for family",
        },
        "b_story_character": {
            "name": "Rosa Martinez",
            "relationship_to_hero": "former partner, now ally",
            "theme_wisdom": "you can't save others until you save yourself",
        },
    }


def _make_snowflake_artifacts():
    """Minimal Snowflake artifacts for prompt generation."""
    return {
        "step_1": {"one_sentence_summary": "A retired detective must rescue his daughter."},
        "step_2": {
            "moral_premise": "Self-sacrifice redeems past failures.",
            "sentences": {
                "disaster_1": "He's forced back into the criminal world.",
                "disaster_2": "His only lead is murdered.",
                "disaster_3": "He's captured by the villain.",
            },
        },
        "step_4": {"content": "Full synopsis of the story."},
    }


# ═══════════════════════════════════════════════════════════════════════════
# VERSION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestVersions:
    """Verify all Step 4 components are at v2.0.0."""

    def test_validator_version(self):
        assert Step4Validator.VERSION == "2.0.0"

    def test_prompt_version(self):
        assert Step4Prompt.VERSION == "2.0.0"

    def test_step_version(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        assert Step4BeatSheet.VERSION == "2.0.0"


# ═══════════════════════════════════════════════════════════════════════════
# VALID ARTIFACT PASSES ALL CHECKS
# ═══════════════════════════════════════════════════════════════════════════

class TestValidArtifact:
    """A well-formed beat sheet should pass all validation checks."""

    def test_valid_artifact_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        is_valid, errors = v.validate(artifact)
        assert is_valid, f"Expected valid, got errors: {errors}"
        assert errors == []

    def test_valid_artifact_has_15_beats(self):
        artifact = _make_valid_beat_sheet()
        assert len(artifact["beats"]) == 15

    def test_valid_artifact_all_beat_names_present(self):
        artifact = _make_valid_beat_sheet()
        names = [b["name"] for b in artifact["beats"]]
        for expected in BEAT_NAMES:
            assert expected in names, f"Missing beat name: {expected}"


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1: BEAT COUNT
# ═══════════════════════════════════════════════════════════════════════════

class TestBeatCount:
    """Validator check 1: exactly 15 beats."""

    def test_too_few_beats(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"] = artifact["beats"][:10]
        is_valid, errors = v.validate(artifact)
        assert not is_valid
        assert any("BEAT_COUNT" in e for e in errors)

    def test_too_many_beats(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"].append(_make_beat(16, "Extra Beat", "Extra."))
        is_valid, errors = v.validate(artifact)
        assert not is_valid
        assert any("BEAT_COUNT" in e for e in errors)

    def test_no_beats_list(self):
        v = Step4Validator()
        is_valid, errors = v.validate({"midpoint_polarity": "up"})
        assert not is_valid
        assert any("MISSING" in e for e in errors)

    def test_beats_not_a_list(self):
        v = Step4Validator()
        is_valid, errors = v.validate({"beats": "not a list"})
        assert not is_valid

    def test_empty_beats_list(self):
        v = Step4Validator()
        artifact = {"beats": [], "midpoint_polarity": "up", "all_is_lost_polarity": "down"}
        is_valid, errors = v.validate(artifact)
        assert not is_valid
        assert any("BEAT_COUNT" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2: BEAT NAMES
# ═══════════════════════════════════════════════════════════════════════════

class TestBeatNames:
    """Validator check 2: all expected beat names present."""

    def test_wrong_beat_name(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["name"] = "Wrong Name"
        is_valid, errors = v.validate(artifact)
        assert not is_valid
        assert any("MISSING_BEAT" in e and "Opening Image" in e for e in errors)

    def test_missing_finale_name(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][13]["name"] = "The End"
        is_valid, errors = v.validate(artifact)
        assert any("MISSING_BEAT" in e and "Finale" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3: DESCRIPTION SENTENCE COUNT
# ═══════════════════════════════════════════════════════════════════════════

class TestSentenceCount:
    """Validator check 3: 1-2 sentences per beat (max 3 with tolerance)."""

    def test_one_sentence_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "A dark room."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_two_sentences_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "A dark room. A figure sits alone."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_three_sentences_passes_tolerance(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "A dark room. A figure sits alone. Rain falls outside."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_four_sentences_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = (
            "A dark room. A figure sits alone. Rain falls outside. The phone rings."
        )
        is_valid, errors = v.validate(artifact)
        assert any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_five_sentences_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = (
            "First. Second. Third. Fourth. Fifth."
        )
        is_valid, errors = v.validate(artifact)
        assert any("DESCRIPTION_TOO_LONG" in e for e in errors)

    def test_abbreviation_dr_not_counted(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "Dr. Smith arrives at the dark office."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_abbreviation_mr_not_counted(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "Mr. Jones tells Mrs. Smith the truth."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_abbreviation_us_not_counted(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "The U.S. government sends a team."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_ellipsis_not_counted(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "He stares into the void... and sees nothing."
        is_valid, errors = v.validate(artifact)
        assert not any("DESCRIPTION_TOO_LONG" in e and "Beat 1" in e for e in errors)

    def test_empty_description_caught(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = ""
        is_valid, errors = v.validate(artifact)
        assert any("EMPTY_DESCRIPTION" in e for e in errors)

    def test_whitespace_only_description_caught(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = "   "
        is_valid, errors = v.validate(artifact)
        assert any("EMPTY_DESCRIPTION" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 4-5: POLARITY
# ═══════════════════════════════════════════════════════════════════════════

class TestPolarity:
    """Validator checks 4-5: midpoint/all-is-lost polarity."""

    def test_missing_midpoint_polarity(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        del artifact["midpoint_polarity"]
        is_valid, errors = v.validate(artifact)
        assert any("MIDPOINT_POLARITY" in e for e in errors)

    def test_invalid_midpoint_polarity(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["midpoint_polarity"] = "sideways"
        is_valid, errors = v.validate(artifact)
        assert any("MIDPOINT_POLARITY" in e for e in errors)

    def test_missing_all_is_lost_polarity(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        del artifact["all_is_lost_polarity"]
        is_valid, errors = v.validate(artifact)
        assert any("ALL_IS_LOST_POLARITY" in e for e in errors)

    def test_polarity_mismatch_both_up(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["midpoint_polarity"] = "up"
        artifact["all_is_lost_polarity"] = "up"
        is_valid, errors = v.validate(artifact)
        assert any("POLARITY_MISMATCH" in e for e in errors)

    def test_polarity_mismatch_both_down(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["midpoint_polarity"] = "down"
        artifact["all_is_lost_polarity"] = "down"
        is_valid, errors = v.validate(artifact)
        assert any("POLARITY_MISMATCH" in e for e in errors)

    def test_correct_polarity_up_down(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["midpoint_polarity"] = "up"
        artifact["all_is_lost_polarity"] = "down"
        is_valid, errors = v.validate(artifact)
        assert not any("POLARITY_MISMATCH" in e for e in errors)

    def test_correct_polarity_down_up(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["midpoint_polarity"] = "down"
        artifact["all_is_lost_polarity"] = "up"
        # Also need to adjust beat 9 and 11 directions
        artifact["beats"][8]["emotional_direction"] = "down"
        artifact["beats"][10]["emotional_direction"] = "up"
        is_valid, errors = v.validate(artifact)
        assert not any("POLARITY_MISMATCH" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 6: BEAT 6 PROACTIVE CHOICE
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat6ProactiveChoice:
    """Validator check 6: Break into Two implies proactive choice."""

    def test_decides_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "He decides to go."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_6_NO_CHOICE" in e for e in errors)

    def test_chooses_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "She chooses to fight."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_6_NO_CHOICE" in e for e in errors)

    def test_commits_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "He commits to the mission."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_6_NO_CHOICE" in e for e in errors)

    def test_no_proactive_keyword_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "He walks through the door."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_6_NO_CHOICE" in e for e in errors)

    def test_passive_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "He is dragged into the adventure by forces beyond his control."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_6_NO_CHOICE" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 7: BEAT 11 WHIFF OF DEATH
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat11WhiffOfDeath:
    """Validator check 7: All Is Lost contains whiff of death."""

    def test_death_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][10]["description"] = "His mentor is killed -- the death shakes him."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_11_NO_DEATH" in e for e in errors)

    def test_whiff_of_death_phrase_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][10]["description"] = "A whiff of death pervades the scene."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_11_NO_DEATH" in e for e in errors)

    def test_no_death_reference_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][10]["description"] = "Everything falls apart and he is very sad."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_11_NO_DEATH" in e for e in errors)

    def test_dying_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][10]["description"] = "The flower is dying in its pot as hope fades."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_11_NO_DEATH" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 8: OPENING/FINAL IMAGE EXISTENCE
# ═══════════════════════════════════════════════════════════════════════════

class TestOpeningFinalImage:
    """Validator check 8: Beat 1 and Beat 15 both exist."""

    def test_both_present(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        is_valid, errors = v.validate(artifact)
        assert not any("MISSING_OPENING_IMAGE" in e for e in errors)
        assert not any("MISSING_FINAL_IMAGE" in e for e in errors)

    def test_missing_opening_image(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["name"] = "Not Opening Image"
        artifact["beats"][0]["number"] = 99
        is_valid, errors = v.validate(artifact)
        assert any("MISSING_OPENING_IMAGE" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 9: BEAT 14 FINALE CONTENT
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat14Finale:
    """Validator check 9: Finale references lessons/action/world."""

    def test_lessons_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][13]["description"] = "He applies the lesson learned and confronts evil."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_14_NO" in e for e in errors)

    def test_defeats_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][13]["description"] = "He defeats the villain in a final showdown."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_14_NO" in e for e in errors)

    def test_no_finale_content_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][13]["description"] = "Things happen and the story ends."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_14_NO" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 10-12: TARGET PAGE AND PERCENTAGE
# ═══════════════════════════════════════════════════════════════════════════

class TestTargetPagePercentage:
    """Validator checks 10-12: target fields present and correct."""

    def test_missing_target_page(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["target_page"] = ""
        is_valid, errors = v.validate(artifact)
        assert any("MISSING_TARGET_PAGE" in e for e in errors)

    def test_missing_target_percentage(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["target_percentage"] = ""
        is_valid, errors = v.validate(artifact)
        assert any("MISSING_TARGET_PCT" in e for e in errors)

    def test_wrong_target_page(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["target_page"] = "5"  # Should be "1"
        is_valid, errors = v.validate(artifact)
        assert any("WRONG_TARGET_PAGE" in e and "Beat 1" in e for e in errors)

    def test_wrong_target_percentage(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["target_percentage"] = "50%"  # Should be "0-1%"
        is_valid, errors = v.validate(artifact)
        assert any("WRONG_TARGET_PCT" in e and "Beat 1" in e for e in errors)

    def test_correct_targets_for_all_beats(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        is_valid, errors = v.validate(artifact)
        assert not any("WRONG_TARGET_PAGE" in e for e in errors)
        assert not any("WRONG_TARGET_PCT" in e for e in errors)

    def test_all_15_beat_page_targets_exist(self):
        """BEAT_PAGE_TARGETS should have entries for beats 1-15."""
        for i in range(1, 16):
            assert i in BEAT_PAGE_TARGETS, f"Missing BEAT_PAGE_TARGETS entry for beat {i}"


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 13: EMOTIONAL DIRECTION
# ═══════════════════════════════════════════════════════════════════════════

class TestEmotionalDirection:
    """Validator check 13: emotional_direction is up/down/neutral."""

    def test_valid_directions(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        is_valid, errors = v.validate(artifact)
        assert not any("INVALID_DIRECTION" in e for e in errors)

    def test_invalid_direction(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["emotional_direction"] = "sideways"
        is_valid, errors = v.validate(artifact)
        assert any("INVALID_DIRECTION" in e for e in errors)

    def test_empty_direction_not_flagged(self):
        """Empty direction is allowed (field not required by all beats)."""
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][2]["emotional_direction"] = ""
        is_valid, errors = v.validate(artifact)
        assert not any("INVALID_DIRECTION" in e and "Beat 3" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 14: OPENING/FINAL IMAGE OPPOSITION
# ═══════════════════════════════════════════════════════════════════════════

class TestImageOpposition:
    """Validator check 14: Opening and Final Image have different directions."""

    def test_opposite_directions_pass(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["emotional_direction"] = "down"
        artifact["beats"][14]["emotional_direction"] = "up"
        is_valid, errors = v.validate(artifact)
        assert not any("IMAGE_SAME_DIRECTION" in e for e in errors)

    def test_same_direction_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["emotional_direction"] = "up"
        artifact["beats"][14]["emotional_direction"] = "up"
        is_valid, errors = v.validate(artifact)
        assert any("IMAGE_SAME_DIRECTION" in e for e in errors)

    def test_both_neutral_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["emotional_direction"] = "neutral"
        artifact["beats"][14]["emotional_direction"] = "neutral"
        is_valid, errors = v.validate(artifact)
        assert any("IMAGE_SAME_DIRECTION" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 15: BEAT 2 THEME STATED
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat2ThemeStated:
    """Validator check 15: Theme Stated references thematic content."""

    def test_theme_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][1]["description"] = "A friend states the theme: love conquers all."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_2_NO_THEME" in e for e in errors)

    def test_says_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][1]["description"] = "His mother says 'family comes first.'"
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_2_NO_THEME" in e for e in errors)

    def test_no_theme_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][1]["description"] = "The sun rises over the city."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_2_NO_THEME" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 16: BEAT 4 CATALYST
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat4Catalyst:
    """Validator check 16: Catalyst describes an external event."""

    def test_receives_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][3]["description"] = "She receives a letter with devastating news."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_4_NO_EVENT" in e for e in errors)

    def test_discovers_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][3]["description"] = "He discovers his wife has been hiding a secret."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_4_NO_EVENT" in e for e in errors)

    def test_no_event_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][3]["description"] = "Life gradually gets worse over time."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_4_NO_EVENT" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 17: BEAT 5 DEBATE
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat5Debate:
    """Validator check 17: Debate poses a question."""

    def test_question_mark_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][4]["description"] = "Can she really do this?"
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_5_NO_QUESTION" in e for e in errors)

    def test_should_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][4]["description"] = "He debates whether he should go on this journey."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_5_NO_QUESTION" in e for e in errors)

    def test_doubt_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][4]["description"] = "She is full of doubt about the mission."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_5_NO_QUESTION" in e for e in errors)

    def test_no_question_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][4]["description"] = "He packs his bags and gets ready."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_5_NO_QUESTION" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 18: BEAT 7 B STORY
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat7BStory:
    """Validator check 18: B Story references new character/theme."""

    def test_meets_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][6]["description"] = "He meets a mysterious woman who becomes his ally."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_7_NO_CHARACTER" in e for e in errors)

    def test_love_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][6]["description"] = "A love story begins with a chance encounter."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_7_NO_CHARACTER" in e for e in errors)

    def test_no_character_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][6]["description"] = "The sun sets over the landscape."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_7_NO_CHARACTER" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 19: BEAT 8 FUN AND GAMES
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat8FunAndGames:
    """Validator check 19: Fun and Games references premise/concept."""

    def test_premise_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][7]["description"] = "The promise of the premise unfolds."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_8_NO_PREMISE" in e for e in errors)

    def test_explore_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][7]["description"] = "She explores the magical world for the first time."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_8_NO_PREMISE" in e for e in errors)

    def test_no_premise_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][7]["description"] = "Time passes and nothing much happens."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_8_NO_PREMISE" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 20: BEAT 10 BAD GUYS CLOSE IN
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat10BGCI:
    """Validator check 20: BGCI has both internal AND external threats."""

    def test_both_internal_and_external_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][9]["description"] = (
            "The villain's forces attack while internal doubt tears the team apart."
        )
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_10_NO" in e for e in errors)

    def test_only_external_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][9]["description"] = "The enemy attacks with full force."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_10_NO_INTERNAL" in e for e in errors)

    def test_only_internal_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][9]["description"] = "Internal doubt and jealousy fracture the team."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_10_NO_EXTERNAL" in e for e in errors)

    def test_neither_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][9]["description"] = "Things get complicated in various ways."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_10_NO_THREATS" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 21: BEAT 12 DARK NIGHT
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat12DarkNight:
    """Validator check 21: Dark Night of the Soul shows despair."""

    def test_despair_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][11]["description"] = "He is in total despair, alone in the dark."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_12_NO_DESPAIR" in e for e in errors)

    def test_hopeless_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][11]["description"] = "She feels hopeless and broken."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_12_NO_DESPAIR" in e for e in errors)

    def test_no_despair_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][11]["description"] = "He takes a walk in the park."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_12_NO_DESPAIR" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 22: BEAT 13 BREAK INTO THREE
# ═══════════════════════════════════════════════════════════════════════════

class TestBeat13BreakIntoThree:
    """Validator check 22: Break into Three shows A+B merger."""

    def test_realizes_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][12]["description"] = "He realizes the truth from his B-story lesson."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_13_NO_MERGER" in e for e in errors)

    def test_solution_keyword_passes(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][12]["description"] = "A solution emerges from combining both stories."
        is_valid, errors = v.validate(artifact)
        assert not any("BEAT_13_NO_MERGER" in e for e in errors)

    def test_no_merger_language_fails(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][12]["description"] = "He gets up and goes outside."
        is_valid, errors = v.validate(artifact)
        assert any("BEAT_13_NO_MERGER" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 23-24: ACT LABELS
# ═══════════════════════════════════════════════════════════════════════════

class TestActLabels:
    """Validator checks 23-24: act_label validation."""

    def test_valid_act_labels(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        is_valid, errors = v.validate(artifact)
        assert not any("ACT_LABEL" in e for e in errors)

    def test_invalid_act_label_value(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["act_label"] = "prologue"
        is_valid, errors = v.validate(artifact)
        assert any("INVALID_ACT_LABEL" in e for e in errors)

    def test_wrong_act_label_thesis_beat_labeled_antithesis(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["act_label"] = "antithesis"  # Beat 1 should be thesis
        is_valid, errors = v.validate(artifact)
        assert any("WRONG_ACT_LABEL" in e and "Beat 1" in e for e in errors)

    def test_wrong_act_label_antithesis_beat_labeled_thesis(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][6]["act_label"] = "thesis"  # Beat 7 should be antithesis
        is_valid, errors = v.validate(artifact)
        assert any("WRONG_ACT_LABEL" in e and "Beat 7" in e for e in errors)

    def test_wrong_act_label_synthesis_beat_labeled_antithesis(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][12]["act_label"] = "antithesis"  # Beat 13 should be synthesis
        is_valid, errors = v.validate(artifact)
        assert any("WRONG_ACT_LABEL" in e and "Beat 13" in e for e in errors)

    def test_all_thesis_beats_1_through_6(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        for i in range(6):
            assert artifact["beats"][i]["act_label"] == "thesis", f"Beat {i+1} should be thesis"

    def test_all_antithesis_beats_7_through_12(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        for i in range(6, 12):
            assert artifact["beats"][i]["act_label"] == "antithesis", f"Beat {i+1} should be antithesis"

    def test_all_synthesis_beats_13_through_15(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        for i in range(12, 15):
            assert artifact["beats"][i]["act_label"] == "synthesis", f"Beat {i+1} should be synthesis"


# ═══════════════════════════════════════════════════════════════════════════
# FIX SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestFixSuggestions:
    """Fix suggestions are generated for all error types."""

    def test_fix_suggestions_count_matches_errors(self):
        v = Step4Validator()
        artifact = {"beats": [], "midpoint_polarity": "sideways"}
        is_valid, errors = v.validate(artifact)
        suggestions = v.fix_suggestions(errors)
        assert len(suggestions) == len(errors)

    def test_fix_suggestions_non_empty(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][5]["description"] = "He drifts along."
        is_valid, errors = v.validate(artifact)
        suggestions = v.fix_suggestions(errors)
        for s in suggestions:
            assert len(s) > 10

    def test_all_error_types_have_suggestions(self):
        """Every error code in the validator should have a matching fix suggestion."""
        v = Step4Validator()
        error_prefixes = [
            "BEAT_COUNT", "MISSING_BEAT", "EMPTY_DESCRIPTION", "DESCRIPTION_TOO_LONG",
            "MIDPOINT_POLARITY", "ALL_IS_LOST_POLARITY", "POLARITY_MISMATCH",
            "BEAT_6_NO_CHOICE", "BEAT_11_NO_DEATH", "MISSING_OPENING_IMAGE",
            "MISSING_FINAL_IMAGE", "BEAT_14_NO_RESOLUTION",
            "MISSING_TARGET_PAGE", "MISSING_TARGET_PCT",
            "WRONG_TARGET_PAGE", "WRONG_TARGET_PCT",
            "INVALID_DIRECTION", "IMAGE_SAME_DIRECTION",
            "BEAT_2_NO_THEME", "BEAT_4_NO_EVENT", "BEAT_5_NO_QUESTION",
            "BEAT_7_NO_CHARACTER", "BEAT_8_NO_PREMISE",
            "BEAT_10_NO_THREATS", "BEAT_10_NO_EXTERNAL", "BEAT_10_NO_INTERNAL",
            "BEAT_12_NO_DESPAIR", "BEAT_13_NO_MERGER",
            "INVALID_ACT_LABEL", "WRONG_ACT_LABEL",
        ]
        for prefix in error_prefixes:
            fake_errors = [f"{prefix}: test error message"]
            suggestions = v.fix_suggestions(fake_errors)
            assert len(suggestions) == 1, f"No suggestion for {prefix}"
            assert suggestions[0] != "Review the BS2 beat sheet structure and ensure all 15 beats are present with correct names, fields, and content.", \
                f"Fallback suggestion used for {prefix} -- add a specific handler"


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT GENERATION
# ═══════════════════════════════════════════════════════════════════════════

class TestPromptGeneration:
    """Step 4 prompt generation from upstream artifacts."""

    def test_generate_prompt_returns_required_keys(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result
        assert "version" in result

    def test_version_is_2_0_0(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert result["version"] == "2.0.0"

    def test_prompt_contains_logline(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "retired detective" in result["user"]

    def test_prompt_contains_hero_name(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "Jack Morrow" in result["user"]

    def test_prompt_contains_antagonist_name(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "Viktor Sokolov" in result["user"]

    def test_prompt_contains_genre(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "Dude with a Problem" in result["user"]

    def test_prompt_contains_six_things(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "alcoholism" in result["user"]

    def test_prompt_contains_thesis_framework(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "THESIS" in result["user"]
        assert "ANTITHESIS" in result["user"]
        assert "SYNTHESIS" in result["user"]

    def test_prompt_contains_act_label_field(self):
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "act_label" in result["user"]

    def test_prompt_no_5_part_finale(self):
        """The 5-part Finale from Strikes Back must NOT be in the prompt."""
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "5-part" not in result["user"]
        assert "gather team" not in result["user"]
        assert "high tower surprise" not in result["user"]
        assert "dig deep" not in result["user"].lower()

    def test_prompt_contains_ch4_finale_rules(self):
        """Finale should reference Ch.4 rules: lessons, tics, ascending, new world."""
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        user = result["user"].lower()
        assert "lessons learned" in user or "lesson" in user
        assert "ascending order" in user
        assert "change the world" in user or "new world order" in user

    def test_prompt_12_sentence_limit(self):
        """Prompt should emphasize 1-2 sentences per beat."""
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert "1-2 sentences" in result["user"]

    def test_prompt_hash_changes_with_input(self):
        p = Step4Prompt()
        result1 = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        alt_step_1 = _make_step_1_artifact()
        alt_step_1["title"] = "Different Title"
        result2 = p.generate_prompt(
            alt_step_1,
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            _make_snowflake_artifacts(),
        )
        assert result1["prompt_hash"] != result2["prompt_hash"]

    def test_system_prompt_mentions_snyder(self):
        p = Step4Prompt()
        assert "Save the Cat" in p.SYSTEM_PROMPT

    def test_system_prompt_mentions_sentence_limit(self):
        p = Step4Prompt()
        assert "two sentences" in p.SYSTEM_PROMPT


# ═══════════════════════════════════════════════════════════════════════════
# REVISION PROMPT
# ═══════════════════════════════════════════════════════════════════════════

class TestRevisionPrompt:
    """Revision prompt incorporates errors and fixes."""

    def test_revision_prompt_contains_errors(self):
        p = Step4Prompt()
        result = p.generate_revision_prompt(
            ["ERROR_1: beat missing"], ["FIX_1: add the beat"], '{"beats": []}'
        )
        assert "ERROR_1" in result["user"]

    def test_revision_prompt_contains_fixes(self):
        p = Step4Prompt()
        result = p.generate_revision_prompt(
            ["ERROR_1: beat missing"], ["FIX_1: add the beat"], '{"beats": []}'
        )
        assert "FIX_1" in result["user"]

    def test_revision_prompt_contains_previous_output(self):
        p = Step4Prompt()
        result = p.generate_revision_prompt(
            ["ERROR_1"], ["FIX_1"], '{"beats": [{"number": 1}]}'
        )
        assert '"number": 1' in result["user"]


# ═══════════════════════════════════════════════════════════════════════════
# STEP IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════

class TestStepImplementation:
    """Step 4 beat sheet implementation tests."""

    def test_parse_beat_sheet_valid_json(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        raw = '{"beats": [{"number": 1, "name": "test"}], "midpoint_polarity": "up"}'
        result = step._parse_beat_sheet(raw)
        assert "beats" in result
        assert len(result["beats"]) == 1

    def test_parse_beat_sheet_markdown_wrapped(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        raw = '```json\n{"beats": [{"number": 1}], "midpoint_polarity": "up"}\n```'
        result = step._parse_beat_sheet(raw)
        assert "beats" in result

    def test_parse_beat_sheet_invalid_returns_empty(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        raw = "This is not JSON at all."
        result = step._parse_beat_sheet(raw)
        assert result["beats"] == []

    def test_parse_beat_sheet_embedded_json(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        raw = 'Here is the beat sheet: {"beats": [{"number": 1}]} -- done'
        result = step._parse_beat_sheet(raw)
        assert "beats" in result

    def test_validate_only_valid(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        artifact = _make_valid_beat_sheet()
        is_valid, msg = step.validate_only(artifact)
        assert is_valid
        assert "passes" in msg.lower()

    def test_validate_only_invalid(self):
        from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
        step = Step4BeatSheet()
        artifact = {"beats": []}
        is_valid, msg = step.validate_only(artifact)
        assert not is_valid
        assert "FAILED" in msg


# ═══════════════════════════════════════════════════════════════════════════
# KEYWORD LIST COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════

class TestKeywordLists:
    """Verify keyword lists are non-empty and cover expected terms."""

    def test_proactive_keywords_non_empty(self):
        assert len(Step4Validator.PROACTIVE_KEYWORDS) >= 10

    def test_whiff_of_death_keywords_non_empty(self):
        assert len(Step4Validator.WHIFF_OF_DEATH_KEYWORDS) >= 10

    def test_finale_keywords_non_empty(self):
        assert len(Step4Validator.FINALE_KEYWORDS) >= 10

    def test_catalyst_keywords_non_empty(self):
        assert len(Step4Validator.CATALYST_KEYWORDS) >= 10

    def test_debate_keywords_non_empty(self):
        assert len(Step4Validator.DEBATE_KEYWORDS) >= 5

    def test_b_story_keywords_non_empty(self):
        assert len(Step4Validator.B_STORY_KEYWORDS) >= 5

    def test_fun_and_games_keywords_non_empty(self):
        assert len(Step4Validator.FUN_AND_GAMES_KEYWORDS) >= 5

    def test_bgci_external_keywords_non_empty(self):
        assert len(Step4Validator.BGCI_EXTERNAL_KEYWORDS) >= 5

    def test_bgci_internal_keywords_non_empty(self):
        assert len(Step4Validator.BGCI_INTERNAL_KEYWORDS) >= 5

    def test_dark_night_keywords_non_empty(self):
        assert len(Step4Validator.DARK_NIGHT_KEYWORDS) >= 5

    def test_break_into_three_keywords_non_empty(self):
        assert len(Step4Validator.BREAK_INTO_THREE_KEYWORDS) >= 5

    def test_expected_act_labels_has_15_entries(self):
        assert len(Step4Validator.EXPECTED_ACT_LABELS) == 15

    def test_proactive_keywords_include_chooses(self):
        assert "chooses" in Step4Validator.PROACTIVE_KEYWORDS

    def test_whiff_of_death_includes_whiff_phrase(self):
        assert "whiff of death" in Step4Validator.WHIFF_OF_DEATH_KEYWORDS

    def test_debate_keywords_include_question_mark(self):
        assert "?" in Step4Validator.DEBATE_KEYWORDS


# ═══════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_beat_with_none_description(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = None
        is_valid, errors = v.validate(artifact)
        assert any("EMPTY_DESCRIPTION" in e for e in errors)

    def test_beat_with_int_description(self):
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["description"] = 42
        is_valid, errors = v.validate(artifact)
        assert any("EMPTY_DESCRIPTION" in e for e in errors)

    def test_beat_number_not_int(self):
        """Non-integer beat numbers should not crash the validator."""
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        artifact["beats"][0]["number"] = "one"
        # Should still complete validation without error
        is_valid, errors = v.validate(artifact)
        assert isinstance(errors, list)

    def test_missing_act_label_field(self):
        """Missing act_label (not present at all) should not error."""
        v = Step4Validator()
        artifact = _make_valid_beat_sheet()
        del artifact["beats"][0]["act_label"]
        is_valid, errors = v.validate(artifact)
        # Empty string is the default from .get("act_label", "")
        # Should not produce INVALID_ACT_LABEL or WRONG_ACT_LABEL
        assert not any("INVALID_ACT_LABEL" in e and "Beat 1" in e for e in errors)

    def test_multiple_errors_accumulated(self):
        """A heavily broken artifact should produce many errors, not just one."""
        v = Step4Validator()
        artifact = {
            "beats": [
                {"number": i, "name": f"wrong_{i}", "description": "", "act_label": "wrong"}
                for i in range(1, 16)
            ],
            "midpoint_polarity": "sideways",
            "all_is_lost_polarity": "sideways",
        }
        is_valid, errors = v.validate(artifact)
        assert not is_valid
        assert len(errors) > 10

    def test_snowflake_synopsis_dict_handling(self):
        """Prompt generator handles dict-type synopsis."""
        p = Step4Prompt()
        snow = _make_snowflake_artifacts()
        snow["step_4"] = {"synopsis_paragraphs": {"p1": "First.", "p2": "Second."}}
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            snow,
        )
        assert "First." in result["user"]
        assert "Second." in result["user"]

    def test_prompt_with_empty_snowflake(self):
        """Prompt generator handles completely empty snowflake artifacts."""
        p = Step4Prompt()
        result = p.generate_prompt(
            _make_step_1_artifact(),
            _make_step_2_artifact(),
            _make_step_3_artifact(),
            {},
        )
        assert "user" in result
        assert len(result["user"]) > 100


# ═══════════════════════════════════════════════════════════════════════════
# BEAT_NAMES AND BEAT_PAGE_TARGETS CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

class TestConstants:
    """Verify the models.py constants are correct per Ch.4."""

    def test_beat_names_has_15_entries(self):
        assert len(BEAT_NAMES) == 15

    def test_beat_names_correct_order(self):
        expected = [
            "Opening Image", "Theme Stated", "Set-Up", "Catalyst", "Debate",
            "Break into Two", "B Story", "Fun and Games", "Midpoint",
            "Bad Guys Close In", "All Is Lost", "Dark Night of the Soul",
            "Break into Three", "Finale", "Final Image",
        ]
        assert BEAT_NAMES == expected

    def test_beat_page_targets_opening_image(self):
        assert BEAT_PAGE_TARGETS[1] == ("1", "0-1%")

    def test_beat_page_targets_theme_stated(self):
        assert BEAT_PAGE_TARGETS[2] == ("5", "~5%")

    def test_beat_page_targets_catalyst(self):
        assert BEAT_PAGE_TARGETS[4] == ("12", "~10%")

    def test_beat_page_targets_break_into_two(self):
        assert BEAT_PAGE_TARGETS[6] == ("25", "~23%")

    def test_beat_page_targets_midpoint(self):
        assert BEAT_PAGE_TARGETS[9] == ("55", "~50%")

    def test_beat_page_targets_all_is_lost(self):
        assert BEAT_PAGE_TARGETS[11] == ("75", "~68%")

    def test_beat_page_targets_break_into_three(self):
        assert BEAT_PAGE_TARGETS[13] == ("85", "~77%")

    def test_beat_page_targets_final_image(self):
        assert BEAT_PAGE_TARGETS[15] == ("110", "~100%")
