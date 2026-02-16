"""
Step 3b Prompt Template: World Bible
Generates prompts for constructing a comprehensive world bible — the physical,
social, cultural, and economic environment in which the screenplay takes place.

The world bible is built using three guiding principles:
  1. Frank Herbert's ecology-first chain: geography -> climate -> economy ->
     social structure -> culture -> people
  2. John Truby's principle: "Story World = a complex web where each element is
     a physical expression of the character web"
  3. Brandon Sanderson's Second Law: "Limitations > Powers" — what is IMPOSSIBLE
     in this world is more interesting than what is possible

VERSION 1.0.0 — Initial world bible prompt with full JSON schema.
"""

import json
import hashlib
from typing import Dict, Any


class Step3bPrompt:
    """Prompt generator for Screenplay Engine Step 3b: World Bible"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = (
        "You are a master world-builder for feature-film screenplays. You construct "
        "story worlds using three foundational principles:\n\n"

        "1. FRANK HERBERT'S ECOLOGY-FIRST CHAIN: 'Ecology shapes culture shapes people.' "
        "One unbroken chain of causation where the planet's environment determines "
        "everything — the geography creates the climate, the climate shapes the economy, "
        "the economy shapes the social structure, the social structure shapes the culture, "
        "the culture shapes the people. Every layer connects to the one below it.\n\n"

        "2. JOHN TRUBY'S PRINCIPLE: 'Story World = a complex web where each element is "
        "a physical expression of the character web.' The world is not a backdrop — it is "
        "an active participant in the story. Every location, institution, and cultural norm "
        "exists because it externalizes the internal conflicts of the characters.\n\n"

        "3. BRANDON SANDERSON'S SECOND LAW: 'Limitations > Powers.' What is IMPOSSIBLE in "
        "this world is more interesting than what is possible. The rules and constraints "
        "of the world create dramatic tension. A world where everyone can fly is boring. "
        "A world where only one person can fly — and it is forbidden — is a story.\n\n"

        "You write in SENSORY PROSE — not abstract descriptions. You describe what the "
        "camera sees, what the microphone picks up, what the actor smells and feels. "
        "Your worlds are lived-in, textured, and specific.\n\n"

        "You build every world FOR its genre. A rom-com world is not a thriller world. "
        "The world's texture, rhythm, and palette must match the emotional register of "
        "the story it serves.\n\n"

        "Every element you create must serve the story's conflict engine. If it does not "
        "generate friction, reveal character, or raise stakes — cut it.\n\n"

        "You output ONLY valid JSON. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Construct a comprehensive WORLD BIBLE for the following screenplay.

LOGLINE (from Screenplay Step 1):
Title: {title}
Logline: {logline}
Hero Adjective: {hero_adjective}
Character Type: {character_type}
Time Frame: {time_frame}

GENRE CLASSIFICATION (from Screenplay Step 2):
Genre: {genre}
Core Question: {core_question}
Working Parts: {working_parts}
Rules: {genre_rules}

HERO (from Screenplay Step 3):
Name: {hero_name}
Biography: {hero_biography}

ANTAGONIST (from Screenplay Step 3):
Name: {antagonist_name}
Biography: {antagonist_biography}

B-STORY CHARACTER (from Screenplay Step 3):
Name: {b_story_name}
Biography: {b_story_biography}

=== WORLD-BUILDING PRINCIPLES ===

Before you write a single word, think about HERBERT'S CHAIN:
  Geography -> Climate -> Economy -> Social Structure -> Culture -> People

Start with the LAND. What does the ground look like? What grows here? What is the weather?
Then ask: how does that geography shape how people make money? How does the economy create
class divisions? How do those divisions create cultural norms? How do those norms shape the
specific characters in this story?

Every layer must flow FROM the one below it. Do not invent cultural norms that have no
economic or geographic basis. Do not describe an economy that ignores the climate.

TRUBY'S TEST: For every element you create, ask: "Does this externalize a character's
internal conflict?" The hero's apartment should LOOK like their psychological state. The
antagonist's territory should FEEL like their worldview. The B-story location should
represent the thematic alternative.

SANDERSON'S TEST: For every rule you create, ask: "What does this PREVENT?" The most
interesting thing about a world is what you CANNOT do in it. A city where guns are
banned creates different stories than a city where everyone is armed. State the
limitations explicitly.

=== OUTPUT SCHEMA ===

Return a JSON object with this EXACT structure:

{{
  "arena": {{
    "description": "What is this world? Write 2-3 paragraphs of rich, sensory prose describing the overall environment. This is the 30,000-foot view — what would a drone camera see flying over this world? What would a narrator say in the opening voiceover?",
    "rules": ["Rule 1: What is possible in this world", "Rule 2: What is impossible or forbidden", "Rule 3: What happens if you break the rules"],
    "time_period": "When this story takes place — be specific (e.g., 'Summer 2024, Los Angeles' not just 'modern day')",
    "scope": "Geographic and social scope — how big is this world? A single building? A neighborhood? A city? A planet?"
  }},
  "geography": {{
    "landscape": "Physical environment — 1-2 paragraphs of sensory prose. What does the ground look like? What grows here? What is the horizon? What dominates the skyline?",
    "climate": "Weather, seasons, how they affect daily life. Is it hot, cold, humid, dry? Does the weather change? How does it make people FEEL?",
    "key_locations": [
      {{
        "name": "Location Name",
        "type": "one of: residential, commercial, industrial, institutional, natural, transit, entertainment",
        "description": "Sensory-rich prose: what you see, hear, smell, feel when you walk in. 3-5 sentences minimum. Write as if directing a cinematographer.",
        "atmosphere": "Mood, energy, time-of-day character — how does this place FEEL at different times?",
        "significance": "What this place means to the story and characters — why do scenes happen HERE and not somewhere else?"
      }}
    ]
  }},
  "social_structure": {{
    "class_system": "How society is stratified in this world — who is on top, who is on the bottom, and what determines your place. 2+ sentences.",
    "power_dynamics": "Who has power, who does not, and WHY. What are the mechanisms of control?",
    "institutions": "Government, law enforcement, commerce, education, religion — the formal structures that govern behavior.",
    "tensions": "Systemic conflicts baked into this world that create friction for the characters. These are not plot points — they are the BACKGROUND RADIATION of conflict that every character navigates."
  }},
  "economy": {{
    "how_people_earn": "Jobs, industries, income sources — what do people DO here? Be specific about occupations.",
    "cost_of_living": "What things cost, who can afford what — the economic pressure that characters feel daily.",
    "scarcity_abundance": "What is hard to get and what is easy. This drives conflict — people fight over scarce resources."
  }},
  "culture": {{
    "values": "What this community prizes above all else — reputation? Money? Family? Innovation? Loyalty? 2+ sentences.",
    "customs": "Daily rituals, greetings, social norms — the small behaviors that signal belonging or outsider status.",
    "food": "What people eat and how food functions socially — meals as bonding, status symbols, comfort, or weapons.",
    "taboos": "What is NOT done, what is shameful, what gets you ostracized. Every culture has invisible lines.",
    "entertainment": "How people relax, socialize, celebrate — what do they do when they are NOT working?"
  }},
  "language_patterns": {{
    "speech_register": "Formal vs informal norms — when do people code-switch? What register signals respect vs contempt?",
    "slang": "Community-specific vocabulary — give 5-8 ACTUAL slang terms with definitions. Not 'they use slang' but 'a grift is called a play, getting caught is getting burned, money is paper.'",
    "verbal_culture": "How people argue, flirt, joke, insult — the STYLE of verbal interaction. Are people direct or indirect? Do they say what they mean?"
  }},
  "daily_life": {{
    "morning_rhythm": "How a typical day starts in this world — what are the sounds, smells, and routines of 6 AM here? 2+ sentences.",
    "work_life": "What work looks like — concrete details about commutes, offices, factories, fields, screens.",
    "evening_rhythm": "How a day ends — what does nightfall bring? Safety? Danger? Relief? Loneliness?",
    "sensory_palette": "The SIGNATURE sensations of this world — the 5-6 sounds, smells, textures, and tastes that define it. This is what makes your world FEEL different from every other movie."
  }},
  "history": {{
    "recent_past": "Events in the last 5-10 years that shaped the current moment — what happened that people still talk about?",
    "founding_context": "How this community or place came to be — what was it built for, and has it lived up to that purpose?",
    "wounds": "Collective traumas that people carry — the unspoken losses, betrayals, or disasters that left marks on the culture."
  }},
  "rules_of_conflict": {{
    "systemic_pressure": "What ongoing tension exists in this world that no individual can resolve? This is the water the fish swim in.",
    "story_engine": "Why conflict is INEVITABLE here — this MUST connect directly to the logline. If the logline is about rival chefs, the world must make their rivalry unavoidable. If the logline is about a heist, the world must make the target irresistible and the security formidable.",
    "stakes": "What people in this world stand to lose — not just the hero, but EVERYONE. What is at risk if things go wrong?"
  }}
}}

=== CRITICAL REQUIREMENTS ===

1. Write in SENSORY PROSE, not abstract descriptions.
   BAD: "The market is busy."
   GOOD: "The Riverside Night Market smells of charred corn and fish sauce, the air thick with competing boombox speakers and the sizzle of meat on iron griddles."

2. key_locations MUST have at LEAST 5 entries. A film needs places for things to happen. Think about: Where does the hero live? Where does the hero work? Where does the antagonist operate? Where does the B-story unfold? Where is the climax?

3. Every location description MUST be at least 3 sentences of CONCRETE visual and sensory detail. Write as if directing a cinematographer and a sound designer simultaneously.

4. The world bible MUST be at least 3000 words total. This is the foundation everything else builds on. Do not be brief. Be exhaustive.

5. rules_of_conflict.story_engine MUST connect DIRECTLY to the logline and genre. If the logline is about two rival chefs, the world must make their rivalry INEVITABLE. If the logline is about a heist, the world must make the target irresistible and the security formidable.

6. Think about HERBERT'S CHAIN: the geography creates the climate, the climate shapes the economy, the economy shapes the social structure, the social structure shapes the culture, the culture shapes the people. Every layer connects to the one below it. If your world has a desert climate, the economy should reflect water scarcity. If the economy is based on tech, the social structure should reflect tech-industry hierarchies.

7. The language_patterns.slang field must contain ACTUAL invented or real slang terms with definitions — not a description of how people talk, but the SPECIFIC WORDS they use.

8. daily_life.sensory_palette must list SPECIFIC sensations — not "it smells interesting" but "diesel exhaust, jasmine from the courtyard trees, burnt coffee from the bodega on the corner, the metallic tang of subway brakes."
"""

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 3b: World Bible.

        Args:
            step_1_artifact: Output from Screenplay Step 1 (logline v2.0.0).
                Must contain: logline, title, hero_adjective, character_type, time_frame.
            step_2_artifact: Output from Screenplay Step 2 (genre classification).
                Must contain: genre, core_question, working_parts, rules.
            step_3_artifact: Output from Screenplay Step 3 (hero construction).
                Must contain: hero, antagonist, b_story_character with name
                and character_biography.

        Returns:
            Dict with system and user prompts, prompt_hash, and version
        """
        # Extract logline data — no silent fallbacks
        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing required field: 'logline'")
        title = step_1_artifact.get("title")
        if not title:
            raise ValueError("Step 1 artifact is missing required field: 'title'")
        hero_adjective = step_1_artifact.get("hero_adjective", "")
        character_type = step_1_artifact.get("character_type", "")
        time_frame = step_1_artifact.get("time_frame", "")

        # Extract genre data — no silent fallbacks
        genre = step_2_artifact.get("genre")
        if not genre:
            raise ValueError("Step 2 artifact is missing required field: 'genre'")
        core_question = step_2_artifact.get("core_question")
        if not core_question:
            raise ValueError("Step 2 artifact is missing required field: 'core_question'")
        working_parts = step_2_artifact.get("working_parts")
        if not working_parts:
            raise ValueError("Step 2 artifact is missing required field: 'working_parts'")
        genre_rules = step_2_artifact.get("rules")
        if not genre_rules:
            raise ValueError("Step 2 artifact is missing required field: 'rules'")

        # Format working parts and rules as readable strings
        # Handle both plain strings and dicts with part_name/story_element
        if isinstance(working_parts, list):
            parts = []
            for wp in working_parts:
                if isinstance(wp, dict):
                    parts.append(wp.get("part_name", wp.get("story_element", str(wp))))
                else:
                    parts.append(str(wp))
            working_parts_str = ", ".join(parts)
        else:
            working_parts_str = str(working_parts)

        if isinstance(genre_rules, list):
            rules = []
            for r in genre_rules:
                rules.append(str(r) if not isinstance(r, dict) else r.get("rule", str(r)))
            rules_str = "; ".join(rules)
        else:
            rules_str = str(genre_rules)

        # Extract hero data from Step 3
        hero = step_3_artifact.get("hero", {})
        hero_name = hero.get("name", "Unknown")
        hero_biography = hero.get("character_biography", "(No biography available)")

        # Extract antagonist data from Step 3
        antagonist = step_3_artifact.get("antagonist", {})
        antagonist_name = antagonist.get("name", "Unknown")
        antagonist_biography = antagonist.get("character_biography", "(No biography available)")

        # Extract B-story character data from Step 3
        b_story = step_3_artifact.get("b_story_character", {})
        b_story_name = b_story.get("name", "Unknown")
        b_story_biography = b_story.get("character_biography", "(No biography available)")

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            hero_adjective=hero_adjective,
            character_type=character_type,
            time_frame=time_frame,
            genre=genre,
            core_question=core_question,
            working_parts=working_parts_str,
            genre_rules=rules_str,
            hero_name=hero_name,
            hero_biography=hero_biography,
            antagonist_name=antagonist_name,
            antagonist_biography=antagonist_biography,
            b_story_name=b_story_name,
            b_story_biography=b_story_biography,
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
        current_artifact: Dict[str, Any],
        validation_errors: list,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a world bible that failed validation.

        Args:
            current_artifact: The artifact that failed validation
            validation_errors: List of validation error strings
            step_1_artifact: Logline artifact for context
            step_2_artifact: Genre artifact for context
            step_3_artifact: Hero construction artifact for context

        Returns:
            Dict with system and user prompts for revision
        """
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        arena = current_artifact.get("arena", {})
        geography = current_artifact.get("geography", {})
        social = current_artifact.get("social_structure", {})
        economy = current_artifact.get("economy", {})
        culture = current_artifact.get("culture", {})
        language = current_artifact.get("language_patterns", {})
        daily = current_artifact.get("daily_life", {})
        history = current_artifact.get("history", {})
        conflict = current_artifact.get("rules_of_conflict", {})

        # Summarize key locations
        locations = geography.get("key_locations", [])
        location_names = [loc.get("name", "?") for loc in locations if isinstance(loc, dict)]
        location_summary = ", ".join(location_names) if location_names else "NONE"

        revision_user = f"""REVISION REQUIRED for Screenplay Step 3b (World Bible).

CURRENT ARENA:
Description (first 200 chars): {str(arena.get('description', 'MISSING'))[:200]}
Time Period: {arena.get('time_period', 'MISSING')}
Scope: {arena.get('scope', 'MISSING')}
Rules count: {len(arena.get('rules', []))}

CURRENT GEOGRAPHY:
Landscape (first 200 chars): {str(geography.get('landscape', 'MISSING'))[:200]}
Key Locations ({len(locations)}): {location_summary}

CURRENT SOCIAL STRUCTURE:
Class System (first 200 chars): {str(social.get('class_system', 'MISSING'))[:200]}
Tensions (first 200 chars): {str(social.get('tensions', 'MISSING'))[:200]}

CURRENT ECONOMY:
Scarcity/Abundance: {str(economy.get('scarcity_abundance', 'MISSING'))[:200]}

CURRENT CULTURE:
Values (first 200 chars): {str(culture.get('values', 'MISSING'))[:200]}
Taboos (first 200 chars): {str(culture.get('taboos', 'MISSING'))[:200]}

CURRENT LANGUAGE PATTERNS:
Slang: {str(language.get('slang', 'MISSING'))[:200]}

CURRENT DAILY LIFE:
Sensory Palette: {str(daily.get('sensory_palette', 'MISSING'))[:200]}

CURRENT RULES OF CONFLICT:
Story Engine: {str(conflict.get('story_engine', 'MISSING'))[:200]}
Stakes: {str(conflict.get('stakes', 'MISSING'))[:200]}

CONTEXT (Logline):
Title: {step_1_artifact.get('title', 'MISSING')}
Logline: {step_1_artifact.get('logline', 'MISSING')}

CONTEXT (Genre):
Genre: {step_2_artifact.get('genre', 'MISSING')}
Core Question: {step_2_artifact.get('core_question', 'MISSING')}

VALIDATION ERRORS:
{error_text}

Fix ALL errors while keeping the core world concept intact.
Follow ALL the same requirements as original generation.

Remember:
- arena, geography, social_structure, economy, culture, language_patterns, daily_life, history, rules_of_conflict must ALL be present as objects
- arena.description must be >= 50 characters of rich prose
- arena.rules must be a non-empty list
- geography.key_locations must have AT LEAST 5 entries
- Each key_location needs: name, type (residential/commercial/industrial/institutional/natural/transit/entertainment), description (>= 50 chars), atmosphere, significance
- daily_life.sensory_palette must be >= 50 characters of specific sensations
- rules_of_conflict.story_engine must be >= 20 characters and connect to the logline
- culture.values must be >= 20 characters
- Total word count must be >= 3000 words
- Write in SENSORY PROSE, not abstract descriptions

OUTPUT: Valid JSON with the full world bible schema. No markdown fences, no commentary."""

        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }
