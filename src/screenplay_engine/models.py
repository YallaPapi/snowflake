"""
Screenplay Engine Data Models
All Pydantic models, enums, and data structures for the Save the Cat pipeline.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────

class SnyderGenre(str, Enum):
    """10 structural genres from Save the Cat Ch.2"""
    MONSTER_IN_THE_HOUSE = "monster_in_the_house"
    GOLDEN_FLEECE = "golden_fleece"
    OUT_OF_THE_BOTTLE = "out_of_the_bottle"
    DUDE_WITH_A_PROBLEM = "dude_with_a_problem"
    RITES_OF_PASSAGE = "rites_of_passage"
    BUDDY_LOVE = "buddy_love"
    WHYDUNIT = "whydunit"
    FOOL_TRIUMPHANT = "fool_triumphant"
    INSTITUTIONALIZED = "institutionalized"
    SUPERHERO = "superhero"


class PrimalUrge(str, Enum):
    """Every hero's goal MUST reduce to one of these 5 drives (Ch.3)"""
    SURVIVAL = "survival"
    HUNGER = "hunger"
    SEX = "sex"
    PROTECTION_OF_LOVED_ONES = "protection_of_loved_ones"
    FEAR_OF_DEATH = "fear_of_death"


class ActorArchetype(str, Enum):
    """10 recurring character types (Ch.3)"""
    YOUNG_MAN_ON_THE_RISE = "young_man_on_the_rise"
    GOOD_GIRL_TEMPTED = "good_girl_tempted"
    THE_IMP = "the_imp"
    SEX_GODDESS = "sex_goddess"
    THE_HUNK = "the_hunk"
    WOUNDED_SOLDIER = "wounded_soldier"
    TROUBLED_SEXPOT = "troubled_sexpot"
    LOVABLE_FOP = "lovable_fop"
    COURT_JESTER = "court_jester"
    WISE_GRANDFATHER = "wise_grandfather"


class StoryFormat(str, Enum):
    """Target output format — adjusts pipeline behavior"""
    TIKTOK = "tiktok"
    REEL = "reel"
    YOUTUBE = "youtube"
    SHORT_FILM = "short_film"
    FEATURE = "feature"
    SERIES_EP = "series_ep"


# ── Step 1: Logline ───────────────────────────────────────────────────────

class Logline(BaseModel):
    """Validated logline + killer title (Ch.1)

    Every field maps to a specific Snyder requirement from Chapter 1.
    Self-reported booleans replaced with structured fields that force
    the LLM to demonstrate compliance.
    """
    # Core output (R1, R2)
    logline: str = Field(..., description="1-2 sentence logline with irony")
    title: str = Field(..., description="Killer title: irony + 'says what it is' + tells the tale")

    # Component 1: Irony (R3, R4)
    ironic_element: str = Field(..., description="Explicit statement of the contradiction/dramatic tension in the logline")
    hero_adjective: str = Field(..., description="Adjective describing the hero that creates tension with their situation")

    # Component 2: Mental picture (R5, R6, R7, R25)
    character_type: str = Field(..., description="Full 'adjective + type' e.g. 'guilt-ridden bounty hunter', 'naive schoolteacher'")
    time_frame: str = Field(..., description="When the story takes place / deadline: 'one night', 'Christmas Day', 'before midnight'")
    story_beginning: str = Field(..., description="Where the story begins — implied by the logline")
    story_ending: str = Field(..., description="Where the story ends — implied by the logline")

    # Component 3: Audience and cost (R9, R10, R11, R12)
    target_audience: str = Field(..., description="Who is this for? e.g. '4-quadrant family', 'male 18-34 action'")
    budget_tier: str = Field(..., description="low (block comedy) / medium / high / tentpole — with brief justification")
    genre_tone: str = Field(..., description="Genre/tone: e.g. 'sci-fi action thriller', 'dark romantic comedy'")

    # Component 4: Killer title — validated via title field + prompt rules

    # High concept (R19) + Poster test (R23)
    high_concept_score: int = Field(default=0, ge=0, le=10, description="How 'high concept' is this? 1=obscure art film, 10=you see the poster instantly")
    poster_concept: str = Field(..., description="1-2 sentence visual concept for the movie poster/one-sheet")


# ── Step 2: Genre ─────────────────────────────────────────────────────────

class GenreDefinition(BaseModel):
    """Genre classification with working parts (Ch.2)"""
    genre: SnyderGenre
    working_parts: List[str] = Field(..., description="Required structural components")
    rules: List[str] = Field(..., description="Constraints that must be followed")
    core_question: str = Field(..., description="What the genre asks")
    example_films: List[str] = Field(default_factory=list)
    sub_types: List[str] = Field(default_factory=list, description="Genre variants with different rules")
    twist: str = Field(default="", description="What makes this 'the same thing, only different'")
    conventions: List[str] = Field(default_factory=list, description="Audience expectations for this genre")


# ── Step 3: Hero ──────────────────────────────────────────────────────────

class HeroProfile(BaseModel):
    """Fully defined protagonist (Ch.3)"""
    name: str
    adjective_descriptor: str = Field(..., description="For logline: 'ordinary cop', 'reluctant hero'")
    character_biography: str = Field(
        default="",
        description="Full prose character biography used as voice/behavior source of truth",
    )
    age_range: str = Field(default="", description="Character's approximate age range e.g. 'late 20s'")
    gender: str = Field(default="", description="Character's gender")
    archetype: ActorArchetype

    # Motivation
    primal_motivation: PrimalUrge
    stated_goal: str = Field(..., description="What hero says they want")
    actual_need: str = Field(..., description="What hero actually needs (learned via theme)")

    # Conflict potential
    maximum_conflict_justification: str
    longest_journey_justification: str

    # Likability
    save_the_cat_moment: str = Field(..., description="Specific early scene showing likability through ACTION")
    six_things_that_need_fixing: List[str] = Field(..., min_length=6, max_length=6)

    # Arc
    opening_state: str = Field(..., description="Who hero is at Opening Image")
    final_state: str = Field(..., description="Who hero is at Final Image (must be opposite)")
    theme_carrier: str = Field(..., description="How protagonist embodies the central question")


class AntagonistProfile(BaseModel):
    """Antagonist constructed to mirror hero (Ch.3 + Ch.7)"""
    name: str
    adjective_descriptor: str
    character_biography: str = Field(
        default="",
        description="Full prose antagonist biography; antagonist remains static (no arc).",
    )
    power_level: str = Field(..., description="Equal or slightly superior to hero")
    moral_difference: str = Field(..., description="Willing to do things hero won't")
    mirror_principle: str = Field(..., description="How they are two halves of same person")


class BStoryCharacter(BaseModel):
    """B-story character carrying the theme (Ch.4 beat 7)"""
    name: str
    character_biography: str = Field(
        default="",
        description="Full prose biography with voice and behavior traits",
    )
    relationship_to_hero: str
    theme_wisdom: str = Field(..., description="The lesson they teach that solves A-story")
    opening_state: str = Field(
        default="",
        description="Who this character is when first introduced",
    )
    final_state: str = Field(
        default="",
        description="Who this character becomes by the Final Image (must differ from opening_state)",
    )


# ── Step 3b: Supporting Cast ──────────────────────────────────────────────

class SupportingCharacter(BaseModel):
    """One supporting character defined before screenplay writing"""
    name: str
    role: str = Field(..., description="Narrative role: ally, mentor, rival, love_interest, authority, victim, comic_relief, henchman, witness, other")
    relationship_to_hero: str = Field(..., description="How they relate to the protagonist")
    arc_summary: str = Field(default="", description="Brief character arc if any (static characters can be empty)")
    distinctive_trait: str = Field(default="", description="Limp and Eye Patch: one memorable physical/behavioral/verbal trait")
    voice_profile: str = Field(default="", description="Speech pattern: vocabulary, sentence length, verbal tics")
    first_appearance_beat: str = Field(default="", description="Which beat they first appear in")


class SupportingCast(BaseModel):
    """Complete supporting cast defined between Hero (Step 3) and Beat Sheet (Step 4)"""
    characters: List[SupportingCharacter] = Field(..., min_length=4, max_length=20)
    total_speaking_roles: int = Field(default=0, description="Total characters with dialogue")
    total_non_speaking: int = Field(default=0, description="Named but silent characters")


# ── Step 4: Beat Sheet ────────────────────────────────────────────────────

class Beat(BaseModel):
    """One of 15 beats in the BS2 (Ch.4)"""
    number: int = Field(..., ge=1, le=15)
    name: str
    act_label: str = Field(default="", description="thesis/antithesis/synthesis -- which of Snyder's three worlds")
    target_page: str = Field(..., description="Target page(s) e.g. '1' or '30-55'")
    target_percentage: str = Field(..., description="Position as % e.g. '0-1%' or '27-50%'")
    description: str = Field(..., description="1-2 sentences MAX")
    snowflake_mapping: str = Field(default="", description="Which Snowflake output feeds this beat")
    emotional_direction: str = Field(default="", description="up/down/neutral")


class BeatSheet(BaseModel):
    """The Blake Snyder Beat Sheet (BS2) — 15 beats (Ch.4)"""
    beats: List[Beat] = Field(..., min_length=15, max_length=15)
    midpoint_polarity: str = Field(..., description="'up' (false victory) or 'down' (false defeat)")
    all_is_lost_polarity: str = Field(..., description="Must be opposite of midpoint")


# ── Step 5: The Board ─────────────────────────────────────────────────────

class BoardCard(BaseModel):
    """One scene card on The Board (Ch.5)"""
    card_number: int = Field(..., ge=1, le=45)
    row: int = Field(..., ge=1, le=4)
    scene_heading: str = Field(..., description="INT./EXT. LOCATION - TIME")
    description: str = Field(..., description="1-2 lines of what happens")
    beat: str = Field(..., description="Which of the 15 beats this belongs to")
    emotional_start: str = Field(..., description="'+' or '-' — scene starts at this polarity")
    emotional_end: str = Field(..., description="'+' or '-' — scene ends at this polarity (must differ from start for dynamic scenes)")
    conflict: str = Field(..., description="Who wants what from whom; who wins")
    storyline_color: str = Field(..., description="'A' (main), 'B' (theme/love), 'C', 'D', 'E'")
    characters_present: List[str] = Field(default_factory=list)
    snowflake_scene_id: str = Field(default="")


class TheBoard(BaseModel):
    """The complete Board — 4 rows x ~10 cards (Ch.5)"""
    row_1_act_one: List[BoardCard] = Field(default_factory=list)
    row_2_act_two_a: List[BoardCard] = Field(default_factory=list)
    row_3_act_two_b: List[BoardCard] = Field(default_factory=list)
    row_4_act_three: List[BoardCard] = Field(default_factory=list)

    @property
    def total_cards(self) -> int:
        return len(self.row_1_act_one) + len(self.row_2_act_two_a) + len(self.row_3_act_two_b) + len(self.row_4_act_three)

    @property
    def all_cards(self) -> List[BoardCard]:
        return self.row_1_act_one + self.row_2_act_two_a + self.row_3_act_two_b + self.row_4_act_three


# ── Step 6: Immutable Laws ────────────────────────────────────────────────

class LawResult(BaseModel):
    """Result of checking one immutable law"""
    law_number: int = Field(..., ge=1, le=7)
    law_name: str
    passed: bool
    violation_details: str = Field(default="")
    fix_suggestion: str = Field(default="")


# ── Step 7: Diagnostics ───────────────────────────────────────────────────

class DiagnosticResult(BaseModel):
    """Result of one diagnostic check"""
    check_number: int = Field(..., ge=1, le=9)
    check_name: str
    passed: bool
    problem_details: str = Field(default="")
    fix_suggestion: str = Field(default="")


# ── Step 8: Screenplay ────────────────────────────────────────────────────

class ScreenplayElement(BaseModel):
    """One element within a screenplay scene"""
    element_type: str = Field(..., description="slugline|action|character|dialogue|parenthetical|transition")
    content: str


class ScreenplayScene(BaseModel):
    """One complete screenplay scene"""
    scene_number: int
    slugline: str = Field(..., description="INT. COFFEE SHOP - NIGHT")
    int_ext: str = Field(..., description="INT|EXT|INT/EXT")
    location: str
    time_of_day: str = Field(..., description="DAY|NIGHT|DAWN|DUSK|CONTINUOUS")
    elements: List[ScreenplayElement] = Field(default_factory=list)
    estimated_duration_seconds: int = Field(default=60)
    beat: str
    emotional_polarity: str
    conflict: str
    characters_present: List[str] = Field(default_factory=list)
    snowflake_scene_id: str = Field(default="")
    board_card_number: int = Field(default=0)


class Screenplay(BaseModel):
    """Complete screenplay output"""
    title: str
    author: str = Field(default="AI Generated")
    format: StoryFormat
    genre: SnyderGenre
    logline: str
    total_pages: float
    estimated_duration_seconds: int
    scenes: List[ScreenplayScene] = Field(default_factory=list)


# ── Step 9: Marketing ─────────────────────────────────────────────────────

class MarketingValidation(BaseModel):
    """Marketing validation result (Ch.8)"""
    logline_still_accurate: bool
    genre_clear: bool
    audience_defined: bool
    title_works: bool
    one_sheet_concept: str = Field(default="", description="Visual poster concept")
    issues: List[str] = Field(default_factory=list)


# ── Pipeline State ─────────────────────────────────────────────────────────

BEAT_NAMES = [
    "Opening Image",
    "Theme Stated",
    "Set-Up",
    "Catalyst",
    "Debate",
    "Break into Two",
    "B Story",
    "Fun and Games",
    "Midpoint",
    "Bad Guys Close In",
    "All Is Lost",
    "Dark Night of the Soul",
    "Break into Three",
    "Finale",
    "Final Image",
]

BEAT_PAGE_TARGETS = {
    1: ("1", "0-1%"),
    2: ("5", "~5%"),
    3: ("1-10", "1-10%"),
    4: ("12", "~10%"),
    5: ("12-25", "10-23%"),
    6: ("25", "~23%"),
    7: ("30", "~27%"),
    8: ("30-55", "27-50%"),
    9: ("55", "~50%"),
    10: ("55-75", "50-68%"),
    11: ("75", "~68%"),
    12: ("75-85", "68-77%"),
    13: ("85", "~77%"),
    14: ("85-110", "77-100%"),
    15: ("110", "~100%"),
}

GENRE_DEFINITIONS: Dict[SnyderGenre, Dict[str, Any]] = {
    SnyderGenre.MONSTER_IN_THE_HOUSE: {
        "working_parts": [
            "monster", "inescapable_space", "sin_transgression",
            "trapped_victims", "run_and_hide_structure",
        ],
        "core_question": "Can they survive the monster they invited in?",
        "core_rule": "Sin invites the monster; the space must be inescapable; structure is run and hide",
        "rules": [
            "Characters must be unable to simply leave the space (no-escape constraint)",
            "The sin (usually greed) must causally create or summon the monster",
            "Monster must be sufficiently powerful that it cannot be easily overcome",
            "Monster spares those who recognize and atone for the sin",
            "Act 2/3 follows a run-and-hide escalation pattern",
        ],
        "sub_types": ["pure_monster", "domestic_monster", "serial_killer", "supernatural"],
        "example_films": [
            "Jaws", "The Exorcist", "Alien", "Fatal Attraction",
            "Jurassic Park", "Tremors",
        ],
    },
    SnyderGenre.GOLDEN_FLEECE: {
        "working_parts": [
            "road_journey", "milestones_of_growth",
            "external_goal_vs_self_discovery", "thematic_episodes",
        ],
        "core_question": "Will the journey change the hero internally?",
        "core_rule": "Hero searches for one thing and discovers himself; each incident MUST produce internal growth",
        "rules": [
            "Hero has an external goal (the fleece) that turns out less important than internal discovery",
            "Episodes must appear episodic but be thematically connected by internal growth",
            "Each milestone = an encounter with a person/event that produces a specific internal shift",
            "Internal growth IS the plot, not a side effect of the adventure",
        ],
        "sub_types": ["quest", "caper_heist", "sports", "road_movie"],
        "example_films": [
            "Star Wars", "Wizard of Oz", "Planes Trains and Automobiles",
            "Back to the Future", "Ocean's Eleven", "The Dirty Dozen",
        ],
    },
    SnyderGenre.OUT_OF_THE_BOTTLE: {
        "working_parts": [
            "wish_or_magic", "moral_lesson",
            "escalating_consequences", "magic_source",
        ],
        "core_question": "What is the real cost of getting what you wished for?",
        "core_rule": "Moral lesson REQUIRED at end; magic does not equal happiness; wish must create escalating problems",
        "rules": [
            "WISH sub-type: hero must be a put-upon Cinderella underdog; lesson that magic isn't everything",
            "COMEUPPANCE sub-type: hero is a jerk needing a swift kick; must include a Save the Cat scene showing something redeemable",
            "Prolonged success without consequence violates the genre",
            "Magic source is irrelevant (God, thing, luck, formula, divine intervention)",
        ],
        "sub_types": ["wish_fulfillment", "comeuppance_curse", "body_swap"],
        "example_films": [
            "Bruce Almighty", "The Mask", "Liar Liar", "Blank Check",
            "The Love Bug", "Freaky Friday", "Groundhog Day",
        ],
    },
    SnyderGenre.DUDE_WITH_A_PROBLEM: {
        "working_parts": [
            "ordinary_person", "extraordinary_problem",
            "individuality_as_weapon", "ordinary_day_disrupted",
        ],
        "core_question": "Can an ordinary person overcome an extraordinary threat?",
        "core_rule": "Badder bad guy equals greater hero; hero wins through individuality not superior force",
        "rules": [
            "The more average the person, the bigger the challenge should be",
            "Hero triumphs through individuality and resourcefulness, not superior force",
            "Story must begin in mundane normalcy before the extraordinary disruption arrives",
            "Stakes should be personal/domestic (save wife, protect family), not abstract",
        ],
        "sub_types": ["action_survival", "espionage", "disaster", "hostage"],
        "example_films": [
            "Die Hard", "Schindler's List", "The Terminator",
            "Titanic", "Breakdown",
        ],
    },
    SnyderGenre.RITES_OF_PASSAGE: {
        "working_parts": [
            "life_transition", "invisible_monster",
            "pain_of_transition", "dramatic_irony",
            "kubler_ross_stages",
        ],
        "core_question": "Can the hero accept the change life demands?",
        "core_rule": "Victory equals surrender and acceptance; the monster is unseen and unnamed; everyone knows except the hero",
        "rules": [
            "The 'monster' (life force) must be invisible, unnamed, and impossible to directly confront",
            "Everyone around the hero recognizes the problem except the hero themselves",
            "Structure follows Kubler-Ross stages: denial, anger, bargaining, depression, acceptance",
            "End point is the hero's ability to ultimately smile — acceptance of humanity",
        ],
        "sub_types": ["puberty", "mid_life_crisis", "aging", "grief", "addiction"],
        "example_films": [
            "10", "Ordinary People", "Days of Wine and Roses",
            "28 Days", "Lost Weekend",
        ],
    },
    SnyderGenre.BUDDY_LOVE: {
        "working_parts": [
            "two_characters", "hate_to_need_arc",
            "incomplete_halves", "separation_reunion",
            "ego_surrender",
        ],
        "core_question": "Can these two make it work despite their differences?",
        "core_rule": "Characters must start by hating each other; they are incomplete halves of a whole; All Is Lost = separation; resolution requires ego surrender",
        "rules": [
            "Characters must begin in opposition/hatred — where would they go if they didn't?",
            "They are incomplete halves of a whole — why these two MUST be together",
            "All Is Lost is a fight/goodbye-and-good-riddance that is actually none of these",
            "Resolution requires surrendering ego to win",
            "These are love stories in disguise — all buddy movies are love stories",
        ],
        "sub_types": ["love_story", "buddy_cop", "catalyst_buddy", "pet_love"],
        "example_films": [
            "Butch Cassidy and the Sundance Kid", "48 Hours",
            "Thelma & Louise", "Finding Nemo", "Rain Man",
            "Lethal Weapon", "E.T.",
        ],
    },
    SnyderGenre.WHYDUNIT: {
        "working_parts": [
            "mystery", "investigation", "dark_revelation",
            "audience_surrogate",
        ],
        "core_question": "What dark truth about human nature will be revealed?",
        "core_rule": "About audience discovering dark human nature, not hero changing; audience is the real detective",
        "rules": [
            "Who is never as interesting as WHY",
            "The onscreen character is the audience's surrogate doing the investigation for us",
            "Investigation must ultimately implicate the audience's own nature (Are we this evil?)",
            "Often involves social/institutional corruption",
        ],
        "sub_types": ["detective_noir", "political_conspiracy", "institutional_corruption"],
        "example_films": [
            "Chinatown", "Citizen Kane", "China Syndrome",
            "All The President's Men", "JFK", "The Insider",
        ],
    },
    SnyderGenre.FOOL_TRIUMPHANT: {
        "working_parts": [
            "underdog_fool", "powerful_institution",
            "insider_accomplice",
        ],
        "core_question": "Can the idiot outsmart the establishment?",
        "core_rule": "The idiot is actually the wisest; establishment is the real fool; fool wins through luck and pluck",
        "rules": [
            "Setup must repeatedly show others discounting the Fool's chances",
            "Insider accomplice gets the brunt of the slapstick/consequences",
            "Insider's crime is being close to the idiot and trying to interfere",
            "Fool triumphs by luck, pluck, and the specialness of not giving up",
        ],
        "sub_types": ["comedic_fool", "dramatic_fool"],
        "example_films": [
            "Dave", "Being There", "Amadeus", "Forrest Gump",
            "The Jerk", "Charly", "Awakenings", "The Pink Panther",
        ],
    },
    SnyderGenre.INSTITUTIONALIZED: {
        "working_parts": [
            "group", "newcomer", "cost_of_belonging",
            "breakout_character", "experienced_guide",
        ],
        "core_question": "What is crazier, me or the institution?",
        "core_rule": "Story must simultaneously honor the institution's value and expose its cost to the individual",
        "rules": [
            "Breakout character exposes the group goal as a fraud (Nicholson, Spacey, Sutherland, Pacino)",
            "Newcomer is 'us' — can literally ask 'How does that work?' to relay exposition",
            "Story must both honor the institution AND expose the problems of losing identity to it",
            "Explores herd mentality and the insanity of sacrificing oneself for the group",
        ],
        "sub_types": ["military", "corporate", "family", "school", "criminal_organization"],
        "example_films": [
            "One Flew Over the Cuckoo's Nest", "American Beauty",
            "MASH", "The Godfather", "9 to 5", "Animal House",
        ],
    },
    SnyderGenre.SUPERHERO: {
        "working_parts": [
            "extraordinary_being", "ordinary_world",
            "jealous_mediocrity", "creation_myth",
        ],
        "core_question": "What is the burden of being different?",
        "core_rule": "Must stress the PAIN and BURDEN of being different; nemesis is jealous mediocrity of ordinary people",
        "rules": [
            "Exact opposite of Dude With A Problem: extraordinary person in ordinary circumstances",
            "Antagonist is the mediocrity/jealousy of ordinary people around the hero (tiny minds)",
            "Story must establish sympathy for the hero's extraordinary burden (creation myth)",
            "Identification comes from sympathy for the plight of being misunderstood",
        ],
        "sub_types": ["literal_superhero", "gifted_individual", "mythic_figure"],
        "example_films": [
            "Superman", "Batman", "Gladiator", "A Beautiful Mind",
            "Frankenstein", "Dracula", "X-Men",
        ],
    },
}
