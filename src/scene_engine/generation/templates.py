"""
Template System for Scene Generation

This implements subtask 44.2: Template System
Scene templates and prompt management for consistent generation following
Snowflake Method patterns with genre-specific and situation-specific templates.
"""

import json
import yaml
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re

from ..models import SceneType, ViewpointType, TenseType


class TemplateType(Enum):
    """Types of scene templates"""
    OPENING = "opening"
    CONTINUATION = "continuation"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    TRANSITION = "transition"
    FLASHBACK = "flashback"
    DIALOGUE_HEAVY = "dialogue_heavy"
    ACTION_SEQUENCE = "action_sequence"
    INTROSPECTIVE = "introspective"
    REVEAL = "reveal"


class GenreTemplate(Enum):
    """Genre-specific template categories"""
    LITERARY = "literary"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    HORROR = "horror"
    HISTORICAL = "historical"
    YOUNG_ADULT = "young_adult"
    ADVENTURE = "adventure"


@dataclass
class PromptTemplate:
    """Template for generation prompts"""
    template_id: str
    name: str
    description: str
    scene_type: SceneType
    template_type: TemplateType
    genre_affinity: List[GenreTemplate]
    
    # Core template content
    system_prompt: str
    structure_prompt: str
    style_prompt: str
    ending_prompt: str
    
    # Template parameters
    default_word_count: int = 1000
    complexity_level: str = "medium"  # simple, medium, complex
    emotional_range: List[str] = None
    typical_settings: List[str] = None
    
    # Usage statistics
    usage_count: int = 0
    average_rating: float = 0.0
    
    def __post_init__(self):
        if self.emotional_range is None:
            self.emotional_range = []
        if self.typical_settings is None:
            self.typical_settings = []


@dataclass
class SceneTemplate:
    """Complete scene template with structure and examples"""
    template_id: str
    name: str
    description: str
    scene_type: SceneType
    template_type: TemplateType
    
    # Structural elements
    opening_patterns: List[str]
    development_patterns: List[str]
    climax_patterns: List[str]
    resolution_patterns: List[str]
    
    # Scene-specific structure
    proactive_structure: Optional[Dict[str, str]] = None
    reactive_structure: Optional[Dict[str, str]] = None
    
    # Style guidelines
    pov_recommendations: List[ViewpointType] = None
    tense_recommendations: List[TenseType] = None
    pacing_notes: str = ""
    dialogue_ratio: str = "balanced"  # low, balanced, high
    
    # Content guidelines
    required_elements: List[str] = None
    avoid_elements: List[str] = None
    genre_considerations: Dict[str, str] = None
    
    # Example content
    example_openings: List[str] = None
    example_endings: List[str] = None
    
    def __post_init__(self):
        if self.pov_recommendations is None:
            self.pov_recommendations = [ViewpointType.THIRD]
        if self.tense_recommendations is None:
            self.tense_recommendations = [TenseType.PAST]
        if self.required_elements is None:
            self.required_elements = []
        if self.avoid_elements is None:
            self.avoid_elements = []
        if self.genre_considerations is None:
            self.genre_considerations = {}
        if self.example_openings is None:
            self.example_openings = []
        if self.example_endings is None:
            self.example_endings = []


class TemplateLibrary:
    """Library of built-in scene templates"""
    
    @staticmethod
    def get_proactive_opening_template() -> SceneTemplate:
        """Template for opening proactive scenes"""
        return SceneTemplate(
            template_id="proactive_opening_001",
            name="Proactive Opening Scene",
            description="Opening scene that establishes character goals and initial conflict",
            scene_type=SceneType.PROACTIVE,
            template_type=TemplateType.OPENING,
            opening_patterns=[
                "Character in their normal world",
                "Character responding to inciting incident",
                "Character making crucial decision",
                "Character facing immediate challenge"
            ],
            development_patterns=[
                "Goal becomes clear through action",
                "Obstacles appear more formidable",
                "Stakes increase with new information",
                "Character commits to course of action"
            ],
            climax_patterns=[
                "Direct confrontation with main obstacle",
                "Character's strength/weakness tested",
                "Moment of highest tension in scene",
                "Choice that determines outcome"
            ],
            resolution_patterns=[
                "Goal partially achieved but cost revealed",
                "Goal failed but new path discovered",
                "Temporary victory with larger problem emerging",
                "Character changed by attempt"
            ],
            proactive_structure={
                "goal_establishment": "Clear, specific goal stated early",
                "conflict_escalation": "Opposition grows stronger throughout",
                "setback_impact": "Failure creates new complications"
            },
            pacing_notes="Start strong, build tension steadily, end with clear setback",
            dialogue_ratio="balanced",
            required_elements=["clear goal", "visible opposition", "character agency"],
            avoid_elements=["passive observation", "easy victories", "unclear stakes"],
            example_openings=[
                "Sarah gripped the steering wheel tighter as she approached the courthouse.",
                "The letter arrived on a Tuesday, changing everything Marcus thought he knew.",
                "Elena had thirty minutes to find the missing file before the meeting."
            ],
            example_endings=[
                "The door slammed shut, leaving him trapped in the very place he'd tried to escape.",
                "She found the evidence she needed, but at a cost she hadn't anticipated.",
                "The plan had worked perfectly, except for the one thing he hadn't considered."
            ]
        )
    
    @staticmethod
    def get_reactive_continuation_template() -> SceneTemplate:
        """Template for continuing reactive scenes"""
        return SceneTemplate(
            template_id="reactive_continuation_001",
            name="Reactive Continuation Scene",
            description="Scene where character processes setback and makes new plan",
            scene_type=SceneType.REACTIVE,
            template_type=TemplateType.CONTINUATION,
            opening_patterns=[
                "Character reeling from previous setback",
                "Character in private moment of reflection",
                "Character seeking counsel or support",
                "Character assessing damage and options"
            ],
            development_patterns=[
                "Emotional reaction fully expressed",
                "Multiple options considered",
                "Advice or insight received",
                "Internal conflict resolved"
            ],
            climax_patterns=[
                "Moment of clarity about path forward",
                "Decision between competing values",
                "Acceptance of necessary sacrifice",
                "Commitment despite uncertainty"
            ],
            resolution_patterns=[
                "Clear decision about next action",
                "New goal established for next scene",
                "Character transformed by decision",
                "Stakes clarified for future scenes"
            ],
            reactive_structure={
                "reaction_authenticity": "Genuine emotional response to setback",
                "dilemma_complexity": "Multiple valid but conflicting options",
                "decision_motivation": "Clear reasoning for chosen path"
            },
            pacing_notes="Start internal, build through contemplation, end with resolve",
            dialogue_ratio="high",
            required_elements=["emotional truth", "genuine dilemma", "clear decision"],
            avoid_elements=["easy answers", "unmotivated choices", "passive acceptance"],
            example_openings=[
                "Marcus sat in his car, hands shaking as the reality sank in.",
                "The silence in Elena's apartment felt deafening after the day's chaos.",
                "Sarah stared at her phone, knowing she had to make the call."
            ],
            example_endings=[
                "She picked up her keys, knowing there was only one way forward.",
                "The decision made, Marcus felt both terrified and relieved.",
                "Elena closed her laptop. Tomorrow, she would tell them everything."
            ]
        )
    
    @staticmethod
    def get_action_sequence_template() -> SceneTemplate:
        """Template for action-heavy scenes"""
        return SceneTemplate(
            template_id="action_sequence_001",
            name="Action Sequence Scene",
            description="High-energy scene with physical conflict and immediate stakes",
            scene_type=SceneType.PROACTIVE,
            template_type=TemplateType.ACTION_SEQUENCE,
            opening_patterns=[
                "Immediate threat establishes urgency",
                "Character springs into action",
                "Confrontation begins without preamble",
                "Chase or pursuit commences"
            ],
            development_patterns=[
                "Action escalates in intensity",
                "Obstacles compound rapidly",
                "Character uses skills/resources",
                "Environment becomes factor"
            ],
            climax_patterns=[
                "Peak physical confrontation",
                "Moment requiring maximum effort",
                "Life-or-death decision point",
                "Ultimate test of character ability"
            ],
            resolution_patterns=[
                "Victory with unexpected cost",
                "Escape but situation worsened",
                "Defeat but knowledge gained",
                "Pyrrhic victory with new threats"
            ],
            proactive_structure={
                "goal_urgency": "Life-or-death stakes clearly established",
                "conflict_physicality": "Tangible, immediate obstacles",
                "setback_consequence": "Physical or strategic disadvantage"
            },
            pacing_notes="Fast-paced throughout, short sentences, immediate consequences",
            dialogue_ratio="low",
            required_elements=["physical stakes", "immediate danger", "character skill"],
            avoid_elements=["lengthy exposition", "internal monologue", "easy solutions"],
            genre_considerations={
                "thriller": "Focus on suspense and escalation",
                "fantasy": "Magic systems create unique solutions and problems",
                "science_fiction": "Technology shapes conflict parameters"
            },
            example_openings=[
                "The alarm screamed as Elena sprinted down the corridor.",
                "Marcus rolled behind the concrete barrier as bullets sparked overhead.",
                "Sarah's hands flew over the controls as the ship plummeted."
            ],
            example_endings=[
                "The explosion threw her clear, but the building was already collapsing.",
                "He reached safety, but the code was still in enemy hands.",
                "The ship stabilized, but they were now deep in hostile territory."
            ]
        )
    
    @staticmethod
    def get_dialogue_heavy_template() -> SceneTemplate:
        """Template for dialogue-focused scenes"""
        return SceneTemplate(
            template_id="dialogue_heavy_001",
            name="Dialogue-Heavy Scene",
            description="Scene built around conversation and character interaction",
            scene_type=SceneType.REACTIVE,
            template_type=TemplateType.DIALOGUE_HEAVY,
            opening_patterns=[
                "Characters meet in tense circumstances",
                "Important conversation begins immediately",
                "Confrontation about recent events",
                "Revelation prompts intense discussion"
            ],
            development_patterns=[
                "Subtext becomes increasingly important",
                "Characters reveal hidden motivations",
                "Conflict expressed through words",
                "Information revealed through interaction"
            ],
            climax_patterns=[
                "Truth finally spoken aloud",
                "Accusation or confession made",
                "Ultimatum delivered",
                "Relationship fundamentally changed"
            ],
            resolution_patterns=[
                "New understanding reached",
                "Alliance formed or broken",
                "Decision influenced by conversation",
                "Character sees situation differently"
            ],
            reactive_structure={
                "reaction_verbalization": "Feelings expressed through dialogue",
                "dilemma_exploration": "Options discussed with other characters",
                "decision_influence": "Conversation shapes final choice"
            },
            pacing_notes="Rhythm determined by speech patterns, use subtext heavily",
            dialogue_ratio="high",
            required_elements=["distinct voices", "subtext", "character revelation"],
            avoid_elements=["exposition dumps", "identical speech patterns", "pointless chatter"],
            example_openings=[
                "\"You lied to me,\" Sarah said, not looking up from her coffee.",
                "Marcus found Elena waiting in his office. \"We need to talk.\"",
                "\"I know what you did,\" the voice said from the shadows."
            ],
            example_endings=[
                "\"Then we understand each other,\" she said, and walked away.",
                "The silence stretched between them, saying everything words couldn't.",
                "\"I'll give you until midnight,\" he said. \"Then I make the call.\""
            ]
        )
    
    @staticmethod
    def get_introspective_template() -> SceneTemplate:
        """Template for internal/reflective scenes"""
        return SceneTemplate(
            template_id="introspective_001",
            name="Introspective Scene",
            description="Character-focused scene exploring internal conflict and growth",
            scene_type=SceneType.REACTIVE,
            template_type=TemplateType.INTROSPECTIVE,
            opening_patterns=[
                "Character alone with thoughts",
                "Quiet moment after intense events",
                "Character reviewing past decisions",
                "Solitary activity prompts reflection"
            ],
            development_patterns=[
                "Memories surface and connect",
                "Internal contradictions explored",
                "Values questioned and examined",
                "Growth through self-understanding"
            ],
            climax_patterns=[
                "Moment of self-recognition",
                "Acceptance of difficult truth",
                "Resolution of internal conflict",
                "Commitment to personal change"
            ],
            resolution_patterns=[
                "New self-awareness achieved",
                "Clearer purpose established",
                "Peace with difficult choice",
                "Readiness for next challenge"
            ],
            reactive_structure={
                "reaction_depth": "Full exploration of emotional impact",
                "dilemma_internal": "Character torn between personal values",
                "decision_growth": "Choice represents character development"
            },
            pacing_notes="Slower, contemplative pace with rich internal detail",
            dialogue_ratio="low",
            required_elements=["authentic emotion", "character insight", "internal logic"],
            avoid_elements=["self-pity", "circular thinking", "lack of resolution"],
            example_openings=[
                "Elena walked the empty beach, trying to make sense of everything.",
                "The photo in Marcus's hand showed a life that felt like someone else's.",
                "Sarah sat in the garden where her grandmother had taught her to be strong."
            ],
            example_endings=[
                "She knew now what she had to do, even if it meant losing everything.",
                "The past couldn't be changed, but the future was still his to write.",
                "For the first time in years, Elena felt truly free."
            ]
        )


class PromptLibrary:
    """Library of prompt templates for different generation scenarios"""
    
    @staticmethod
    def get_genre_specific_prompts() -> Dict[GenreTemplate, PromptTemplate]:
        """Get genre-specific prompt templates"""
        
        mystery_prompt = PromptTemplate(
            template_id="mystery_001",
            name="Mystery Scene Template",
            description="Template for mystery genre scenes",
            scene_type=SceneType.PROACTIVE,
            template_type=TemplateType.CONTINUATION,
            genre_affinity=[GenreTemplate.MYSTERY],
            system_prompt="""
You are writing a mystery scene. Focus on clues, red herrings, deduction, and maintaining suspense.
Every detail should either advance the investigation or mislead in purposeful ways.
""",
            structure_prompt="""
MYSTERY SCENE STRUCTURE:
- Goal: Uncover information, follow leads, or confront suspects
- Conflict: Missing clues, false information, uncooperative witnesses
- Setback: Discovery that complicates rather than solves the mystery

Maintain fairness to the reader - all clues must be available to them.
""",
            style_prompt="""
MYSTERY STYLE ELEMENTS:
- Precise observation of details
- Logical deduction process
- Atmospheric tension
- Red herrings that feel organic
- Clues that reward careful readers
""",
            ending_prompt="""
End with the character having new information but facing a deeper mystery.
The setback should make the case more complex, not simply block progress.
""",
            default_word_count=1200,
            complexity_level="complex",
            emotional_range=["curiosity", "frustration", "revelation", "concern"],
            typical_settings=["crime scene", "interrogation room", "suspect's home", "police station"]
        )
        
        romance_prompt = PromptTemplate(
            template_id="romance_001",
            name="Romance Scene Template",
            description="Template for romance genre scenes",
            scene_type=SceneType.REACTIVE,
            template_type=TemplateType.CONTINUATION,
            genre_affinity=[GenreTemplate.ROMANCE],
            system_prompt="""
You are writing a romance scene. Focus on emotional connection, relationship development, and romantic tension.
Characters should be vulnerable and authentic in their interactions.
""",
            structure_prompt="""
ROMANCE SCENE STRUCTURE:
- Reaction: Emotional response to romantic development
- Dilemma: Conflict between desire and obstacle (internal or external)
- Decision: Choice that affects romantic relationship

Focus on emotional truth and character growth through relationship.
""",
            style_prompt="""
ROMANCE STYLE ELEMENTS:
- Rich emotional interiority
- Meaningful dialogue and subtext
- Physical awareness and chemistry
- Relationship dynamics exploration
- Hope balanced with conflict
""",
            ending_prompt="""
End with a decision that moves the romantic relationship forward or creates new tension.
The choice should feel emotionally authentic and advance character development.
""",
            default_word_count=1000,
            complexity_level="medium",
            emotional_range=["attraction", "vulnerability", "hope", "fear", "joy"],
            typical_settings=["intimate spaces", "romantic locations", "shared activities", "conflict zones"]
        )
        
        fantasy_prompt = PromptTemplate(
            template_id="fantasy_001",
            name="Fantasy Scene Template", 
            description="Template for fantasy genre scenes",
            scene_type=SceneType.PROACTIVE,
            template_type=TemplateType.ACTION_SEQUENCE,
            genre_affinity=[GenreTemplate.FANTASY],
            system_prompt="""
You are writing a fantasy scene. Incorporate magic systems, fantastical elements, and world-building.
Magic should have consistent rules and meaningful costs or limitations.
""",
            structure_prompt="""
FANTASY SCENE STRUCTURE:
- Goal: Often involves magical solutions or supernatural challenges
- Conflict: Magic systems, mythical creatures, or otherworldly obstacles
- Setback: Magic fails, backfires, or reveals new supernatural threats

Ensure magical elements follow established rules and serve the story.
""",
            style_prompt="""
FANTASY STYLE ELEMENTS:
- Vivid fantastical imagery
- Magic system consistency
- World-building through details
- Mythic or epic tone where appropriate
- Balance of familiar and extraordinary
""",
            ending_prompt="""
End with magical consequences that create new story complications.
The setback should emerge from the fantasy elements in logical ways.
""",
            default_word_count=1500,
            complexity_level="complex",
            emotional_range=["wonder", "determination", "fear", "triumph", "loss"],
            typical_settings=["magical realms", "ancient ruins", "enchanted forests", "wizard towers"]
        )
        
        return {
            GenreTemplate.MYSTERY: mystery_prompt,
            GenreTemplate.ROMANCE: romance_prompt,
            GenreTemplate.FANTASY: fantasy_prompt
        }


class TemplateManager:
    """Manages scene and prompt templates for generation"""
    
    def __init__(self, template_directory: Optional[str] = None):
        self.template_directory = Path(template_directory) if template_directory else None
        self.scene_templates = {}
        self.prompt_templates = {}
        self.usage_statistics = {}
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Load custom templates if directory provided
        if self.template_directory and self.template_directory.exists():
            self._load_custom_templates()
    
    def _load_builtin_templates(self):
        """Load built-in scene and prompt templates"""
        
        # Load built-in scene templates
        builtin_scene_templates = [
            TemplateLibrary.get_proactive_opening_template(),
            TemplateLibrary.get_reactive_continuation_template(),
            TemplateLibrary.get_action_sequence_template(),
            TemplateLibrary.get_dialogue_heavy_template(),
            TemplateLibrary.get_introspective_template()
        ]
        
        for template in builtin_scene_templates:
            self.scene_templates[template.template_id] = template
        
        # Load built-in prompt templates
        genre_prompts = PromptLibrary.get_genre_specific_prompts()
        for genre, prompt_template in genre_prompts.items():
            self.prompt_templates[prompt_template.template_id] = prompt_template
    
    def _load_custom_templates(self):
        """Load custom templates from directory"""
        
        try:
            # Load scene templates
            scene_template_files = list(self.template_directory.glob("scene_templates/*.json"))
            for template_file in scene_template_files:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template = SceneTemplate(**template_data)
                    self.scene_templates[template.template_id] = template
            
            # Load prompt templates
            prompt_template_files = list(self.template_directory.glob("prompt_templates/*.json"))
            for template_file in prompt_template_files:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template = PromptTemplate(**template_data)
                    self.prompt_templates[template.template_id] = template
                    
        except Exception as e:
            print(f"Warning: Failed to load custom templates: {e}")
    
    def find_scene_template(self, scene_type: SceneType, 
                          template_type: Optional[TemplateType] = None,
                          genre: Optional[GenreTemplate] = None) -> List[SceneTemplate]:
        """Find scene templates matching criteria"""
        
        matching_templates = []
        
        for template in self.scene_templates.values():
            # Check scene type match
            if template.scene_type != scene_type:
                continue
            
            # Check template type match if specified
            if template_type and template.template_type != template_type:
                continue
            
            # Check genre consideration if specified
            if genre and genre.value not in template.genre_considerations:
                continue
            
            matching_templates.append(template)
        
        # Sort by usage count and rating
        matching_templates.sort(
            key=lambda t: (t.usage_count, t.average_rating),
            reverse=True
        )
        
        return matching_templates
    
    def find_prompt_template(self, scene_type: SceneType,
                           genre: Optional[GenreTemplate] = None,
                           template_type: Optional[TemplateType] = None) -> Optional[PromptTemplate]:
        """Find best matching prompt template"""
        
        matching_templates = []
        
        for template in self.prompt_templates.values():
            # Check scene type match
            if template.scene_type != scene_type:
                continue
            
            # Check genre affinity if specified
            if genre and genre not in template.genre_affinity:
                continue
            
            # Check template type match if specified
            if template_type and template.template_type != template_type:
                continue
            
            matching_templates.append(template)
        
        if not matching_templates:
            return None
        
        # Return most used and highest rated template
        return max(matching_templates, 
                  key=lambda t: (t.usage_count, t.average_rating))
    
    def get_template_by_id(self, template_id: str) -> Optional[Union[SceneTemplate, PromptTemplate]]:
        """Get specific template by ID"""
        
        if template_id in self.scene_templates:
            return self.scene_templates[template_id]
        elif template_id in self.prompt_templates:
            return self.prompt_templates[template_id]
        
        return None
    
    def create_composite_prompt(self, prompt_template: PromptTemplate,
                              scene_template: Optional[SceneTemplate] = None,
                              custom_instructions: Optional[str] = None) -> str:
        """Create composite prompt combining templates and custom instructions"""
        
        prompt_parts = []
        
        # Add system prompt
        prompt_parts.append(prompt_template.system_prompt)
        
        # Add structure guidance
        prompt_parts.append(prompt_template.structure_prompt)
        
        # Add scene template structure if available
        if scene_template:
            prompt_parts.append(f"\nSCENE TEMPLATE GUIDANCE:")
            prompt_parts.append(f"Template: {scene_template.name}")
            prompt_parts.append(f"Opening patterns: {', '.join(scene_template.opening_patterns[:3])}")
            
            if scene_template.proactive_structure and prompt_template.scene_type == SceneType.PROACTIVE:
                prompt_parts.append("Proactive structure requirements:")
                for key, value in scene_template.proactive_structure.items():
                    prompt_parts.append(f"- {key}: {value}")
            
            if scene_template.reactive_structure and prompt_template.scene_type == SceneType.REACTIVE:
                prompt_parts.append("Reactive structure requirements:")
                for key, value in scene_template.reactive_structure.items():
                    prompt_parts.append(f"- {key}: {value}")
            
            if scene_template.required_elements:
                prompt_parts.append(f"Required elements: {', '.join(scene_template.required_elements)}")
            
            if scene_template.avoid_elements:
                prompt_parts.append(f"Avoid these elements: {', '.join(scene_template.avoid_elements)}")
        
        # Add style guidance
        prompt_parts.append(prompt_template.style_prompt)
        
        # Add custom instructions
        if custom_instructions:
            prompt_parts.append(f"\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}")
        
        # Add ending guidance
        prompt_parts.append(prompt_template.ending_prompt)
        
        return "\n\n".join(prompt_parts)
    
    def record_template_usage(self, template_id: str, rating: Optional[float] = None):
        """Record template usage for statistics"""
        
        template = self.get_template_by_id(template_id)
        if not template:
            return
        
        # Update usage count
        template.usage_count += 1
        
        # Update rating if provided
        if rating is not None:
            current_total = template.average_rating * (template.usage_count - 1)
            template.average_rating = (current_total + rating) / template.usage_count
        
        # Record in statistics
        if template_id not in self.usage_statistics:
            self.usage_statistics[template_id] = {
                'usage_count': 0,
                'ratings': [],
                'last_used': None
            }
        
        stats = self.usage_statistics[template_id]
        stats['usage_count'] += 1
        stats['last_used'] = datetime.now()
        
        if rating is not None:
            stats['ratings'].append(rating)
    
    def get_template_recommendations(self, scene_type: SceneType,
                                   genre: Optional[GenreTemplate] = None,
                                   complexity: str = "medium") -> List[Tuple[str, float]]:
        """Get template recommendations with confidence scores"""
        
        recommendations = []
        
        # Find matching scene templates
        scene_templates = self.find_scene_template(scene_type, genre=genre)
        
        for template in scene_templates:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on usage
            if template.usage_count > 0:
                confidence += min(0.3, template.usage_count * 0.05)
            
            # Increase confidence based on rating
            if template.average_rating > 0:
                confidence += template.average_rating * 0.2
            
            # Adjust for complexity match
            if template.complexity_level == complexity:
                confidence += 0.1
            
            recommendations.append((template.template_id, min(1.0, confidence)))
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def export_templates(self, output_directory: str):
        """Export templates to files for backup or sharing"""
        
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export scene templates
        scene_dir = output_path / "scene_templates"
        scene_dir.mkdir(exist_ok=True)
        
        for template_id, template in self.scene_templates.items():
            template_file = scene_dir / f"{template_id}.json"
            with open(template_file, 'w') as f:
                json.dump(asdict(template), f, indent=2)
        
        # Export prompt templates  
        prompt_dir = output_path / "prompt_templates"
        prompt_dir.mkdir(exist_ok=True)
        
        for template_id, template in self.prompt_templates.items():
            template_file = prompt_dir / f"{template_id}.json"
            with open(template_file, 'w') as f:
                json.dump(asdict(template), f, indent=2)
        
        # Export usage statistics
        stats_file = output_path / "usage_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(self.usage_statistics, f, indent=2, default=str)
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get comprehensive template usage statistics"""
        
        total_scene_templates = len(self.scene_templates)
        total_prompt_templates = len(self.prompt_templates)
        
        most_used_scene = max(self.scene_templates.values(), 
                            key=lambda t: t.usage_count, default=None)
        most_used_prompt = max(self.prompt_templates.values(),
                             key=lambda t: t.usage_count, default=None)
        
        highest_rated_scene = max(self.scene_templates.values(),
                                key=lambda t: t.average_rating, default=None)
        highest_rated_prompt = max(self.prompt_templates.values(),
                                 key=lambda t: t.average_rating, default=None)
        
        return {
            'total_scene_templates': total_scene_templates,
            'total_prompt_templates': total_prompt_templates,
            'most_used_scene_template': most_used_scene.template_id if most_used_scene else None,
            'most_used_prompt_template': most_used_prompt.template_id if most_used_prompt else None,
            'highest_rated_scene_template': highest_rated_scene.template_id if highest_rated_scene else None,
            'highest_rated_prompt_template': highest_rated_prompt.template_id if highest_rated_prompt else None,
            'template_types_available': list(set(t.template_type.value for t in self.scene_templates.values())),
            'genres_supported': list(set(str(g) for t in self.prompt_templates.values() for g in t.genre_affinity))
        }