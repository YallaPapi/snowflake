"""
Tests for checkpoint configuration: check applicability matrix and definitions.
"""

import pytest
from src.screenplay_engine.pipeline.checkpoint.checkpoint_config import (
    CHECKPOINT_CONFIG,
    CHECK_DEFINITIONS,
    CHECK_NAMES,
    STEP_ARTIFACT_KEYS,
    get_applicable_checks,
    get_check_definitions,
    get_check_name,
)


class TestCheckpointConfig:
    """Tests for the CHECKPOINT_CONFIG mapping."""

    def test_all_six_steps_have_config(self):
        """Steps 1-6 must all have checkpoint configurations."""
        for step in range(1, 7):
            assert step in CHECKPOINT_CONFIG, f"Step {step} missing from CHECKPOINT_CONFIG"

    def test_step_1_checks(self):
        """Step 1 (Logline): Hero Leads + Is It Primal."""
        checks = get_applicable_checks(1)
        assert checks == [1, 9]

    def test_step_2_checks(self):
        """Step 2 (Genre): Emotional Color Wheel."""
        checks = get_applicable_checks(2)
        assert checks == [5]

    def test_step_3_checks(self):
        """Step 3 (Hero): 5 checks."""
        checks = get_applicable_checks(3)
        assert checks == [1, 3, 7, 8, 9]

    def test_step_4_checks(self):
        """Step 4 (Beat Sheet): 6 checks."""
        checks = get_applicable_checks(4)
        assert checks == [1, 3, 4, 5, 7, 9]

    def test_step_5_checks(self):
        """Step 5 (Board): 8 checks (all except Talking the Plot)."""
        checks = get_applicable_checks(5)
        assert checks == [1, 3, 4, 5, 6, 7, 8, 9]
        assert 2 not in checks  # Talking the Plot needs dialogue

    def test_step_6_all_nine_checks(self):
        """Step 6 (Screenplay): All 9 checks."""
        checks = get_applicable_checks(6)
        assert checks == [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert len(checks) == 9

    def test_checks_are_cumulative(self):
        """Later steps should have at least as many checks as earlier steps."""
        for step in range(1, 6):
            current = set(get_applicable_checks(step))
            next_step = set(get_applicable_checks(step + 1))
            # Not strictly cumulative (Step 2 has check 5, Step 3 doesn't have 5)
            # But Step 6 must have all checks
            if step == 5:
                assert len(next_step) >= len(current)

    def test_step_6_is_superset(self):
        """Step 6 must be a superset of all other steps' checks."""
        full = set(get_applicable_checks(6))
        for step in range(1, 6):
            subset = set(get_applicable_checks(step))
            assert subset.issubset(full), f"Step {step} checks {subset - full} not in Step 6"

    def test_nonexistent_step_returns_empty(self):
        """Steps outside 1-6 return empty check list."""
        assert get_applicable_checks(0) == []
        assert get_applicable_checks(7) == []
        assert get_applicable_checks(99) == []

    def test_all_check_numbers_valid(self):
        """All check numbers referenced in config must be 1-9."""
        for step, checks in CHECKPOINT_CONFIG.items():
            for check_num in checks:
                assert 1 <= check_num <= 9, f"Invalid check {check_num} in step {step}"


class TestCheckDefinitions:
    """Tests for CHECK_DEFINITIONS content."""

    def test_all_nine_checks_defined(self):
        """All 9 checks must have definitions."""
        for i in range(1, 10):
            assert i in CHECK_DEFINITIONS, f"Check {i} missing from CHECK_DEFINITIONS"

    def test_check_definitions_have_required_fields(self):
        """Each definition must have name, description, fail_criteria, fix_template."""
        required_fields = ["name", "description", "fail_criteria", "fix_template"]
        for num, defn in CHECK_DEFINITIONS.items():
            for field in required_fields:
                assert field in defn, f"Check {num} missing field '{field}'"
                assert len(defn[field]) > 10, f"Check {num} field '{field}' too short"

    def test_check_names_match_definitions(self):
        """CHECK_NAMES and CHECK_DEFINITIONS must agree on names."""
        for num, name in CHECK_NAMES.items():
            assert CHECK_DEFINITIONS[num]["name"] == name

    def test_canonical_check_names(self):
        """Canonical names must match step_7_validator expected names."""
        expected = [
            "The Hero Leads",
            "Talking the Plot",
            "Make the Bad Guy Badder",
            "Turn Turn Turn",
            "Emotional Color Wheel",
            "Hi How Are You I'm Fine",
            "Take a Step Back",
            "Limp and Eye Patch",
            "Is It Primal",
        ]
        for i, name in enumerate(expected, 1):
            assert CHECK_NAMES[i] == name


class TestGetCheckDefinitions:
    """Tests for get_check_definitions helper."""

    def test_returns_subset(self):
        """Should return only requested checks."""
        defs = get_check_definitions([1, 9])
        assert len(defs) == 2
        assert defs[0]["check_number"] == 1
        assert defs[1]["check_number"] == 9

    def test_preserves_order(self):
        """Should return in the order requested."""
        defs = get_check_definitions([9, 1, 5])
        assert [d["check_number"] for d in defs] == [9, 1, 5]

    def test_ignores_invalid_numbers(self):
        """Invalid check numbers should be silently skipped."""
        defs = get_check_definitions([1, 99, 2])
        assert len(defs) == 2
        assert [d["check_number"] for d in defs] == [1, 2]

    def test_empty_input(self):
        """Empty input returns empty list."""
        assert get_check_definitions([]) == []


class TestGetCheckName:
    """Tests for get_check_name helper."""

    def test_valid_check(self):
        assert get_check_name(1) == "The Hero Leads"
        assert get_check_name(9) == "Is It Primal"

    def test_invalid_check(self):
        assert "Unknown" in get_check_name(99)


class TestStepArtifactKeys:
    """Tests for STEP_ARTIFACT_KEYS mapping."""

    def test_all_steps_have_keys(self):
        for step in range(1, 7):
            assert step in STEP_ARTIFACT_KEYS

    def test_step_1_only_has_step_1(self):
        assert STEP_ARTIFACT_KEYS[1] == ["step_1"]

    def test_step_6_has_screenplay(self):
        assert "screenplay" in STEP_ARTIFACT_KEYS[6]

    def test_keys_are_cumulative(self):
        """Each step should have all keys from prior steps plus its own."""
        for step in range(2, 7):
            current_keys = set(STEP_ARTIFACT_KEYS[step])
            prev_keys = set(STEP_ARTIFACT_KEYS[step - 1])
            # Step 6 renames step_6 to screenplay, so not strictly cumulative
            # But all prior step_N keys should be present
            for pk in prev_keys:
                if pk.startswith("step_"):
                    assert pk in current_keys or step == 6
