"""
Test Configuration for Scene Engine API Tests

TaskMaster Task 47.7: Test Configuration and Fixtures
Common test configuration, fixtures, and utilities for API tests.
"""

import pytest
import os
import sys
import logging
from unittest.mock import Mock, patch

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Disable verbose logging from some modules during tests
logging.getLogger('src.scene_engine').setLevel(logging.WARNING)
logging.getLogger('fastapi').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables"""
    # Set test-specific environment variables
    os.environ['TESTING'] = 'true'
    os.environ['API_HOST'] = 'localhost'
    os.environ['API_PORT'] = '8000'
    
    # Mock API keys to avoid real API calls during testing
    os.environ['ANTHROPIC_API_KEY'] = 'test_anthropic_key_123'
    os.environ['OPENAI_API_KEY'] = 'test_openai_key_456'
    
    yield
    
    # Clean up
    for key in ['TESTING', 'API_HOST', 'API_PORT', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY']:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_scene_services():
    """Mock all Scene Engine services for consistent testing"""
    
    patches = {}
    
    # Mock Scene Planning Service
    plan_patch = patch('src.scene_engine.planning.service.ScenePlanningService')
    plan_mock = plan_patch.start()
    patches['planning'] = plan_patch
    
    plan_response = Mock()
    plan_response.success = True
    plan_response.scene_card = Mock()
    plan_response.scene_card.__dict__ = {
        'scene_id': 'mock_scene_123',
        'scene_type': 'proactive',
        'scene_crucible': 'Mock scene crucible',
        'pov_character': 'Mock Character'
    }
    plan_response.validation_results = {'goal_validation': 'passed'}
    plan_response.structure_score = 0.85
    plan_response.recommendations = ['Mock recommendation']
    plan_response.processing_time_seconds = 1.2
    
    plan_mock.return_value.generate_scene_plan.return_value = plan_response
    
    # Mock Scene Drafting Service
    draft_patch = patch('src.scene_engine.drafting.service.SceneDraftingService')
    draft_mock = draft_patch.start()
    patches['drafting'] = draft_patch
    
    draft_response = Mock()
    draft_response.success = True
    draft_response.scene_card = Mock()
    draft_response.scene_card.__dict__ = {
        'scene_id': 'mock_scene_456',
        'scene_type': 'proactive'
    }
    draft_response.prose_content = "Mock generated prose content for the scene."
    draft_response.structure_adherence_score = 0.92
    draft_response.pov_consistency_score = 0.88
    draft_response.exposition_usage = {'backstory': 45, 'description': 102}
    
    draft_mock.return_value.draft_scene_prose.return_value = draft_response
    
    # Mock Scene Triage Service
    triage_patch = patch('src.scene_engine.triage.service.SceneTriageService')
    triage_mock = triage_patch.start()
    patches['triage'] = triage_patch
    
    triage_response = Mock()
    triage_response.success = True
    triage_response.decision = Mock()
    triage_response.decision.value = 'YES'
    triage_response.classification_score = 0.89
    triage_response.final_scene_card = Mock()
    triage_response.final_scene_card.__dict__ = {
        'scene_id': 'mock_scene_789',
        'scene_type': 'reactive'
    }
    triage_response.final_prose_content = "Mock enhanced prose content."
    triage_response.redesign_applied = False
    triage_response.redesign_attempts = 0
    triage_response.corrections_applied = []
    triage_response.quality_improvement = 0.0
    triage_response.recommendations = ['Mock triage recommendation']
    
    triage_mock.return_value.evaluate_scene.return_value = triage_response
    
    # Mock Scene Persistence Service
    persistence_patch = patch('src.scene_engine.persistence.service.ScenePersistenceService')
    persistence_mock = persistence_patch.start()
    patches['persistence'] = persistence_patch
    
    mock_scene_card = Mock()
    mock_scene_card.__dict__ = {
        'scene_id': 'mock_stored_scene',
        'scene_type': 'proactive',
        'scene_crucible': 'Stored scene crucible',
        'pov_character': 'Stored Character'
    }
    
    mock_metadata = {
        'created_at': '2025-01-20T10:30:00Z',
        'last_modified': '2025-01-20T11:00:00Z',
        'version': 1,
        'triage_status': 'YES'
    }
    
    persistence_mock.return_value.get_scene_card.return_value = mock_scene_card
    persistence_mock.return_value.get_scene_prose.return_value = "Mock stored prose content"
    persistence_mock.return_value.get_scene_metadata.return_value = mock_metadata
    persistence_mock.return_value.list_scenes.return_value = ['scene_1', 'scene_2', 'scene_3']
    persistence_mock.return_value.save_scene_card.return_value = True
    persistence_mock.return_value.save_scene_prose.return_value = True
    persistence_mock.return_value.delete_scene.return_value = True
    
    yield patches
    
    # Clean up patches
    for patch_obj in patches.values():
        patch_obj.stop()


@pytest.fixture
def sample_scene_data():
    """Sample scene data for testing"""
    return {
        'proactive_scene_card': {
            'scene_id': 'test_proactive_scene',
            'scene_type': 'proactive',
            'scene_crucible': 'The detective must solve the case before the killer strikes again',
            'pov_character': 'Detective Sarah Wilson',
            'pov': 'third_limited',
            'tense': 'past',
            'setting': 'police precinct',
            'proactive': {
                'goal': 'identify the killer from the evidence',
                'conflict': 'limited evidence and political pressure',
                'setback': 'key witness refuses to testify'
            }
        },
        'reactive_scene_card': {
            'scene_id': 'test_reactive_scene',
            'scene_type': 'reactive',
            'scene_crucible': 'Processing the devastating news of betrayal',
            'pov_character': 'Hero protagonist',
            'pov': 'first_person',
            'tense': 'present',
            'setting': 'abandoned warehouse',
            'reactive': {
                'reaction': 'shock and overwhelming anger',
                'dilemma': 'confront the betrayer or seek evidence',
                'decision': 'decides to gather proof before confronting'
            }
        },
        'sample_prose': {
            'short': "The door creaked open. Sarah stepped inside cautiously.",
            'medium': """
            Detective Sarah Wilson approached the crime scene with measured steps, 
            her trained eye already cataloging details. The victim lay sprawled 
            across the marble floor, a pool of crimson expanding beneath the body.
            
            "What do we know?" she asked her partner, pulling on latex gloves.
            
            The killer had left no obvious clues, but Sarah had learned that 
            the most important evidence was often hidden in plain sight.
            """,
            'long': """
            The rain hammered against the precinct windows as Detective Sarah Wilson 
            stared at the case files spread across her desk. Three victims, three 
            different locations, but something connected them all—she could feel it.
            
            "Working late again?" Captain Martinez approached, coffee in hand.
            
            "The pattern is there, Captain. I just can't see it yet." Sarah rubbed 
            her tired eyes. The killer was escalating, and they were running out of time.
            
            She picked up the first victim's photo. Young, ambitious, working in tech. 
            The second victim was older, a teacher. The third, a local business owner.
            No obvious connections, different social circles, different parts of the city.
            
            But the killer chose them for a reason. There had to be something.
            
            Sarah's phone buzzed. Another crime scene. Another victim.
            
            Time was up.
            """
        }
    }


@pytest.fixture
def api_test_data():
    """API-specific test data"""
    return {
        'valid_plan_requests': [
            {
                'scene_type': 'proactive',
                'scene_crucible': 'Hero must escape the collapsing building',
                'pov_character': 'Action Hero',
                'pov': 'third_limited',
                'tense': 'past'
            },
            {
                'scene_type': 'reactive',
                'scene_crucible': 'Dealing with the loss of a team member',
                'pov_character': 'Team Leader',
                'pov': 'first_person',
                'tense': 'present'
            }
        ],
        'invalid_plan_requests': [
            {
                'scene_type': 'invalid_type',
                'scene_crucible': 'Test crucible',
                'pov_character': 'Test character'
            },
            {
                'scene_type': 'proactive',
                'scene_crucible': '',  # Too short
                'pov_character': 'Test character'
            },
            {
                'scene_type': 'proactive',
                'scene_crucible': 'Test crucible'
                # Missing pov_character
            }
        ],
        'performance_test_requests': {
            'light_load': 5,
            'medium_load': 20,
            'heavy_load': 50
        }
    }


# Custom pytest markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "stress: mark test as stress test (long running)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# Custom test collection hook
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test file names"""
    for item in items:
        # Add integration marker to integration test files
        if "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance test files
        if "performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
        
        # Add stress marker to tests with 'stress' in the name
        if "stress" in item.name.lower():
            item.add_marker(pytest.mark.stress)


# Test utilities
class TestHelper:
    """Helper utilities for API tests"""
    
    @staticmethod
    def assert_valid_scene_card(scene_card_data: dict):
        """Assert that a scene card has valid structure"""
        required_fields = ['scene_id', 'scene_type', 'scene_crucible', 'pov_character']
        
        for field in required_fields:
            assert field in scene_card_data, f"Missing required field: {field}"
            assert scene_card_data[field], f"Empty required field: {field}"
        
        assert scene_card_data['scene_type'] in ['proactive', 'reactive']
        
        if scene_card_data['scene_type'] == 'proactive':
            assert 'proactive' in scene_card_data
            proactive = scene_card_data['proactive']
            assert all(key in proactive for key in ['goal', 'conflict', 'setback'])
        
        elif scene_card_data['scene_type'] == 'reactive':
            assert 'reactive' in scene_card_data
            reactive = scene_card_data['reactive']
            assert all(key in reactive for key in ['reaction', 'dilemma', 'decision'])
    
    @staticmethod
    def assert_valid_api_response(response_data: dict, expected_fields: list):
        """Assert that an API response has the expected structure"""
        for field in expected_fields:
            assert field in response_data, f"Missing expected field: {field}"
    
    @staticmethod
    def assert_error_response(response_data: dict):
        """Assert that an error response has the correct structure"""
        required_error_fields = ['error', 'detail', 'code', 'timestamp']
        
        for field in required_error_fields:
            assert field in response_data, f"Missing error field: {field}"


@pytest.fixture
def test_helper():
    """Provide test helper utilities"""
    return TestHelper