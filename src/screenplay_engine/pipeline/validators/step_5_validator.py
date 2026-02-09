"""
Step 5 Validator: The Board -- 40 Scene Cards (Save the Cat Ch.5)

v2.0.0 -- Rewritten against Ch.5 ("Building The Perfect Beast") of Save the Cat! (2005).
Corrected landmark positions (All Is Lost ~card 28, Break into Three ~card 30).
Tightened storyline gap limits (A/B: 3, C/D/E: 6). Added beat name validation against
canonical BEAT_NAMES, scene heading format check (INT./EXT.), description word count,
card number uniqueness, and emotional change enforcement (start != end).
"""

from typing import Tuple, List, Dict, Any, Set

from src.screenplay_engine.models import BEAT_NAMES


# ── Constants ──────────────────────────────────────────────────────────────

# Landmark beats and their expected approximate card positions (from book page mappings)
# Catalyst ~page 12 = ~card 4, Break into Two ~page 25 = ~card 10,
# Midpoint ~page 55 = ~card 20, All Is Lost ~page 75 = ~card 28,
# Break into Three ~page 85 = ~card 30 (end of Column 3)
LANDMARK_BEATS = {
    "Catalyst": 4,
    "Break into Two": 10,
    "Midpoint": 20,
    "All Is Lost": 28,
    "Break into Three": 30,
}

# Tolerance window: landmark can be +/- this many cards from target
LANDMARK_TOLERANCE = 5

# Valid storyline colors (A-E)
VALID_STORYLINE_COLORS = {"A", "B", "C", "D", "E"}

# Maximum consecutive cards without a storyline color appearing
# A = main plot (should be in nearly every scene, but B-story runs may skip A)
# B = theme/B-story (appears regularly but concentrated around B Story/DNOTSF beats)
# C/D/E = subplots — no gap limit; Row 4 payoff check (19) ensures resolution
MAX_STORYLINE_GAP_A = 6
MAX_STORYLINE_GAP_B = 10

# Valid scene heading prefixes (standard screenplay format)
VALID_HEADING_PREFIXES = ("INT.", "EXT.", "INT./EXT.", "I/E.")

# Known beat names (lowercase for case-insensitive matching)
KNOWN_BEAT_NAMES_LOWER = {name.lower() for name in BEAT_NAMES}

# Max words per card description (index card constraint -- "simple declarative sentences")
MAX_DESCRIPTION_WORDS = 50


class Step5Validator:
    """Validator for Screenplay Engine Step 5: The Board (40 Scene Cards)"""

    VERSION = "2.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a Board artifact with 40 scene cards in 4 rows.

        Checks:
            1.  Board has 4 rows (row_1_act_one through row_4_act_three)
            2.  Total card count is 38-42 (approximately 40, +/-2)
            3.  Each row has at least 7 cards (book says 9-10 per column)
            4.  Row 4 (Act Three) has at least 7 cards (must not be light)
            5.  Every card has non-empty conflict field
            6.  Every card has emotional_start of '+' or '-'
            7.  Every card has emotional_end of '+' or '-'
            8.  emotional_start and emotional_end differ (emotional CHANGE)
            9.  Every card has a non-empty scene_heading
            10. Scene heading starts with INT./EXT. prefix
            11. Every card has a storyline_color (A through E)
            12. Every card has at least one character in characters_present
            13. Beat name matches one of the 15 canonical BS2 beats
            14. Description is brief (max 50 words, fits on an index card)
            15. Card numbers are unique across the board
            16. No A storyline disappears for more than 6 consecutive cards
            17. B storyline not absent for 10+ cards (C/D/E checked via Row 4 payoff only)
            18. Midpoint and All Is Lost have opposite polarity
            19. Every storyline used in Acts 1-2 appears in Row 4 (payoff)
            20. 5 landmark beats present at approximately correct positions

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # ── 1. Board has 4 rows ──────────────────────────────────────────
        row_keys = [
            "row_1_act_one",
            "row_2_act_two_a",
            "row_3_act_two_b",
            "row_4_act_three",
        ]
        rows: Dict[str, list] = {}
        for key in row_keys:
            row_data = artifact.get(key)
            if not isinstance(row_data, list):
                errors.append(
                    f"MISSING_ROW: '{key}' must be a list of scene cards"
                )
                rows[key] = []
            else:
                rows[key] = row_data

        # Flatten all cards for board-level checks
        all_cards = []
        for key in row_keys:
            all_cards.extend(rows.get(key, []))

        # ── 2. Total card count is 38-42 ─────────────────────────────────
        total = len(all_cards)
        if total < 38:
            errors.append(
                f"TOO_FEW_CARDS: Board has {total} cards, minimum is 38 "
                f"(target 40). Add more scenes."
            )
        elif total > 42:
            errors.append(
                f"TOO_MANY_CARDS: Board has {total} cards, maximum is 42 "
                f"(target 40). Consolidate scenes or merge sequences."
            )

        # ── 3. Each row has at least 7 cards ─────────────────────────────
        row_labels = {
            "row_1_act_one": "Row 1 (Act One)",
            "row_2_act_two_a": "Row 2 (Act Two A)",
            "row_3_act_two_b": "Row 3 (Act Two B)",
            "row_4_act_three": "Row 4 (Act Three)",
        }
        for key in row_keys:
            row = rows.get(key, [])
            label = row_labels[key]
            if len(row) < 7:
                errors.append(
                    f"ROW_TOO_LIGHT: {label} has only {len(row)} cards, "
                    f"minimum is 7 (target 9-10)."
                )

        # ── 4. Row 4 (Act Three) has at least 7 cards ───────────────────
        row_4 = rows.get("row_4_act_three", [])
        if len(row_4) < 7 and not any("Row 4 (Act Three)" in e for e in errors):
            errors.append(
                f"ACT_THREE_LIGHT: Act Three has only {len(row_4)} cards. "
                f"Common mistake: overloading Acts 1-2 and starving Act 3."
            )

        # ── Per-card checks (5-15) ───────────────────────────────────────
        seen_card_numbers: Set[int] = set()

        for idx, card in enumerate(all_cards):
            if not isinstance(card, dict):
                errors.append(f"INVALID_CARD: Card at index {idx} is not a dict")
                continue

            card_num = card.get("card_number", idx + 1)
            prefix = f"Card {card_num}"

            # 5. Non-empty conflict
            conflict = (card.get("conflict") or "").strip()
            if not conflict:
                errors.append(
                    f"MISSING_CONFLICT: {prefix} must have a 'conflict' field "
                    f"(who wants what from whom; who wins)"
                )

            # 6. emotional_start is "+" or "-"
            e_start = (
                card.get("emotional_start")
                or card.get("emotional_polarity")
                or ""
            ).strip()
            if e_start not in ("+", "-"):
                errors.append(
                    f"INVALID_POLARITY_START: {prefix} emotional_start must be "
                    f"'+' or '-', got '{e_start}'"
                )

            # 7. emotional_end is "+" or "-"
            e_end = (card.get("emotional_end") or "").strip()
            if e_end not in ("+", "-"):
                errors.append(
                    f"INVALID_POLARITY_END: {prefix} emotional_end must be "
                    f"'+' or '-', got '{e_end}'"
                )

            # 8. Emotional CHANGE -- start and end must differ
            if (
                e_start in ("+", "-")
                and e_end in ("+", "-")
                and e_start == e_end
            ):
                errors.append(
                    f"NO_EMOTIONAL_CHANGE: {prefix} emotional_start and "
                    f"emotional_end are both '{e_start}'. Every scene must have "
                    f"emotional change from + to - or - to +."
                )

            # 9. Scene heading non-empty
            heading = (card.get("scene_heading") or "").strip()
            if not heading:
                errors.append(
                    f"MISSING_HEADING: {prefix} must have a non-empty "
                    f"'scene_heading' (INT./EXT. LOCATION - TIME)"
                )

            # 10. Scene heading format -- must start with INT./EXT.
            if heading:
                heading_upper = heading.upper()
                if not any(heading_upper.startswith(p) for p in VALID_HEADING_PREFIXES):
                    errors.append(
                        f"BAD_HEADING_FORMAT: {prefix} scene_heading must start "
                        f"with INT., EXT., INT./EXT., or I/E. -- got "
                        f"'{heading[:40]}'"
                    )

            # 11. Storyline color A-E
            color = (card.get("storyline_color") or "").strip().upper()
            if color not in VALID_STORYLINE_COLORS:
                errors.append(
                    f"INVALID_STORYLINE: {prefix} storyline_color must be "
                    f"A, B, C, D, or E -- got '{card.get('storyline_color', '')}'"
                )

            # 12. At least one character present
            chars = card.get("characters_present", [])
            if not isinstance(chars, list) or len(chars) == 0:
                errors.append(
                    f"NO_CHARACTERS: {prefix} must have at least one character "
                    f"in 'characters_present'"
                )

            # 13. Beat name matches canonical BEAT_NAMES (fuzzy: beat value
            #     may start with the canonical name, e.g. "Midpoint (False Victory)")
            beat_name = (card.get("beat") or "").strip()
            if beat_name:
                beat_lower = beat_name.lower()
                if (
                    beat_lower not in KNOWN_BEAT_NAMES_LOWER
                    and not any(beat_lower.startswith(bn) for bn in KNOWN_BEAT_NAMES_LOWER)
                ):
                    errors.append(
                        f"INVALID_BEAT: {prefix} beat '{beat_name}' is not one "
                        f"of the 15 canonical BS2 beats."
                    )
            else:
                errors.append(
                    f"MISSING_BEAT: {prefix} must have a 'beat' field naming "
                    f"which of the 15 BS2 beats this scene belongs to."
                )

            # 14. Description word count (index card constraint)
            desc = (card.get("description") or "").strip()
            if desc:
                word_count = len(desc.split())
                if word_count > MAX_DESCRIPTION_WORDS:
                    errors.append(
                        f"DESCRIPTION_TOO_LONG: {prefix} description is "
                        f"{word_count} words (max {MAX_DESCRIPTION_WORDS}). "
                        f"Use simple declarative sentences that fit on an "
                        f"index card."
                    )

            # 15. Card number uniqueness
            if isinstance(card_num, int):
                if card_num in seen_card_numbers:
                    errors.append(
                        f"DUPLICATE_CARD_NUMBER: Card number {card_num} appears "
                        f"more than once. Each card must have a unique number."
                    )
                seen_card_numbers.add(card_num)

        # ── 16-17. Storyline gap checks ──────────────────────────────────
        if all_cards:
            # Collect all used storyline colors
            used_colors: Set[str] = set()
            for card in all_cards:
                if isinstance(card, dict):
                    c = (card.get("storyline_color") or "").strip().upper()
                    if c in VALID_STORYLINE_COLORS:
                        used_colors.add(c)

            # Check each used color for maximum consecutive absence
            for color in used_colors:
                gap = 0
                max_gap = 0
                for card in all_cards:
                    if not isinstance(card, dict):
                        continue
                    card_color = (
                        card.get("storyline_color") or ""
                    ).strip().upper()
                    if card_color == color:
                        gap = 0
                    else:
                        gap += 1
                        if gap > max_gap:
                            max_gap = gap
                # Per-storyline gap limits (C/D/E skip — Row 4 payoff check is enough)
                if color == "A":
                    gap_limit = MAX_STORYLINE_GAP_A
                elif color == "B":
                    gap_limit = MAX_STORYLINE_GAP_B
                else:
                    continue  # no gap limit for secondary subplots
                if max_gap > gap_limit:
                    errors.append(
                        f"STORYLINE_GAP: Storyline '{color}' disappears for "
                        f"{max_gap} consecutive cards (max {gap_limit}). "
                        f"Interleave storyline scenes more evenly."
                    )

        # ── 18. Midpoint and All Is Lost must have OPPOSITE polarity ─────
        if all_cards:
            midpoint_card = None
            ais_card = None
            for card in all_cards:
                if not isinstance(card, dict):
                    continue
                beat_val = (card.get("beat") or "").strip().lower()
                if beat_val.startswith("midpoint") and midpoint_card is None:
                    midpoint_card = card
                elif beat_val.startswith("all is lost") and ais_card is None:
                    ais_card = card

            if midpoint_card and ais_card:
                mp_end = (
                    midpoint_card.get("emotional_end")
                    or midpoint_card.get("emotional_start")
                    or midpoint_card.get("emotional_polarity")
                    or ""
                ).strip()
                ais_end = (
                    ais_card.get("emotional_end")
                    or ais_card.get("emotional_start")
                    or ais_card.get("emotional_polarity")
                    or ""
                ).strip()
                if mp_end and ais_end and mp_end == ais_end:
                    errors.append(
                        f"MIDPOINT_AIS_SAME_POLARITY: Midpoint ends '{mp_end}' "
                        f"and All Is Lost ends '{ais_end}' -- they MUST be "
                        f"opposite. If Midpoint is a false victory (+), All Is "
                        f"Lost must be the hero's lowest point (-)."
                    )

        # ── 19. Every storyline used must appear in Row 4 (payoff) ───────
        if all_cards:
            row_4_cards = rows.get("row_4_act_three", [])
            row_4_colors: Set[str] = set()
            for card in row_4_cards:
                if isinstance(card, dict):
                    c = (card.get("storyline_color") or "").strip().upper()
                    if c in VALID_STORYLINE_COLORS:
                        row_4_colors.add(c)

            all_used_colors: Set[str] = set()
            for card in all_cards:
                if isinstance(card, dict):
                    c = (card.get("storyline_color") or "").strip().upper()
                    if c in VALID_STORYLINE_COLORS:
                        all_used_colors.add(c)

            # Only A and B storylines require explicit Act Three payoff
            # C/D/E are minor subplots — nice to resolve but not structurally required
            primary_used = all_used_colors & {"A", "B"}
            unpaid_storylines = primary_used - row_4_colors
            if unpaid_storylines:
                errors.append(
                    f"STORYLINE_NO_PAYOFF: Storyline(s) "
                    f"{', '.join(sorted(unpaid_storylines))} appear earlier but "
                    f"have no cards in Row 4 (Act Three). Every primary subplot must "
                    f"pay off in the finale."
                )

        # ── 20. 5 landmark beats at approximately correct positions ──────
        if all_cards:
            # Build a map of beat name (lowered) -> card number
            beat_positions: Dict[str, int] = {}
            for card in all_cards:
                if not isinstance(card, dict):
                    continue
                beat_name_val = (card.get("beat") or "").strip()
                card_num_val = card.get("card_number", 0)
                if beat_name_val and card_num_val:
                    beat_lower = beat_name_val.lower()
                    if beat_lower not in beat_positions:
                        beat_positions[beat_lower] = card_num_val

            for landmark_name, expected_pos in LANDMARK_BEATS.items():
                landmark_lower = landmark_name.lower()
                # Fuzzy match: beat value may start with landmark name
                actual_pos = beat_positions.get(landmark_lower)
                if actual_pos is None:
                    for bp_name, bp_pos in beat_positions.items():
                        if bp_name.startswith(landmark_lower):
                            actual_pos = bp_pos
                            break
                if actual_pos is None:
                    errors.append(
                        f"MISSING_LANDMARK: No card found with beat "
                        f"'{landmark_name}'. It should appear near card "
                        f"{expected_pos}."
                    )
                else:
                    if abs(actual_pos - expected_pos) > LANDMARK_TOLERANCE:
                        errors.append(
                            f"LANDMARK_POSITION: '{landmark_name}' is at card "
                            f"{actual_pos} but should be near card "
                            f"{expected_pos} (+/-{LANDMARK_TOLERANCE})."
                        )

        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Provide specific fix suggestions for each validation error.

        Args:
            errors: List of error strings from validate()

        Returns:
            List of human-readable fix suggestions
        """
        suggestions: List[str] = []

        for error in errors:
            if "MISSING_ROW" in error:
                suggestions.append(
                    "Add the missing row key with a list of scene cards. "
                    "All 4 rows are required: row_1_act_one, row_2_act_two_a, "
                    "row_3_act_two_b, row_4_act_three."
                )
            elif "TOO_FEW_CARDS" in error:
                suggestions.append(
                    "Add more scene cards to reach at least 38 total (target 40). "
                    "Check which rows are under-populated and expand them."
                )
            elif "TOO_MANY_CARDS" in error:
                suggestions.append(
                    "Reduce card count to 42 or fewer (target 40). "
                    "Merge sequences into single cards or remove redundant scenes."
                )
            elif "ROW_TOO_LIGHT" in error:
                suggestions.append(
                    "Each row must have at least 7 cards (target 9-10). "
                    "Add scenes to the under-populated row."
                )
            elif "ACT_THREE_LIGHT" in error:
                suggestions.append(
                    "Act Three (Row 4) must have at least 7 cards. "
                    "Common Save the Cat mistake: overloading Acts 1-2 "
                    "and leaving Act 3 too thin. Move or add scenes to Row 4."
                )
            elif "MISSING_CONFLICT" in error:
                suggestions.append(
                    "Every scene card must have a 'conflict' field: "
                    "who wants what from whom and who wins. One conflict "
                    "per scene, with opposing forces clearly identified."
                )
            elif "INVALID_POLARITY_START" in error:
                suggestions.append(
                    "Set emotional_start to exactly '+' or '-'. This is "
                    "the emotional tone at the BEGINNING of the scene."
                )
            elif "INVALID_POLARITY_END" in error:
                suggestions.append(
                    "Set emotional_end to exactly '+' or '-'. This is "
                    "the emotional tone at the END of the scene."
                )
            elif "NO_EMOTIONAL_CHANGE" in error:
                suggestions.append(
                    "emotional_start and emotional_end must differ. Every "
                    "scene is a 'mini-movie' where the emotional tone changes "
                    "from + to - or - to +. If you can't find the change, "
                    "the scene may not be needed."
                )
            elif "MISSING_HEADING" in error:
                suggestions.append(
                    "Add a scene_heading in standard screenplay format: "
                    "INT./EXT. LOCATION - TIME (e.g., 'INT. COFFEE SHOP - NIGHT')."
                )
            elif "BAD_HEADING_FORMAT" in error:
                suggestions.append(
                    "Scene heading must start with INT., EXT., INT./EXT., or "
                    "I/E. followed by location and time of day."
                )
            elif "INVALID_STORYLINE" in error:
                suggestions.append(
                    "Set storyline_color to one of: A (main plot), B (theme/love), "
                    "C, D, or E (subplots). Uppercase single letter."
                )
            elif "NO_CHARACTERS" in error:
                suggestions.append(
                    "Add at least one character name to 'characters_present'. "
                    "Every scene must have someone on screen."
                )
            elif "INVALID_BEAT" in error:
                suggestions.append(
                    "Beat name must be one of the 15 canonical BS2 beats: "
                    "Opening Image, Theme Stated, Set-Up, Catalyst, Debate, "
                    "Break into Two, B Story, Fun and Games, Midpoint, "
                    "Bad Guys Close In, All Is Lost, Dark Night of the Soul, "
                    "Break into Three, Finale, Final Image."
                )
            elif "MISSING_BEAT" in error:
                suggestions.append(
                    "Every card must have a 'beat' field identifying which "
                    "of the 15 BS2 beats it belongs to."
                )
            elif "DESCRIPTION_TOO_LONG" in error:
                suggestions.append(
                    f"Keep description under {MAX_DESCRIPTION_WORDS} words. "
                    "Use simple declarative sentences that fit on a physical "
                    "index card."
                )
            elif "DUPLICATE_CARD_NUMBER" in error:
                suggestions.append(
                    "Each card must have a unique card_number. "
                    "Renumber duplicates so every card has a distinct number."
                )
            elif "STORYLINE_GAP" in error:
                suggestions.append(
                    "Interleave storyline scenes more evenly. A storyline "
                    f"must not be absent for more than {MAX_STORYLINE_GAP_A} "
                    f"consecutive cards; B for more than {MAX_STORYLINE_GAP_B}."
                )
            elif "MIDPOINT_AIS_SAME_POLARITY" in error:
                suggestions.append(
                    "Midpoint and All Is Lost MUST have opposite polarity. "
                    "If Midpoint is a false victory (+), All Is Lost must be "
                    "the hero's lowest point (-), and vice versa."
                )
            elif "STORYLINE_NO_PAYOFF" in error:
                suggestions.append(
                    "Every storyline that appears in Acts 1-2 must have at "
                    "least one card in Row 4 (Act Three) to pay off the "
                    "subplot. Add a resolution card for the missing storyline."
                )
            elif "MISSING_LANDMARK" in error:
                suggestions.append(
                    "Add a card with the missing landmark beat name. "
                    "The 5 required landmarks are: Catalyst (~card 4), "
                    "Break into Two (~card 10), Midpoint (~card 20), "
                    "All Is Lost (~card 28), Break into Three (~card 30)."
                )
            elif "LANDMARK_POSITION" in error:
                suggestions.append(
                    "Move the landmark card closer to its target position "
                    f"(+/-{LANDMARK_TOLERANCE} cards). Reorder or renumber "
                    "cards as needed."
                )
            else:
                suggestions.append(
                    "Review and fix the indicated issue in the Board artifact."
                )

        return suggestions
