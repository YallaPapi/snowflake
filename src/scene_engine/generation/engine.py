"""
Scene Generation Engine

This implements subtask 44.1: Generation Engine
Core scene generation logic following Proactive/Reactive patterns with
AI model integration, content validation, and Snowflake Method compliance.
"""

import json
import re
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib

from ..models import (
    SceneCard, SceneType, ViewpointType, TenseType, 
    ProactiveScene, ReactiveScene
)
from ..validation.service import SceneValidationService, ValidationRequest


class GenerationMode(Enum):
    """Scene generation modes"""
    CREATIVE = "creative"
    STRUCTURED = "structured"
    ADAPTIVE = "adaptive"
    TEMPLATE_BASED = "template_based"


class AIModel(Enum):
    """Supported AI models for generation"""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GEMINI = "gemini"
    LOCAL = "local"


@dataclass
class GenerationContext:
    """Context information for scene generation"""
    project_title: str
    project_genre: str
    project_tone: Optional[str] = None
    target_audience: Optional[str] = None
    previous_scenes: List[Dict[str, Any]] = None
    character_profiles: List[Dict[str, Any]] = None
    story_outline: Optional[str] = None
    chapter_context: Optional[str] = None
    narrative_arc_position: Optional[str] = None  # beginning, middle, climax, resolution
    
    def __post_init__(self):
        if self.previous_scenes is None:
            self.previous_scenes = []
        if self.character_profiles is None:
            self.character_profiles = []


@dataclass
class GenerationRequest:
    """Request for scene generation"""
    scene_type: SceneType
    pov_character: str
    scene_purpose: str  # What this scene accomplishes in the story
    context: GenerationContext
    
    # Scene-specific requirements
    required_elements: List[str] = None  # Must include these story elements
    emotional_tone: Optional[str] = None  # happy, tense, mysterious, etc.
    setting_location: Optional[str] = None
    setting_time: Optional[str] = None
    word_count_target: int = 1000
    
    # Generation parameters
    generation_mode: GenerationMode = GenerationMode.STRUCTURED
    creativity_level: float = 0.7  # 0.0 to 1.0
    use_templates: bool = True
    
    # Chain link information (if continuing from previous scene)
    previous_scene_ending: Optional[str] = None
    chain_transition_type: Optional[str] = None
    
    def __post_init__(self):
        if self.required_elements is None:
            self.required_elements = []


@dataclass
class GenerationResponse:
    """Response from scene generation"""
    success: bool
    scene_card: Optional[SceneCard] = None
    prose_content: Optional[str] = None
    
    # Generation metadata
    generation_id: str = ""
    model_used: str = ""
    generation_time_seconds: float = 0.0
    word_count: int = 0
    
    # Quality metrics
    snowflake_compliance_score: float = 0.0
    narrative_coherence_score: float = 0.0
    character_consistency_score: float = 0.0
    
    # Validation results
    validation_passed: bool = False
    validation_errors: List[str] = None
    validation_warnings: List[str] = None
    
    # Generation process info
    template_used: Optional[str] = None
    refinement_passes: int = 0
    alternatives_generated: int = 1
    
    # Error information
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []
        if self.validation_warnings is None:
            self.validation_warnings = []
        if self.error_details is None:
            self.error_details = {}
        if not self.generation_id:
            self.generation_id = f"gen_{int(datetime.utcnow().timestamp())}_{hash(str(self))}"


class GenerationError(Exception):
    """Base exception for generation errors"""
    pass


class ModelIntegrationError(GenerationError):
    """Error in AI model integration"""
    pass


class TemplateError(GenerationError):
    """Error in template processing"""
    pass


class ValidationFailureError(GenerationError):
    """Error when generated content fails validation"""
    pass


class AIModelInterface:
    """Interface for AI model integration"""
    
    def __init__(self, model_type: AIModel, api_key: Optional[str] = None, 
                 endpoint: Optional[str] = None):
        self.model_type = model_type
        self.api_key = api_key
        self.endpoint = endpoint
        self.model_config = self._get_model_config()
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration"""
        configs = {
            AIModel.CLAUDE: {
                "max_tokens": 4000,
                "temperature": 0.7,
                "model": "claude-3-sonnet-20240229"
            },
            AIModel.GPT4: {
                "max_tokens": 4000,
                "temperature": 0.7,
                "model": "gpt-4"
            },
            AIModel.GEMINI: {
                "max_tokens": 4000,
                "temperature": 0.7,
                "model": "gemini-pro"
            },
            AIModel.LOCAL: {
                "max_tokens": 4000,
                "temperature": 0.7,
                "model": "local-model"
            }
        }
        return configs.get(self.model_type, configs[AIModel.CLAUDE])
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the AI model"""
        # This is a placeholder - actual implementation would depend on specific model APIs
        if self.model_type == AIModel.CLAUDE:
            return await self._generate_claude(prompt, **kwargs)
        elif self.model_type == AIModel.GPT4:
            return await self._generate_gpt4(prompt, **kwargs)
        elif self.model_type == AIModel.GEMINI:
            return await self._generate_gemini(prompt, **kwargs)
        else:
            return await self._generate_local(prompt, **kwargs)
    
    async def _generate_claude(self, prompt: str, **kwargs) -> str:
        """Generate content using Claude API (placeholder)"""
        # Placeholder implementation - would use actual Claude API
        return f"[Generated by Claude] {prompt[:100]}..."
    
    async def _generate_gpt4(self, prompt: str, **kwargs) -> str:
        """Generate content using GPT-4 API (placeholder)"""
        # Placeholder implementation - would use actual OpenAI API
        return f"[Generated by GPT-4] {prompt[:100]}..."
    
    async def _generate_gemini(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini API (placeholder)"""
        # Placeholder implementation - would use actual Gemini API
        return f"[Generated by Gemini] {prompt[:100]}..."
    
    async def _generate_local(self, prompt: str, **kwargs) -> str:
        """Generate content using local model (placeholder)"""
        # Placeholder implementation - would use local model
        return f"[Generated by Local Model] {prompt[:100]}..."


class PromptBuilder:
    """Builds generation prompts following Snowflake Method principles"""
    
    @staticmethod
    def build_scene_generation_prompt(request: GenerationRequest) -> str:
        """Build comprehensive scene generation prompt"""
        
        prompt_parts = []
        
        # System instructions
        prompt_parts.append("""
You are a professional novelist's assistant specializing in the Snowflake Method. Generate a scene that strictly follows Snowflake Method principles for scene structure and character development.

CRITICAL REQUIREMENTS:
- Follow Randy Ingermanson's Proactive/Reactive scene patterns exactly
- Proactive scenes must have Goal-Conflict-Setback (G-C-S) structure
- Reactive scenes must have Reaction-Dilemma-Decision (R-D-D) structure
- Maintain viewpoint discipline (stay in chosen POV throughout)
- Ensure scene crucible creates meaningful conflict
- Advance the story and develop character
""")
        
        # Scene type specific instructions
        if request.scene_type == SceneType.PROACTIVE:
            prompt_parts.append("""
PROACTIVE SCENE STRUCTURE:
1. GOAL: What does the POV character want in this scene? Must be specific and time-bound.
2. CONFLICT: What prevents the character from achieving the goal? Must be credible opposition.
3. SETBACK: How does the conflict result in failure or partial failure? Must increase stakes.

The scene should end with the character worse off than when they started, creating the need for a Reactive scene.
""")
        else:
            prompt_parts.append("""
REACTIVE SCENE STRUCTURE:
1. REACTION: How does the POV character emotionally respond to the previous setback?
2. DILEMMA: What difficult choice must the character make? Present clear options with trade-offs.
3. DECISION: What does the character decide to do? This becomes the goal for the next Proactive scene.

The scene should end with a clear decision that launches the next scene's action.
""")
        
        # Context information
        prompt_parts.append(f"""
STORY CONTEXT:
- Project: {request.context.project_title} ({request.context.project_genre})
- POV Character: {request.pov_character}
- Scene Purpose: {request.scene_purpose}
- Target Word Count: {request.word_count_target}
""")
        
        if request.context.project_tone:
            prompt_parts.append(f"- Project Tone: {request.context.project_tone}")
        
        if request.emotional_tone:
            prompt_parts.append(f"- Scene Emotional Tone: {request.emotional_tone}")
        
        if request.setting_location:
            prompt_parts.append(f"- Location: {request.setting_location}")
        
        if request.setting_time:
            prompt_parts.append(f"- Time: {request.setting_time}")
        
        # Character context
        if request.context.character_profiles:
            prompt_parts.append("\nCHARACTER PROFILES:")
            for char in request.context.character_profiles:
                prompt_parts.append(f"- {char.get('name', 'Unknown')}: {char.get('description', 'No description')}")
                if char.get('goals'):
                    prompt_parts.append(f"  Goals: {', '.join(char['goals'])}")
                if char.get('conflicts'):
                    prompt_parts.append(f"  Conflicts: {', '.join(char['conflicts'])}")
        
        # Previous scene context
        if request.previous_scene_ending:
            prompt_parts.append(f"\nPREVIOUS SCENE ENDING: {request.previous_scene_ending}")
        
        if request.context.previous_scenes:
            prompt_parts.append("\nRECENT SCENES SUMMARY:")
            for i, scene in enumerate(request.context.previous_scenes[-3:]):  # Last 3 scenes
                prompt_parts.append(f"{i+1}. {scene.get('summary', 'No summary')}")
        
        # Story requirements
        if request.required_elements:
            prompt_parts.append(f"\nREQUIRED STORY ELEMENTS: {', '.join(request.required_elements)}")
        
        if request.context.story_outline:
            prompt_parts.append(f"\nSTORY OUTLINE CONTEXT: {request.context.story_outline}")
        
        # Generation instructions
        prompt_parts.append(f"""
GENERATION REQUIREMENTS:
1. Write a complete scene of approximately {request.word_count_target} words
2. Maintain {request.pov_character}'s viewpoint throughout (third person limited recommended)
3. Use past tense unless specifically requested otherwise
4. Include sensory details and emotional depth
5. Ensure dialogue serves story purpose and reveals character
6. End with clear transition setup for next scene

OUTPUT FORMAT:
Provide your response as a JSON object with these fields:
{{
    "scene_crucible": "One sentence describing the core conflict/situation",
    "place": "Physical location of the scene",
    "time": "When the scene takes place",
    "proactive_data": {{  // Only for Proactive scenes
        "goal": "Specific, time-bound goal",
        "conflict": "What opposes the goal",
        "setback": "How the goal fails or partially fails"
    }},
    "reactive_data": {{  // Only for Reactive scenes
        "reaction": "Emotional response to previous setback",
        "dilemma": "The difficult choice facing the character",
        "decision": "What the character decides to do"
    }},
    "prose_content": "The complete scene prose",
    "exposition_used": ["list", "of", "exposition", "elements", "revealed"],
    "chain_link": "How this scene connects to the story flow"
}}

Generate the scene now:
""")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_refinement_prompt(original_content: str, refinement_goals: List[str]) -> str:
        """Build prompt for content refinement"""
        
        prompt = f"""
You are refining a scene for a novel following the Snowflake Method. Improve the following content based on these specific goals:

REFINEMENT GOALS:
{chr(10).join([f"- {goal}" for goal in refinement_goals])}

ORIGINAL CONTENT:
{original_content}

REFINEMENT INSTRUCTIONS:
1. Maintain the core story structure and character viewpoint
2. Preserve the scene's G-C-S or R-D-D pattern
3. Enhance prose quality without changing fundamental plot points
4. Improve pacing, dialogue, and sensory details
5. Ensure consistency with Snowflake Method principles

Provide the refined content maintaining the same JSON structure as the original.
"""
        
        return prompt


class SceneGenerationEngine:
    """Core engine for AI-powered scene generation"""
    
    def __init__(self, model_interface: Optional[AIModelInterface] = None,
                 validation_service: Optional[SceneValidationService] = None):
        self.model_interface = model_interface or AIModelInterface(AIModel.CLAUDE)
        self.validation_service = validation_service or SceneValidationService()
        self.prompt_builder = PromptBuilder()
        self.generation_history = []
        
    async def generate_scene(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a scene based on the request"""
        
        start_time = datetime.utcnow()
        generation_id = f"gen_{int(start_time.timestamp())}_{hash(str(request))}"
        
        try:
            # Build generation prompt
            prompt = self.prompt_builder.build_scene_generation_prompt(request)
            
            # Generate content using AI model
            raw_content = await self.model_interface.generate_content(
                prompt=prompt,
                temperature=request.creativity_level,
                max_tokens=request.word_count_target * 2  # Allow some buffer
            )
            
            # Parse generated content
            scene_card, prose_content = self._parse_generated_content(
                raw_content, request.scene_type
            )
            
            # Validate generated scene
            validation_result = self._validate_generated_scene(scene_card, request)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(
                scene_card, prose_content, request
            )
            
            # Create response
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = GenerationResponse(
                success=True,
                scene_card=scene_card,
                prose_content=prose_content,
                generation_id=generation_id,
                model_used=self.model_interface.model_type.value,
                generation_time_seconds=generation_time,
                word_count=len(prose_content.split()) if prose_content else 0,
                snowflake_compliance_score=quality_metrics['snowflake_compliance'],
                narrative_coherence_score=quality_metrics['narrative_coherence'],
                character_consistency_score=quality_metrics['character_consistency'],
                validation_passed=validation_result['passed'],
                validation_errors=validation_result['errors'],
                validation_warnings=validation_result['warnings']
            )
            
            # Store in generation history
            self.generation_history.append({
                'request': request,
                'response': response,
                'timestamp': start_time
            })
            
            return response
            
        except Exception as e:
            # Handle generation errors
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            return GenerationResponse(
                success=False,
                generation_id=generation_id,
                model_used=self.model_interface.model_type.value,
                generation_time_seconds=generation_time,
                error_message=str(e),
                error_details={'exception_type': type(e).__name__}
            )
    
    def _parse_generated_content(self, raw_content: str, 
                               scene_type: SceneType) -> Tuple[SceneCard, str]:
        """Parse AI-generated content into SceneCard and prose"""
        
        try:
            # Extract JSON from response (handle cases where model adds extra text)
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                # Fallback: assume entire content is JSON
                json_str = raw_content
            
            # Parse JSON
            content_data = json.loads(json_str)
            
            # Extract basic scene information
            scene_data = {
                'scene_type': scene_type,
                'pov': content_data.get('pov', 'Unknown'),
                'viewpoint': ViewpointType.THIRD,  # Default
                'tense': TenseType.PAST,  # Default
                'scene_crucible': content_data.get('scene_crucible', ''),
                'place': content_data.get('place', ''),
                'time': content_data.get('time', ''),
                'exposition_used': content_data.get('exposition_used', []),
                'chain_link': content_data.get('chain_link', '')
            }
            
            # Add scene-specific structure
            if scene_type == SceneType.PROACTIVE and 'proactive_data' in content_data:
                proactive_data = content_data['proactive_data']
                scene_data['proactive'] = ProactiveScene(
                    goal=proactive_data.get('goal', ''),
                    conflict=proactive_data.get('conflict', ''),
                    setback=proactive_data.get('setback', '')
                )
            elif scene_type == SceneType.REACTIVE and 'reactive_data' in content_data:
                reactive_data = content_data['reactive_data']
                scene_data['reactive'] = ReactiveScene(
                    reaction=reactive_data.get('reaction', ''),
                    dilemma=reactive_data.get('dilemma', ''),
                    decision=reactive_data.get('decision', '')
                )
            
            # Create scene card
            scene_card = SceneCard(**scene_data)
            prose_content = content_data.get('prose_content', '')
            
            return scene_card, prose_content
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise GenerationError(f"Failed to parse generated content: {str(e)}")
    
    def _validate_generated_scene(self, scene_card: SceneCard, 
                                request: GenerationRequest) -> Dict[str, Any]:
        """Validate the generated scene using validation service"""
        
        try:
            validation_request = ValidationRequest(
                scene_card=scene_card,
                context={
                    'project_context': {
                        'genre': request.context.project_genre,
                        'tone': request.context.project_tone
                    },
                    'character_profiles': request.context.character_profiles
                }
            )
            
            validation_result = self.validation_service.validate_scene_card(validation_request)
            
            return {
                'passed': validation_result.is_valid,
                'errors': validation_result.errors,
                'warnings': validation_result.warnings
            }
            
        except Exception:
            # If validation fails, return basic validation
            return {
                'passed': len(scene_card.scene_crucible) > 10,  # Basic check
                'errors': [],
                'warnings': ['Validation service unavailable']
            }
    
    def _calculate_quality_metrics(self, scene_card: SceneCard, prose_content: str,
                                 request: GenerationRequest) -> Dict[str, float]:
        """Calculate quality metrics for generated content"""
        
        metrics = {
            'snowflake_compliance': 0.0,
            'narrative_coherence': 0.0,
            'character_consistency': 0.0
        }
        
        # Snowflake compliance scoring
        compliance_score = 0.0
        
        if scene_card.scene_crucible and len(scene_card.scene_crucible) > 20:
            compliance_score += 0.2
        
        if scene_card.scene_type == SceneType.PROACTIVE and scene_card.proactive:
            if (scene_card.proactive.goal and scene_card.proactive.conflict 
                and scene_card.proactive.setback):
                compliance_score += 0.4
        elif scene_card.scene_type == SceneType.REACTIVE and scene_card.reactive:
            if (scene_card.reactive.reaction and scene_card.reactive.dilemma 
                and scene_card.reactive.decision):
                compliance_score += 0.4
        
        if scene_card.pov and len(scene_card.pov) > 0:
            compliance_score += 0.2
        
        if prose_content and len(prose_content.split()) >= request.word_count_target * 0.8:
            compliance_score += 0.2
        
        metrics['snowflake_compliance'] = min(1.0, compliance_score)
        
        # Narrative coherence (basic heuristics)
        coherence_score = 0.5  # Default middle score
        
        if prose_content:
            # Check for narrative flow indicators
            if any(word in prose_content.lower() for word in 
                   ['then', 'next', 'after', 'before', 'when', 'while']):
                coherence_score += 0.2
            
            # Check for dialogue presence (indicates character interaction)
            if '"' in prose_content or "'" in prose_content:
                coherence_score += 0.1
            
            # Check for sensory details
            sensory_words = ['saw', 'heard', 'felt', 'smelled', 'tasted', 'touched']
            if any(word in prose_content.lower() for word in sensory_words):
                coherence_score += 0.2
        
        metrics['narrative_coherence'] = min(1.0, coherence_score)
        
        # Character consistency (check if POV character appears in prose)
        consistency_score = 0.5  # Default
        
        if prose_content and request.pov_character.lower() in prose_content.lower():
            consistency_score += 0.3
        
        if scene_card.pov == request.pov_character:
            consistency_score += 0.2
        
        metrics['character_consistency'] = min(1.0, consistency_score)
        
        return metrics
    
    async def refine_scene(self, scene_card: SceneCard, prose_content: str,
                         refinement_goals: List[str]) -> Tuple[SceneCard, str]:
        """Refine existing scene content"""
        
        # Create refinement prompt
        original_content = json.dumps({
            'scene_crucible': scene_card.scene_crucible,
            'place': scene_card.place,
            'time': scene_card.time,
            'proactive_data': scene_card.proactive.dict() if scene_card.proactive else None,
            'reactive_data': scene_card.reactive.dict() if scene_card.reactive else None,
            'prose_content': prose_content,
            'exposition_used': scene_card.exposition_used,
            'chain_link': scene_card.chain_link
        }, indent=2)
        
        refinement_prompt = self.prompt_builder.build_refinement_prompt(
            original_content, refinement_goals
        )
        
        # Generate refined content
        refined_raw = await self.model_interface.generate_content(refinement_prompt)
        
        # Parse refined content
        refined_scene_card, refined_prose = self._parse_generated_content(
            refined_raw, scene_card.scene_type
        )
        
        return refined_scene_card, refined_prose
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about generation performance"""
        
        if not self.generation_history:
            return {'total_generations': 0}
        
        successful_generations = [g for g in self.generation_history 
                                if g['response'].success]
        
        total_time = sum(g['response'].generation_time_seconds 
                        for g in self.generation_history)
        avg_time = total_time / len(self.generation_history)
        
        avg_quality = sum(g['response'].snowflake_compliance_score 
                         for g in successful_generations) / len(successful_generations) if successful_generations else 0
        
        return {
            'total_generations': len(self.generation_history),
            'successful_generations': len(successful_generations),
            'success_rate': len(successful_generations) / len(self.generation_history),
            'average_generation_time': avg_time,
            'average_quality_score': avg_quality,
            'models_used': list(set(g['response'].model_used for g in self.generation_history))
        }