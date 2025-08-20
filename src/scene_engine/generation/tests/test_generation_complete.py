"""
Comprehensive Test Suite for Scene Generation Service

This implements subtask 44.5: Generation Tests
Complete test coverage for all generation components including engine,
templates, refinement, and integration service functionality.
"""

import pytest
import asyncio
import tempfile
import json
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from ..engine import (
    SceneGenerationEngine, GenerationRequest, GenerationResponse,
    GenerationContext, AIModelInterface, AIModel, PromptBuilder,
    GenerationError, ModelIntegrationError
)
from ..templates import (
    TemplateManager, SceneTemplate, PromptTemplate, TemplateType,
    GenreTemplate, TemplateLibrary, PromptLibrary
)
from ..refinement import (
    ContentRefiner, ContentAnalyzer, RefinementProcessor,
    RefinementIssue, RefinementSuggestion, RefinementType, RefinementPriority
)
from ..service import (
    SceneGenerationService, GenerationWorkflowRequest, GenerationWorkflowResponse
)

# Import scene engine models for test data
from ...models import SceneCard, SceneType, ViewpointType, TenseType, ProactiveScene, ReactiveScene
from ...validation.service import SceneValidationService, ValidationRequest, ValidationResponse
from ...persistence.service import PersistenceService


@pytest.fixture
def mock_ai_model():
    """Mock AI model interface for testing"""
    mock = Mock(spec=AIModelInterface)
    mock.model_type = AIModel.CLAUDE
    mock.generate_content = AsyncMock(return_value="""
    {
        "scene_crucible": "Jack must retrieve the ancient map from the heavily guarded library",
        "place": "Ancient Library",
        "time": "Midnight", 
        "proactive_data": {
            "goal": "Retrieve the ancient map without being detected",
            "conflict": "Guards patrol the library and security systems are active",
            "setback": "The map is incomplete, missing crucial navigation details"
        },
        "prose_content": "Jack crept through the shadows toward the ancient library, his heart pounding with each step. The guard rotation would change in ten minutes - his only window of opportunity. The massive oak doors loomed before him, their iron hinges promising to betray his presence with the slightest squeak. He had to get that map tonight, no matter the cost. But as he slipped inside and found the document case, his hopes crumbled. The map was torn, half of it missing, rendering his dangerous mission only partially successful.",
        "exposition_used": ["Jack's background as a thief", "Importance of the map"],
        "chain_link": "This scene follows Jack's decision to steal the map and leads to his reaction to finding it incomplete"
    }
    """)
    return mock


@pytest.fixture 
def mock_validation_service():
    """Mock validation service for testing"""
    mock = Mock(spec=SceneValidationService)
    mock.validate_scene_card.return_value = ValidationResponse(
        is_valid=True,
        errors=[],
        warnings=[],
        validation_details={}
    )
    return mock


@pytest.fixture
def mock_persistence_service():
    """Mock persistence service for testing"""
    mock = Mock(spec=PersistenceService)
    
    # Mock project summary
    mock.get_project_summary.return_value = {
        'project': {
            'id': 1,
            'title': 'Test Novel',
            'genre': 'Mystery',
            'author': 'Test Author'
        },
        'statistics': {
            'total_scenes': 5,
            'proactive_scenes': 3,
            'reactive_scenes': 2
        }
    }
    
    # Mock CRUD operations
    mock.crud = {
        'scene_cards': Mock(),
        'characters': Mock(),
        'chain_links': Mock()
    }
    
    mock.crud['scene_cards'].get_scene_cards.return_value = []
    mock.crud['characters'].get_characters.return_value = []
    
    return mock


@pytest.fixture
def sample_generation_request():
    """Sample generation request for testing"""
    context = GenerationContext(
        project_title="Test Novel",
        project_genre="Mystery",
        previous_scenes=[],
        character_profiles=[{
            'name': 'Jack',
            'role': 'protagonist',
            'description': 'Skilled thief with a moral code',
            'goals': ['Find the treasure', 'Protect his sister'],
            'conflicts': ['Trust issues', 'Criminal past']
        }]
    )
    
    return GenerationRequest(
        scene_type=SceneType.PROACTIVE,
        pov_character="Jack",
        scene_purpose="Jack attempts to steal the ancient map",
        context=context,
        emotional_tone="tense",
        setting_location="Ancient Library", 
        setting_time="Midnight",
        word_count_target=300
    )


@pytest.fixture
def temp_template_dir():
    """Temporary directory for template testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir)


# Generation Engine Tests
class TestSceneGenerationEngine:
    """Test scene generation engine functionality"""
    
    @pytest.mark.asyncio
    async def test_generation_engine_initialization(self, mock_ai_model, mock_validation_service):
        """Test generation engine initialization"""
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        assert engine.model_interface == mock_ai_model
        assert engine.validation_service == mock_validation_service
        assert isinstance(engine.prompt_builder, PromptBuilder)
        assert engine.generation_history == []
    
    @pytest.mark.asyncio
    async def test_successful_scene_generation(self, mock_ai_model, mock_validation_service, sample_generation_request):
        """Test successful scene generation flow"""
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        response = await engine.generate_scene(sample_generation_request)
        
        assert response.success is True
        assert response.scene_card is not None
        assert response.prose_content is not None
        assert response.scene_card.scene_type == SceneType.PROACTIVE
        assert response.scene_card.pov == "Jack"
        assert response.word_count > 0
        assert len(engine.generation_history) == 1
        
        # Verify AI model was called
        mock_ai_model.generate_content.assert_called_once()
        
        # Verify validation was performed
        mock_validation_service.validate_scene_card.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generation_with_invalid_json(self, mock_ai_model, mock_validation_service, sample_generation_request):
        """Test handling of invalid JSON from AI model"""
        # Mock invalid JSON response
        mock_ai_model.generate_content.return_value = "Invalid JSON response from AI model"
        
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        response = await engine.generate_scene(sample_generation_request)
        
        assert response.success is False
        assert "Failed to parse generated content" in response.error_message
    
    @pytest.mark.asyncio
    async def test_generation_model_error(self, mock_validation_service, sample_generation_request):
        """Test handling of AI model errors"""
        # Mock AI model that raises exception
        mock_ai_model = Mock(spec=AIModelInterface)
        mock_ai_model.generate_content = AsyncMock(side_effect=Exception("Model API error"))
        
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        response = await engine.generate_scene(sample_generation_request)
        
        assert response.success is False
        assert "Model API error" in response.error_message
    
    @pytest.mark.asyncio
    async def test_scene_refinement(self, mock_ai_model, mock_validation_service):
        """Test scene refinement functionality"""
        # Mock refined content response
        mock_ai_model.generate_content.return_value = """
        {
            "scene_crucible": "Improved scene crucible with more detail",
            "place": "Ancient Library",
            "time": "Midnight",
            "proactive_data": {
                "goal": "Enhanced goal description",
                "conflict": "More detailed conflict",
                "setback": "Stronger setback with consequences"
            },
            "prose_content": "Refined prose content with better flow and pacing",
            "exposition_used": [],
            "chain_link": "Improved chain link description"
        }
        """
        
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Create sample scene card
        original_scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Jack",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Original crucible",
            place="Library",
            time="Night",
            exposition_used=[],
            chain_link="",
            proactive=ProactiveScene(goal="Get map", conflict="Guards", setback="Incomplete")
        )
        
        refined_scene, refined_prose = await engine.refine_scene(
            original_scene_card,
            "Original prose content",
            ["Improve pacing", "Enhance description"]
        )
        
        assert refined_scene.scene_crucible == "Improved scene crucible with more detail"
        assert refined_prose == "Refined prose content with better flow and pacing"
    
    def test_generation_statistics(self, mock_ai_model, mock_validation_service):
        """Test generation statistics tracking"""
        engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Add mock generation history
        engine.generation_history = [
            {
                'response': Mock(success=True, generation_time_seconds=2.5, snowflake_compliance_score=0.8, model_used='claude')
            },
            {
                'response': Mock(success=False, generation_time_seconds=1.0, snowflake_compliance_score=0.0, model_used='claude')
            },
            {
                'response': Mock(success=True, generation_time_seconds=3.2, snowflake_compliance_score=0.9, model_used='claude')
            }
        ]
        
        stats = engine.get_generation_statistics()
        
        assert stats['total_generations'] == 3
        assert stats['successful_generations'] == 2
        assert stats['success_rate'] == 2/3
        assert stats['average_generation_time'] == (2.5 + 1.0 + 3.2) / 3
        assert stats['average_quality_score'] == (0.8 + 0.9) / 2


class TestPromptBuilder:
    """Test prompt building functionality"""
    
    def test_build_proactive_scene_prompt(self, sample_generation_request):
        """Test building proactive scene generation prompt"""
        prompt = PromptBuilder.build_scene_generation_prompt(sample_generation_request)
        
        assert "PROACTIVE SCENE STRUCTURE" in prompt
        assert "GOAL:" in prompt
        assert "CONFLICT:" in prompt
        assert "SETBACK:" in prompt
        assert "Jack" in prompt
        assert "Test Novel" in prompt
        assert "Mystery" in prompt
    
    def test_build_reactive_scene_prompt(self, sample_generation_request):
        """Test building reactive scene generation prompt"""
        # Modify request for reactive scene
        sample_generation_request.scene_type = SceneType.REACTIVE
        
        prompt = PromptBuilder.build_scene_generation_prompt(sample_generation_request)
        
        assert "REACTIVE SCENE STRUCTURE" in prompt
        assert "REACTION:" in prompt
        assert "DILEMMA:" in prompt
        assert "DECISION:" in prompt
    
    def test_build_refinement_prompt(self):
        """Test building refinement prompt"""
        original_content = "Original scene content that needs improvement"
        refinement_goals = ["Improve pacing", "Enhance dialogue", "Add sensory details"]
        
        prompt = PromptBuilder.build_refinement_prompt(original_content, refinement_goals)
        
        assert original_content in prompt
        assert "Improve pacing" in prompt
        assert "Enhance dialogue" in prompt
        assert "Add sensory details" in prompt
        assert "REFINEMENT GOALS" in prompt


# Template System Tests
class TestTemplateManager:
    """Test template management system"""
    
    def test_template_manager_initialization(self, temp_template_dir):
        """Test template manager initialization"""
        manager = TemplateManager(temp_template_dir)
        
        # Should load built-in templates
        assert len(manager.scene_templates) > 0
        assert len(manager.prompt_templates) > 0
        
        # Should have built-in template types
        template_types = set(t.template_type for t in manager.scene_templates.values())
        assert TemplateType.OPENING in template_types
        assert TemplateType.CONTINUATION in template_types
    
    def test_find_scene_template(self, temp_template_dir):
        """Test finding appropriate scene templates"""
        manager = TemplateManager(temp_template_dir)
        
        # Find proactive opening templates
        proactive_templates = manager.find_scene_template(
            SceneType.PROACTIVE, 
            TemplateType.OPENING
        )
        
        assert len(proactive_templates) > 0
        for template in proactive_templates:
            assert template.scene_type == SceneType.PROACTIVE
            assert template.template_type == TemplateType.OPENING
    
    def test_find_prompt_template(self, temp_template_dir):
        """Test finding appropriate prompt templates"""
        manager = TemplateManager(temp_template_dir)
        
        # Find mystery genre template
        mystery_template = manager.find_prompt_template(
            SceneType.PROACTIVE,
            GenreTemplate.MYSTERY
        )
        
        if mystery_template:  # Built-in templates may not include all genres
            assert GenreTemplate.MYSTERY in mystery_template.genre_affinity
    
    def test_template_usage_tracking(self, temp_template_dir):
        """Test template usage statistics"""
        manager = TemplateManager(temp_template_dir)
        
        # Get a template
        templates = list(manager.scene_templates.values())
        template = templates[0]
        original_usage = template.usage_count
        
        # Record usage
        manager.record_template_usage(template.template_id, 4.5)
        
        assert template.usage_count == original_usage + 1
        
        # Check statistics
        stats = manager.get_template_statistics()
        assert stats['total_scene_templates'] > 0
        assert stats['total_prompt_templates'] > 0
    
    def test_composite_prompt_creation(self, temp_template_dir):
        """Test creating composite prompts from templates"""
        manager = TemplateManager(temp_template_dir)
        
        # Get templates
        prompt_templates = list(manager.prompt_templates.values())
        scene_templates = list(manager.scene_templates.values())
        
        if prompt_templates and scene_templates:
            prompt_template = prompt_templates[0]
            scene_template = scene_templates[0]
            
            composite_prompt = manager.create_composite_prompt(
                prompt_template,
                scene_template,
                "Additional custom instructions for this specific scene"
            )
            
            assert prompt_template.system_prompt in composite_prompt
            assert scene_template.name in composite_prompt
            assert "Additional custom instructions" in composite_prompt
    
    def test_template_export_import(self, temp_template_dir):
        """Test template export functionality"""
        manager = TemplateManager(temp_template_dir)
        
        export_dir = Path(temp_template_dir) / "export"
        manager.export_templates(str(export_dir))
        
        # Check exported files exist
        assert (export_dir / "scene_templates").exists()
        assert (export_dir / "prompt_templates").exists()
        assert (export_dir / "usage_statistics.json").exists()
        
        # Check scene templates were exported
        scene_template_files = list((export_dir / "scene_templates").glob("*.json"))
        assert len(scene_template_files) > 0
        
        # Verify a template file
        with open(scene_template_files[0], 'r') as f:
            template_data = json.load(f)
            assert 'template_id' in template_data
            assert 'name' in template_data
            assert 'scene_type' in template_data


class TestTemplateLibrary:
    """Test built-in template library"""
    
    def test_proactive_opening_template(self):
        """Test proactive opening scene template"""
        template = TemplateLibrary.get_proactive_opening_template()
        
        assert template.scene_type == SceneType.PROACTIVE
        assert template.template_type == TemplateType.OPENING
        assert len(template.opening_patterns) > 0
        assert len(template.development_patterns) > 0
        assert len(template.climax_patterns) > 0
        assert len(template.resolution_patterns) > 0
        assert template.proactive_structure is not None
        assert 'goal_establishment' in template.proactive_structure
    
    def test_reactive_continuation_template(self):
        """Test reactive continuation scene template"""
        template = TemplateLibrary.get_reactive_continuation_template()
        
        assert template.scene_type == SceneType.REACTIVE
        assert template.template_type == TemplateType.CONTINUATION
        assert template.reactive_structure is not None
        assert 'reaction_authenticity' in template.reactive_structure
    
    def test_genre_specific_prompts(self):
        """Test genre-specific prompt templates"""
        genre_prompts = PromptLibrary.get_genre_specific_prompts()
        
        assert GenreTemplate.MYSTERY in genre_prompts
        assert GenreTemplate.ROMANCE in genre_prompts
        assert GenreTemplate.FANTASY in genre_prompts
        
        mystery_prompt = genre_prompts[GenreTemplate.MYSTERY]
        assert "mystery" in mystery_prompt.system_prompt.lower()
        assert "clues" in mystery_prompt.structure_prompt.lower()


# Content Refinement Tests
class TestContentAnalyzer:
    """Test content analysis functionality"""
    
    def test_content_analyzer_initialization(self, mock_validation_service):
        """Test content analyzer initialization"""
        analyzer = ContentAnalyzer(mock_validation_service)
        
        assert analyzer.validation_service == mock_validation_service
        assert len(analyzer.dialogue_patterns) > 0
        assert len(analyzer.pacing_patterns) > 0
        assert len(analyzer.consistency_patterns) > 0
    
    def test_analyze_content_comprehensive(self, mock_validation_service):
        """Test comprehensive content analysis"""
        analyzer = ContentAnalyzer(mock_validation_service)
        
        # Create test scene card
        scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Jack",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Jack must steal the map",
            place="Library",
            time="Night",
            exposition_used=[],
            chain_link="",
            proactive=ProactiveScene(
                goal="Get the map",
                conflict="Guards are present",
                setback="Map is incomplete"
            )
        )
        
        # Test prose with various issues
        prose_content = """
        Jack crept into the library. Jack moved carefully. Jack looked around.
        The was a guard somewhere nearby. He was walking really quickly and he was very nervous.
        "I need that map," he whispered softly to himself.
        """
        
        report = analyzer.analyze_content(scene_card, prose_content)
        
        assert report.content_id is not None
        assert report.original_word_count > 0
        assert len(report.issues_found) > 0
        assert len(report.suggestions_made) > 0
        assert 0.0 <= report.overall_quality_score <= 1.0
    
    def test_structure_analysis(self, mock_validation_service):
        """Test structure analysis functionality"""
        analyzer = ContentAnalyzer(mock_validation_service)
        
        # Test weak opening
        scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Jack",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Test crucible",
            place="Library",
            time="Night",
            exposition_used=[],
            chain_link="",
            proactive=ProactiveScene(goal="Test", conflict="Test", setback="Test")
        )
        
        weak_prose = "There was a man in the library when the clock struck midnight."
        
        issues = analyzer._analyze_structure(scene_card, weak_prose)
        
        # Should identify weak opening
        weak_opening_issues = [i for i in issues if "weak" in i.description.lower()]
        assert len(weak_opening_issues) > 0
    
    def test_style_analysis(self, mock_validation_service):
        """Test style analysis functionality"""
        analyzer = ContentAnalyzer(mock_validation_service)
        
        # Prose with style issues
        repetitive_prose = """
        Jack walked quickly. Sarah walked quickly. Tom walked quickly.
        He was really very extremely quite nervous. She was really very extremely quite scared.
        The book was being read by Jack. The door was being opened by Sarah.
        """
        
        issues = analyzer._analyze_style(repetitive_prose)
        
        # Should identify multiple style issues
        assert len(issues) > 0
        
        # Check for specific issue types
        issue_types = [i.refinement_type for i in issues]
        assert RefinementType.STYLE in issue_types
    
    def test_dialogue_analysis(self, mock_validation_service):
        """Test dialogue analysis functionality"""
        analyzer = ContentAnalyzer(mock_validation_service)
        
        # Prose with dialogue issues
        dialogue_prose = '''
        "I need to find that map," Jack said.
        "It's dangerous," Sarah said.
        "I don't care," Jack said.
        "But what if you're caught?" Sarah said.
        "I'll be careful," Jack said.
        '''
        
        issues = analyzer._analyze_dialogue(dialogue_prose)
        
        # Should identify repetitive dialogue tags
        repetitive_tag_issues = [i for i in issues if "said" in i.description.lower()]
        assert len(repetitive_tag_issues) > 0


class TestRefinementProcessor:
    """Test refinement processing functionality"""
    
    def test_refinement_processor_initialization(self):
        """Test refinement processor initialization"""
        processor = RefinementProcessor()
        
        assert processor.analyzer is not None
        assert processor.applied_refinements == []
    
    def test_apply_refinements(self):
        """Test applying refinements to content"""
        processor = RefinementProcessor()
        
        # Create test scene card
        scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Jack",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Test crucible",
            place="Library",
            time="Night",
            exposition_used=[],
            chain_link="",
            proactive=ProactiveScene(goal="Test", conflict="Test", setback="Test")
        )
        
        prose_content = "Jack walked quickly through the dark corridor."
        
        # Create refinement suggestions
        refinements = [
            RefinementSuggestion(
                suggestion_id="test_1",
                original_text="walked quickly",
                improved_text="crept silently",
                refinement_type=RefinementType.STYLE,
                confidence_score=0.8,
                reasoning="Replace adverb with stronger verb"
            )
        ]
        
        refined_scene, refined_prose, applied_changes = processor.apply_refinements(
            scene_card, prose_content, refinements, confidence_threshold=0.7
        )
        
        assert "crept silently" in refined_prose
        assert "walked quickly" not in refined_prose
        assert len(applied_changes) > 0
    
    def test_refinement_statistics(self):
        """Test refinement statistics tracking"""
        processor = RefinementProcessor()
        
        # Add mock applied refinements
        processor.applied_refinements = [
            Mock(refinement_type=RefinementType.STYLE, confidence_score=0.8),
            Mock(refinement_type=RefinementType.DIALOGUE, confidence_score=0.9),
            Mock(refinement_type=RefinementType.STYLE, confidence_score=0.7)
        ]
        
        stats = processor.get_refinement_statistics()
        
        assert stats['total_refinements'] == 3
        assert stats['refinements_by_type']['style'] == 2
        assert stats['refinements_by_type']['dialogue'] == 1
        assert stats['most_common_type'] == 'style'


class TestContentRefiner:
    """Test integrated content refinement system"""
    
    def test_content_refiner_initialization(self):
        """Test content refiner initialization"""
        refiner = ContentRefiner()
        
        assert refiner.analyzer is not None
        assert refiner.processor is not None
    
    def test_refine_scene_content(self, mock_validation_service):
        """Test complete scene content refinement"""
        analyzer = ContentAnalyzer(mock_validation_service)
        processor = RefinementProcessor(analyzer)
        refiner = ContentRefiner(analyzer, processor)
        
        # Create test scene card
        scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Jack",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Jack needs to find the map",
            place="Library",
            time="Night",
            exposition_used=[],
            chain_link="",
            proactive=ProactiveScene(
                goal="Find the ancient map",
                conflict="Library is guarded",
                setback="Map is damaged"
            )
        )
        
        prose_content = "Jack walked quickly through the library looking for the map."
        
        refined_scene, refined_prose, report = refiner.refine_scene_content(
            scene_card,
            prose_content,
            refinement_goals=[RefinementType.STYLE, RefinementType.PACING]
        )
        
        assert report.refinement_complete is True
        assert report.final_word_count > 0
        assert refined_scene is not None
        assert refined_prose is not None


# Integration Service Tests  
class TestSceneGenerationService:
    """Test integrated scene generation service"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_persistence_service, mock_validation_service, temp_template_dir):
        """Test service initialization with all components"""
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        
        assert service.persistence_service == mock_persistence_service
        assert service.validation_service == mock_validation_service
        assert service.template_manager is not None
        assert service.generation_engine is not None
        assert service.content_refiner is not None
    
    @pytest.mark.asyncio
    async def test_complete_generation_workflow(self, mock_ai_model, mock_persistence_service, 
                                               mock_validation_service, temp_template_dir):
        """Test complete scene generation workflow"""
        # Setup service with mocks
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        service.ai_model = mock_ai_model
        service.generation_engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Mock persistence methods
        mock_persistence_service.create_scene_card_with_prose.return_value = (
            Mock(id=1, scene_id='generated_scene_001'),
            Mock(word_count=250)
        )
        
        # Create workflow request
        request = GenerationWorkflowRequest(
            project_id=1,
            project_title="Test Novel",
            project_genre="Mystery",
            scene_type=SceneType.PROACTIVE,
            pov_character="Jack",
            scene_purpose="Jack searches for clues in the abandoned warehouse",
            generation_settings={
                'emotional_tone': 'tense',
                'location': 'Abandoned Warehouse',
                'word_count': 300
            },
            refinement_goals=[RefinementType.STYLE],
            auto_save=True,
            validate_before_save=True
        )
        
        # Execute workflow
        response = await service.generate_scene_complete(request)
        
        # Verify response
        assert response.success is True
        assert response.scene_card is not None
        assert response.prose_content is not None
        assert response.validation_passed is True
        assert response.saved_to_database is True
        assert response.total_processing_time > 0
        assert "scene_generation" in response.steps_completed
        
        # Verify AI model was called
        mock_ai_model.generate_content.assert_called()
        
        # Verify persistence was called
        mock_persistence_service.create_scene_card_with_prose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_persistence_service, mock_validation_service, temp_template_dir):
        """Test workflow error handling"""
        # Setup service with failing AI model
        mock_ai_model = Mock(spec=AIModelInterface)
        mock_ai_model.generate_content = AsyncMock(side_effect=Exception("AI model failed"))
        
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        service.ai_model = mock_ai_model
        service.generation_engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Create workflow request
        request = GenerationWorkflowRequest(
            project_id=1,
            project_title="Test Novel",
            project_genre="Mystery",
            scene_type=SceneType.PROACTIVE,
            pov_character="Jack",
            scene_purpose="Test scene"
        )
        
        # Execute workflow
        response = await service.generate_scene_complete(request)
        
        # Verify error response
        assert response.success is False
        assert response.error_message is not None
        assert "AI model failed" in response.error_message
        assert len(response.steps_failed) > 0
    
    @pytest.mark.asyncio
    async def test_batch_generation(self, mock_ai_model, mock_persistence_service, 
                                   mock_validation_service, temp_template_dir):
        """Test batch scene generation"""
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        service.ai_model = mock_ai_model
        service.generation_engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Mock persistence
        mock_persistence_service.create_scene_card_with_prose.return_value = (
            Mock(id=1, scene_id='scene_001'),
            Mock(word_count=200)
        )
        
        # Create multiple requests
        requests = [
            GenerationWorkflowRequest(
                project_id=1,
                project_title="Test Novel",
                project_genre="Mystery",
                scene_type=SceneType.PROACTIVE,
                pov_character="Jack",
                scene_purpose="Scene 1",
                auto_save=False
            ),
            GenerationWorkflowRequest(
                project_id=1,
                project_title="Test Novel", 
                project_genre="Mystery",
                scene_type=SceneType.REACTIVE,
                pov_character="Sarah",
                scene_purpose="Scene 2",
                auto_save=False
            )
        ]
        
        # Execute batch
        responses = service.generate_scene_batch(requests)
        
        assert len(responses) == 2
        for response in responses:
            if not isinstance(response, Exception):
                assert hasattr(response, 'success')
    
    def test_workflow_statistics(self, mock_persistence_service, mock_validation_service, temp_template_dir):
        """Test workflow statistics tracking"""
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        
        # Add mock workflow history
        service.workflow_history = [
            {'status': 'completed', 'start_time': datetime.now(), 'end_time': datetime.now()},
            {'status': 'failed', 'start_time': datetime.now(), 'end_time': datetime.now()},
            {'status': 'completed', 'start_time': datetime.now(), 'end_time': datetime.now()}
        ]
        
        stats = service.get_workflow_statistics()
        
        assert stats['workflow_statistics']['total_workflows'] == 3
        assert stats['workflow_statistics']['successful_workflows'] == 2
        assert stats['workflow_statistics']['success_rate'] == 2/3
        assert 'generation_statistics' in stats
        assert 'template_statistics' in stats
    
    @pytest.mark.asyncio
    async def test_regeneration_with_feedback(self, mock_ai_model, mock_persistence_service, 
                                            mock_validation_service, temp_template_dir):
        """Test scene regeneration with user feedback"""
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        service.ai_model = mock_ai_model
        service.generation_engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Add mock workflow to history
        original_request = GenerationWorkflowRequest(
            project_id=1,
            project_title="Test Novel",
            project_genre="Mystery",
            scene_type=SceneType.PROACTIVE,
            pov_character="Jack",
            scene_purpose="Original scene"
        )
        
        service.workflow_history = [{
            'workflow_id': 'original_123',
            'request': original_request,
            'status': 'completed'
        }]
        
        # Test regeneration with feedback
        feedback = {
            'style_preferences': {'creativity': 0.9},
            'content_changes': {'emotional_tone': 'dramatic'},
            'more_creative': True,
            'refinement_focus': [RefinementType.DIALOGUE]
        }
        
        response = await service.regenerate_scene_with_feedback('original_123', feedback)
        
        # Should create new generation with modified settings
        assert response.workflow_id != 'original_123'


# Integration Tests
class TestGenerationIntegration:
    """Test end-to-end generation integration"""
    
    @pytest.mark.asyncio
    async def test_full_generation_pipeline(self, mock_ai_model, mock_persistence_service, 
                                          mock_validation_service, temp_template_dir):
        """Test complete generation pipeline integration"""
        # Setup complete service
        service = SceneGenerationService(
            persistence_service=mock_persistence_service,
            validation_service=mock_validation_service,
            template_directory=temp_template_dir
        )
        service.ai_model = mock_ai_model
        service.generation_engine = SceneGenerationEngine(mock_ai_model, mock_validation_service)
        
        # Mock all required persistence methods
        mock_persistence_service.create_scene_card_with_prose.return_value = (
            Mock(id=1, scene_id='full_test_scene'),
            Mock(word_count=400)
        )
        
        # Create comprehensive workflow request
        request = GenerationWorkflowRequest(
            project_id=1,
            project_title="Integration Test Novel",
            project_genre="Fantasy",
            scene_type=SceneType.PROACTIVE,
            pov_character="Elena",
            scene_purpose="Elena must activate the ancient portal before the demons arrive",
            template_preferences=[TemplateType.ACTION_SEQUENCE],
            generation_settings={
                'emotional_tone': 'intense',
                'location': 'Ancient Portal Chamber',
                'time': 'Dawn of the final battle',
                'word_count': 500,
                'creativity': 0.8
            },
            refinement_goals=[RefinementType.PACING, RefinementType.DESCRIPTION],
            auto_save=True,
            validate_before_save=True,
            link_to_previous_scene=False
        )
        
        # Execute complete workflow
        response = await service.generate_scene_complete(request)
        
        # Comprehensive verification
        assert response.success is True
        assert response.scene_card is not None
        assert response.prose_content is not None
        assert response.scene_card.scene_type == SceneType.PROACTIVE
        assert response.scene_card.pov == "Elena"
        assert response.validation_passed is True
        assert response.saved_to_database is True
        
        # Verify all steps completed
        expected_steps = [
            "context_preparation",
            "template_selection", 
            "scene_generation",
            "content_refinement",
            "validation",
            "database_save"
        ]
        
        for step in expected_steps:
            assert step in response.steps_completed
        
        # Verify no steps failed
        assert len(response.steps_failed) == 0
        
        # Verify timing and metadata
        assert response.total_processing_time > 0
        assert response.generation_response is not None
        assert response.refinement_report is not None
        
        # Verify service statistics were updated
        stats = service.get_workflow_statistics()
        assert stats['workflow_statistics']['total_workflows'] >= 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])