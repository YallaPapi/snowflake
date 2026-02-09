"""
Scene Generation Service Integration Layer

This implements subtask 44.4: Integration Layer
High-level service that connects generation engine, templates, refinement,
persistence, and validation systems for complete scene generation workflow.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .engine import (
    SceneGenerationEngine, GenerationRequest, GenerationResponse, 
    GenerationContext, AIModelInterface, AIModel
)
from .templates import TemplateManager, TemplateType, GenreTemplate
from .refinement import ContentRefiner, RefinementType, RefinementReport
from ..models import SceneCard, SceneType, ViewpointType, TenseType
from ..validation.service import SceneValidationService
from ..persistence.service import PersistenceService
from ..chaining.generator import ChainLinkGenerator


@dataclass
class GenerationWorkflowRequest:
    """Request for complete generation workflow"""
    # Project context
    project_id: int
    project_title: str
    project_genre: str
    
    # Scene specification
    scene_type: SceneType
    pov_character: str
    scene_purpose: str
    
    # Optional parameters
    template_preferences: Optional[List[TemplateType]] = None
    generation_settings: Optional[Dict[str, Any]] = None
    refinement_goals: Optional[List[RefinementType]] = None
    auto_save: bool = True
    validate_before_save: bool = True
    
    # Chain linking
    link_to_previous_scene: bool = False
    previous_scene_id: Optional[str] = None
    
    def __post_init__(self):
        if self.template_preferences is None:
            self.template_preferences = []
        if self.generation_settings is None:
            self.generation_settings = {}
        if self.refinement_goals is None:
            self.refinement_goals = []


@dataclass
class GenerationWorkflowResponse:
    """Response from complete generation workflow"""
    success: bool
    workflow_id: str
    
    # Generated content
    scene_card: Optional[SceneCard] = None
    prose_content: Optional[str] = None
    
    # Processing results
    generation_response: Optional[GenerationResponse] = None
    refinement_report: Optional[RefinementReport] = None
    validation_passed: bool = False
    
    # Persistence results
    saved_to_database: bool = False
    scene_database_id: Optional[int] = None
    
    # Chain linking results
    chain_link_created: bool = False
    chain_link_id: Optional[str] = None
    
    # Workflow statistics
    total_processing_time: float = 0.0
    steps_completed: List[str] = None
    steps_failed: List[str] = None
    
    # Error information
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []
        if self.steps_failed is None:
            self.steps_failed = []
        if self.error_details is None:
            self.error_details = {}


class SceneGenerationService:
    """High-level service for complete scene generation workflow"""
    
    def __init__(self, 
                 persistence_service: Optional[PersistenceService] = None,
                 validation_service: Optional[SceneValidationService] = None,
                 template_manager: Optional[TemplateManager] = None,
                 ai_model_interface: Optional[AIModelInterface] = None,
                 template_directory: Optional[str] = None):
        
        # Initialize core services
        self.persistence_service = persistence_service or PersistenceService()
        self.validation_service = validation_service or SceneValidationService()
        self.template_manager = template_manager or TemplateManager(template_directory)
        
        # Initialize AI model interface
        self.ai_model = ai_model_interface or AIModelInterface(AIModel.CLAUDE)
        
        # Initialize generation components
        self.generation_engine = SceneGenerationEngine(
            model_interface=self.ai_model,
            validation_service=self.validation_service
        )
        
        self.content_refiner = ContentRefiner()
        self.chain_generator = ChainLinkGenerator()
        
        # Workflow tracking
        self.active_workflows = {}
        self.workflow_history = []
        
    async def generate_scene_complete(self, request: GenerationWorkflowRequest) -> GenerationWorkflowResponse:
        """Execute complete scene generation workflow"""
        
        workflow_id = f"workflow_{int(datetime.utcnow().timestamp())}"
        start_time = datetime.utcnow()
        
        response = GenerationWorkflowResponse(
            success=False,
            workflow_id=workflow_id
        )
        
        # Track workflow
        self.active_workflows[workflow_id] = {
            'request': request,
            'start_time': start_time,
            'status': 'running'
        }
        
        try:
            # Step 1: Prepare generation context
            response.steps_completed.append("context_preparation")
            generation_context = await self._prepare_generation_context(request)
            
            # Step 2: Select templates
            response.steps_completed.append("template_selection")
            scene_template, prompt_template = self._select_templates(request)
            
            # Step 3: Generate scene
            response.steps_completed.append("scene_generation")
            generation_request = self._build_generation_request(
                request, generation_context, scene_template, prompt_template
            )
            
            generation_response = await self.generation_engine.generate_scene(generation_request)
            response.generation_response = generation_response
            
            if not generation_response.success:
                raise Exception(f"Scene generation failed: {generation_response.error_message}")
            
            # Step 4: Refine content (if requested)
            if request.refinement_goals:
                response.steps_completed.append("content_refinement")
                scene_card, prose_content, refinement_report = self.content_refiner.refine_scene_content(
                    generation_response.scene_card,
                    generation_response.prose_content,
                    request.refinement_goals
                )
                response.refinement_report = refinement_report
            else:
                scene_card = generation_response.scene_card
                prose_content = generation_response.prose_content
            
            # Step 5: Validate (if requested)
            if request.validate_before_save:
                response.steps_completed.append("validation")
                validation_result = self._validate_generated_content(scene_card, request)
                response.validation_passed = validation_result['passed']
                
                if not response.validation_passed and validation_result['critical_errors']:
                    # Attempt auto-fix for critical validation errors
                    scene_card, prose_content = await self._auto_fix_validation_errors(
                        scene_card, prose_content, validation_result['errors']
                    )
                    
                    # Re-validate after fixes
                    validation_result = self._validate_generated_content(scene_card, request)
                    response.validation_passed = validation_result['passed']
            else:
                response.validation_passed = True
            
            # Step 6: Save to database (if requested and validation passed)
            if request.auto_save and response.validation_passed:
                response.steps_completed.append("database_save")
                db_scene_card, prose_obj = self.persistence_service.create_scene_card_with_prose(
                    project_id=request.project_id,
                    scene_card=scene_card,
                    prose_content=prose_content,
                    prose_notes=f"Generated scene - Workflow {workflow_id}"
                )
                response.saved_to_database = True
                response.scene_database_id = db_scene_card.id
            
            # Step 7: Create chain link (if requested)
            if request.link_to_previous_scene and request.previous_scene_id:
                response.steps_completed.append("chain_linking")
                chain_link_result = await self._create_chain_link(
                    request, scene_card, db_scene_card.scene_id if response.saved_to_database else None
                )
                response.chain_link_created = chain_link_result['success']
                response.chain_link_id = chain_link_result.get('chain_id')
            
            # Set final response data
            response.success = True
            response.scene_card = scene_card
            response.prose_content = prose_content
            
        except Exception as e:
            # Handle workflow errors
            response.error_message = str(e)
            response.error_details = {'exception_type': type(e).__name__}
            
            # Add failed step
            current_step = self._get_current_step(response.steps_completed)
            if current_step:
                response.steps_failed.append(current_step)
        
        finally:
            # Calculate total processing time
            end_time = datetime.utcnow()
            response.total_processing_time = (end_time - start_time).total_seconds()
            
            # Update workflow tracking
            self.active_workflows[workflow_id]['status'] = 'completed' if response.success else 'failed'
            self.active_workflows[workflow_id]['end_time'] = end_time
            
            # Move to history
            self.workflow_history.append(self.active_workflows[workflow_id])
            del self.active_workflows[workflow_id]
        
        return response
    
    async def _prepare_generation_context(self, request: GenerationWorkflowRequest) -> GenerationContext:
        """Prepare context information for generation"""
        
        # Get project information
        project_summary = self.persistence_service.get_project_summary(request.project_id)
        project_info = project_summary['project']
        
        # Get recent scenes for context
        recent_scenes = self.persistence_service.crud['scene_cards'].get_scene_cards(
            project_id=request.project_id,
            limit=5
        )
        
        previous_scenes = []
        for scene in recent_scenes:
            scene_summary = {
                'scene_id': scene.scene_id,
                'scene_type': scene.scene_type.value,
                'pov': scene.pov,
                'summary': scene.scene_crucible,
                'place': scene.place,
                'time': scene.time
            }
            previous_scenes.append(scene_summary)
        
        # Get character profiles
        characters = self.persistence_service.crud['characters'].get_characters(request.project_id)
        character_profiles = []
        
        for character in characters:
            profile = {
                'name': character.name,
                'role': character.role,
                'description': character.description,
                'goals': character.goals or [],
                'conflicts': character.conflicts or []
            }
            character_profiles.append(profile)
        
        return GenerationContext(
            project_title=project_info['title'],
            project_genre=project_info.get('genre', request.project_genre),
            project_tone=None,  # Could be extracted from project settings
            target_audience=None,  # Could be extracted from project settings
            previous_scenes=previous_scenes,
            character_profiles=character_profiles
        )
    
    def _select_templates(self, request: GenerationWorkflowRequest) -> Tuple[Optional[object], Optional[object]]:
        """Select appropriate templates for generation"""
        
        # Determine genre template
        genre_mapping = {
            'mystery': GenreTemplate.MYSTERY,
            'romance': GenreTemplate.ROMANCE,
            'fantasy': GenreTemplate.FANTASY,
            'science fiction': GenreTemplate.SCIENCE_FICTION,
            'thriller': GenreTemplate.THRILLER,
            'horror': GenreTemplate.HORROR
        }
        
        genre_template = genre_mapping.get(request.project_genre.lower())
        
        # Find scene template
        scene_templates = self.template_manager.find_scene_template(
            scene_type=request.scene_type,
            template_type=request.template_preferences[0] if request.template_preferences else None,
            genre=genre_template
        )
        
        scene_template = scene_templates[0] if scene_templates else None
        
        # Find prompt template
        prompt_template = self.template_manager.find_prompt_template(
            scene_type=request.scene_type,
            genre=genre_template,
            template_type=request.template_preferences[0] if request.template_preferences else None
        )
        
        # Record template usage
        if scene_template:
            self.template_manager.record_template_usage(scene_template.template_id)
        if prompt_template:
            self.template_manager.record_template_usage(prompt_template.template_id)
        
        return scene_template, prompt_template
    
    def _build_generation_request(self, workflow_request: GenerationWorkflowRequest,
                                context: GenerationContext, 
                                scene_template: Optional[object],
                                prompt_template: Optional[object]) -> GenerationRequest:
        """Build generation request from workflow parameters"""
        
        # Extract generation settings
        settings = workflow_request.generation_settings
        
        generation_request = GenerationRequest(
            scene_type=workflow_request.scene_type,
            pov_character=workflow_request.pov_character,
            scene_purpose=workflow_request.scene_purpose,
            context=context,
            
            # Optional parameters from settings
            emotional_tone=settings.get('emotional_tone'),
            setting_location=settings.get('location'),
            setting_time=settings.get('time'),
            word_count_target=settings.get('word_count', 1000),
            
            # Generation parameters
            creativity_level=settings.get('creativity', 0.7),
            use_templates=scene_template is not None,
            
            # Chain linking context
            previous_scene_ending=settings.get('previous_ending'),
            chain_transition_type=settings.get('transition_type')
        )
        
        return generation_request
    
    def _validate_generated_content(self, scene_card: SceneCard, 
                                  request: GenerationWorkflowRequest) -> Dict[str, Any]:
        """Validate generated content"""
        
        from ..validation.service import ValidationRequest
        
        validation_request = ValidationRequest(
            scene_card=scene_card,
            context={
                'project_context': {
                    'genre': request.project_genre,
                    'title': request.project_title
                }
            }
        )
        
        validation_result = self.validation_service.validate_scene_card(validation_request)
        
        # Categorize errors by severity
        critical_errors = [error for error in validation_result.errors 
                         if 'critical' in error.lower() or 'missing' in error.lower()]
        
        return {
            'passed': validation_result.is_valid,
            'errors': validation_result.errors,
            'warnings': validation_result.warnings,
            'critical_errors': critical_errors
        }
    
    async def _auto_fix_validation_errors(self, scene_card: SceneCard, prose_content: str,
                                        errors: List[str]) -> Tuple[SceneCard, str]:
        """Attempt to automatically fix validation errors"""
        
        # This is a simplified auto-fix - would use AI models for more sophisticated fixes
        
        for error in errors:
            if 'scene crucible' in error.lower() and len(scene_card.scene_crucible) < 20:
                # Generate a basic scene crucible from the prose content
                first_sentence = prose_content.split('.')[0] if '.' in prose_content else prose_content[:100]
                scene_card.scene_crucible = f"Scene focusing on {scene_card.pov}: {first_sentence}"
            
            elif 'goal' in error.lower() and scene_card.proactive and not scene_card.proactive.goal:
                # Set a basic goal
                scene_card.proactive.goal = f"{scene_card.pov} seeks to accomplish their objective"
            
            elif 'conflict' in error.lower() and scene_card.proactive and not scene_card.proactive.conflict:
                # Set a basic conflict
                scene_card.proactive.conflict = f"Obstacles prevent {scene_card.pov} from succeeding"
        
        return scene_card, prose_content
    
    async def _create_chain_link(self, request: GenerationWorkflowRequest,
                               scene_card: SceneCard, current_scene_id: Optional[str]) -> Dict[str, Any]:
        """Create chain link to previous scene"""
        
        if not request.previous_scene_id or not current_scene_id:
            return {'success': False, 'error': 'Missing scene IDs for chain linking'}
        
        try:
            # Get previous scene
            previous_scene = self.persistence_service.crud['scene_cards'].get_scene_card(
                request.previous_scene_id, request.project_id
            )
            
            if not previous_scene:
                return {'success': False, 'error': 'Previous scene not found'}
            
            # Create chain link using chain generator
            from ..chaining.models import SceneReference
            
            source_scene = SceneReference(
                scene_id=previous_scene.scene_id,
                scene_type=SceneType(previous_scene.scene_type.value),
                pov_character=previous_scene.pov
            )
            
            target_scene = SceneReference(
                scene_id=current_scene_id,
                scene_type=scene_card.scene_type,
                pov_character=scene_card.pov
            )
            
            # Generate chain link
            chain_link = self.chain_generator.generate_chain_link(
                source_scene=source_scene,
                target_scene=target_scene,
                story_context={'project_title': request.project_title}
            )
            
            # Save chain link
            self.persistence_service.crud['chain_links'].create_chain_link(
                request.project_id, chain_link
            )
            
            return {'success': True, 'chain_id': chain_link.chain_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_current_step(self, completed_steps: List[str]) -> Optional[str]:
        """Get current step being processed"""
        
        all_steps = [
            "context_preparation", "template_selection", "scene_generation",
            "content_refinement", "validation", "database_save", "chain_linking"
        ]
        
        for step in all_steps:
            if step not in completed_steps:
                return step
        
        return None
    
    def generate_scene_batch(self, requests: List[GenerationWorkflowRequest]) -> List[GenerationWorkflowResponse]:
        """Generate multiple scenes in batch"""
        
        async def process_batch():
            tasks = [self.generate_scene_complete(request) for request in requests]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        # Run batch processing
        results = asyncio.run(process_batch())
        
        # Handle any exceptions
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error response
                error_response = GenerationWorkflowResponse(
                    success=False,
                    workflow_id=f"batch_error_{i}",
                    error_message=str(result)
                )
                responses.append(error_response)
            else:
                responses.append(result)
        
        return responses
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow statistics"""
        
        total_workflows = len(self.workflow_history)
        successful_workflows = len([w for w in self.workflow_history 
                                  if w.get('status') == 'completed'])
        
        if total_workflows == 0:
            return {'total_workflows': 0}
        
        success_rate = successful_workflows / total_workflows
        
        # Calculate average processing time
        processing_times = []
        for workflow in self.workflow_history:
            if 'end_time' in workflow and 'start_time' in workflow:
                duration = (workflow['end_time'] - workflow['start_time']).total_seconds()
                processing_times.append(duration)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Get generation engine statistics
        generation_stats = self.generation_engine.get_generation_statistics()
        
        # Get template usage statistics
        template_stats = self.template_manager.get_template_statistics()
        
        return {
            'workflow_statistics': {
                'total_workflows': total_workflows,
                'successful_workflows': successful_workflows,
                'success_rate': success_rate,
                'average_processing_time_seconds': avg_processing_time,
                'active_workflows': len(self.active_workflows)
            },
            'generation_statistics': generation_stats,
            'template_statistics': template_stats,
            'refinement_statistics': self.content_refiner.get_refinement_summary()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of specific workflow"""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'status': workflow['status'],
                'start_time': workflow['start_time'],
                'elapsed_time': (datetime.utcnow() - workflow['start_time']).total_seconds()
            }
        
        # Check workflow history
        for workflow in self.workflow_history:
            if workflow.get('workflow_id') == workflow_id:
                return {
                    'workflow_id': workflow_id,
                    'status': workflow.get('status', 'unknown'),
                    'start_time': workflow.get('start_time'),
                    'end_time': workflow.get('end_time'),
                    'total_time': (workflow['end_time'] - workflow['start_time']).total_seconds() if 'end_time' in workflow else None
                }
        
        return {'workflow_id': workflow_id, 'status': 'not_found'}
    
    async def regenerate_scene_with_feedback(self, original_workflow_id: str,
                                          feedback: Dict[str, Any]) -> GenerationWorkflowResponse:
        """Regenerate scene incorporating user feedback"""
        
        # Find original workflow
        original_workflow = None
        for workflow in self.workflow_history:
            if workflow.get('workflow_id') == original_workflow_id:
                original_workflow = workflow
                break
        
        if not original_workflow:
            return GenerationWorkflowResponse(
                success=False,
                workflow_id=f"regen_error_{original_workflow_id}",
                error_message="Original workflow not found"
            )
        
        # Create new request based on feedback
        original_request = original_workflow['request']
        
        # Update generation settings with feedback
        updated_settings = original_request.generation_settings.copy()
        
        if 'style_preferences' in feedback:
            updated_settings.update(feedback['style_preferences'])
        
        if 'content_changes' in feedback:
            updated_settings.update(feedback['content_changes'])
        
        # Increase creativity if user wants more variation
        if feedback.get('more_creative', False):
            updated_settings['creativity'] = min(1.0, updated_settings.get('creativity', 0.7) + 0.2)
        
        # Create regeneration request
        regen_request = GenerationWorkflowRequest(
            project_id=original_request.project_id,
            project_title=original_request.project_title,
            project_genre=original_request.project_genre,
            scene_type=original_request.scene_type,
            pov_character=original_request.pov_character,
            scene_purpose=original_request.scene_purpose,
            generation_settings=updated_settings,
            refinement_goals=feedback.get('refinement_focus', original_request.refinement_goals),
            auto_save=feedback.get('auto_save', False),  # Don't auto-save regenerations by default
            validate_before_save=original_request.validate_before_save
        )
        
        # Generate new version
        return await self.generate_scene_complete(regen_request)
    
    def export_workflow_history(self, output_path: str):
        """Export workflow history for analysis"""
        
        import json
        
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_workflows': len(self.workflow_history),
            'workflow_statistics': self.get_workflow_statistics(),
            'workflow_history': []
        }
        
        # Serialize workflow history
        for workflow in self.workflow_history:
            workflow_data = {
                'workflow_id': workflow.get('workflow_id'),
                'status': workflow.get('status'),
                'start_time': workflow.get('start_time').isoformat() if workflow.get('start_time') else None,
                'end_time': workflow.get('end_time').isoformat() if workflow.get('end_time') else None,
                'request_summary': {
                    'project_id': workflow['request'].project_id,
                    'scene_type': workflow['request'].scene_type.value,
                    'pov_character': workflow['request'].pov_character
                } if workflow.get('request') else None
            }
            export_data['workflow_history'].append(workflow_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return export_data