"""
Scene Engine API Integration Tests

TaskMaster Task 47.7: API Integration Tests
Comprehensive integration tests for all Scene Engine REST API endpoints.
Tests cover happy path, error cases, and edge cases for each endpoint.
"""

import pytest
import json
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch
from datetime import datetime

from fastapi.testclient import TestClient
from fastapi import status

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.main import app
from src.scene_engine.models import SceneCard, SceneType


class TestSceneEngineIntegration:
    """Integration tests for Scene Engine API endpoints"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_proactive_plan_request(self):
        """Sample request for proactive scene planning"""
        return {
            "scene_type": "proactive",
            "scene_crucible": "The detective must infiltrate the criminal organization before they execute their plan",
            "pov_character": "Detective Sarah Chen",
            "pov": "third_limited",
            "tense": "past",
            "setting": "abandoned warehouse district",
            "context": {
                "preceding_scene_outcome": "discovered the location of the meeting",
                "character_goals": ["stop the crime", "protect innocents"]
            }
        }
    
    @pytest.fixture
    def sample_reactive_plan_request(self):
        """Sample request for reactive scene planning"""
        return {
            "scene_type": "reactive",
            "scene_crucible": "The hero faces the devastating loss of their mentor and must decide how to continue",
            "pov_character": "Alex Morgan",
            "pov": "first_person",
            "tense": "present",
            "setting": "mentor's destroyed laboratory"
        }
    
    @pytest.fixture
    def sample_scene_card(self):
        """Sample scene card for testing"""
        return {
            "scene_id": "test_scene_001",
            "scene_type": "proactive",
            "scene_crucible": "The hacker must break into the secure server before the deadline",
            "pov_character": "Marcus Kim",
            "pov": "third_limited", 
            "tense": "past",
            "setting": "underground bunker",
            "proactive": {
                "goal": "hack into the server and retrieve the stolen data",
                "conflict": "advanced security systems and time pressure",
                "setback": "security detects the intrusion and initiates lockdown"
            }
        }
    
    @pytest.fixture
    def sample_draft_request(self, sample_scene_card):
        """Sample request for scene drafting"""
        return {
            "scene_card": sample_scene_card,
            "target_word_count": 800,
            "style_preferences": {
                "dialogue_percentage": 0.3,
                "exposition_budget": {
                    "max_backstory_words": 100,
                    "max_description_words": 150
                }
            }
        }
    
    @pytest.fixture
    def sample_triage_request(self, sample_scene_card):
        """Sample request for scene triage"""
        return {
            "scene_card": sample_scene_card,
            "prose_content": "Marcus stared at the server. It was secure. He tried to hack it. It detected him. Security activated. He failed.",
            "triage_options": {
                "auto_redesign_maybe": True,
                "max_redesign_attempts": 2,
                "classification_criteria": {
                    "yes_quality_threshold": 0.8,
                    "no_quality_threshold": 0.5
                }
            }
        }
    
    # Test POST /scene/plan endpoint
    def test_plan_proactive_scene_success(self, client, sample_proactive_plan_request):
        """Test successful proactive scene planning"""
        with patch('src.scene_engine.planning.service.ScenePlanningService') as mock_service:
            # Mock successful planning response
            mock_response = Mock()
            mock_response.success = True
            mock_response.scene_card = Mock()
            mock_response.scene_card.__dict__ = sample_proactive_plan_request.copy()
            mock_response.validation_results = {"goal_validation": "passed"}
            mock_response.structure_score = 0.85
            mock_response.recommendations = ["Consider adding more specific conflict details"]
            mock_response.processing_time_seconds = 2.3
            
            mock_service.return_value.generate_scene_plan.return_value = mock_response
            
            response = client.post("/scene/plan", json=sample_proactive_plan_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "scene_card" in data
            assert "scene_id" in data
            assert "planning_details" in data
            assert data["planning_details"]["structure_adherence"] == 0.85
    
    def test_plan_reactive_scene_success(self, client, sample_reactive_plan_request):
        """Test successful reactive scene planning"""
        with patch('src.scene_engine.planning.service.ScenePlanningService') as mock_service:
            mock_response = Mock()
            mock_response.success = True
            mock_response.scene_card = Mock()
            mock_response.scene_card.__dict__ = sample_reactive_plan_request.copy()
            mock_response.validation_results = {"structure_validation": "passed"}
            mock_response.structure_score = 0.78
            mock_response.recommendations = []
            mock_response.processing_time_seconds = 1.8
            
            mock_service.return_value.generate_scene_plan.return_value = mock_response
            
            response = client.post("/scene/plan", json=sample_reactive_plan_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["scene_card"]["scene_type"] == "reactive"
    
    def test_plan_scene_validation_errors(self, client):
        """Test scene planning with validation errors"""
        # Missing required fields
        invalid_request = {
            "scene_type": "proactive"
            # Missing scene_crucible and pov_character
        }
        
        response = client.post("/scene/plan", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "validation_errors" in data
    
    def test_plan_scene_invalid_scene_type(self, client):
        """Test scene planning with invalid scene type"""
        invalid_request = {
            "scene_type": "invalid_type",
            "scene_crucible": "Test crucible",
            "pov_character": "Test character"
        }
        
        response = client.post("/scene/plan", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_plan_scene_service_failure(self, client, sample_proactive_plan_request):
        """Test scene planning when service fails"""
        with patch('src.scene_engine.planning.service.ScenePlanningService') as mock_service:
            mock_response = Mock()
            mock_response.success = False
            mock_response.error_message = "Goal validation failed"
            
            mock_service.return_value.generate_scene_plan.return_value = mock_response
            
            response = client.post("/scene/plan", json=sample_proactive_plan_request)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "Goal validation failed" in data["detail"]
    
    # Test POST /scene/draft endpoint
    def test_draft_scene_success(self, client, sample_draft_request):
        """Test successful scene drafting"""
        with patch('src.scene_engine.drafting.service.SceneDraftingService') as mock_service:
            mock_response = Mock()
            mock_response.success = True
            mock_response.scene_card = Mock()
            mock_response.scene_card.__dict__ = sample_draft_request["scene_card"]
            mock_response.prose_content = "Marcus approached the server with determination. The security systems hummed ominously around him as he began his infiltration attempt. Time was running short."
            mock_response.structure_adherence_score = 0.92
            mock_response.pov_consistency_score = 0.88
            mock_response.exposition_usage = {"backstory": 45, "description": 102}
            
            mock_service.return_value.draft_scene_prose.return_value = mock_response
            
            response = client.post("/scene/draft", json=sample_draft_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "prose_content" in data
            assert "quality_metrics" in data
            assert data["quality_metrics"]["structure_adherence_score"] == 0.92
            assert data["quality_metrics"]["word_count"] > 0
    
    def test_draft_scene_invalid_scene_card(self, client):
        """Test scene drafting with invalid scene card"""
        invalid_request = {
            "scene_card": {
                "scene_type": "invalid"  # Invalid enum value
            },
            "target_word_count": 500
        }
        
        response = client.post("/scene/draft", json=invalid_request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid scene card format" in data["detail"]
    
    def test_draft_scene_word_count_limits(self, client, sample_scene_card):
        """Test scene drafting with invalid word count limits"""
        # Test word count too low
        request = {
            "scene_card": sample_scene_card,
            "target_word_count": 50  # Below minimum
        }
        
        response = client.post("/scene/draft", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test word count too high
        request["target_word_count"] = 10000  # Above maximum
        response = client.post("/scene/draft", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_draft_scene_service_failure(self, client, sample_draft_request):
        """Test scene drafting when service fails"""
        with patch('src.scene_engine.drafting.service.SceneDraftingService') as mock_service:
            mock_response = Mock()
            mock_response.success = False
            mock_response.error_message = "POV consistency check failed"
            
            mock_service.return_value.draft_scene_prose.return_value = mock_response
            
            response = client.post("/scene/draft", json=sample_draft_request)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "POV consistency check failed" in data["detail"]
    
    # Test POST /scene/triage endpoint
    def test_triage_scene_yes_decision(self, client, sample_triage_request):
        """Test scene triage with YES decision"""
        with patch('src.scene_engine.triage.service.SceneTriageService') as mock_service:
            mock_response = Mock()
            mock_response.success = True
            mock_response.decision = Mock()
            mock_response.decision.value = "YES"
            mock_response.classification_score = 0.89
            mock_response.final_scene_card = Mock()
            mock_response.final_scene_card.__dict__ = sample_triage_request["scene_card"]
            mock_response.final_prose_content = "Enhanced prose content..."
            mock_response.redesign_applied = False
            mock_response.redesign_attempts = 0
            mock_response.corrections_applied = []
            mock_response.quality_improvement = 0.0
            mock_response.recommendations = ["Scene meets all quality standards"]
            
            mock_service.return_value.evaluate_scene.return_value = mock_response
            
            response = client.post("/scene/triage", json=sample_triage_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["decision"] == "YES"
            assert data["classification_score"] == 0.89
            assert data["redesign_applied"] is False
    
    def test_triage_scene_maybe_with_redesign(self, client, sample_triage_request):
        """Test scene triage with MAYBE decision and redesign"""
        with patch('src.scene_engine.triage.service.SceneTriageService') as mock_service:
            mock_response = Mock()
            mock_response.success = True
            mock_response.decision = Mock()
            mock_response.decision.value = "MAYBE"
            mock_response.classification_score = 0.65
            mock_response.final_scene_card = Mock()
            mock_response.final_scene_card.__dict__ = sample_triage_request["scene_card"]
            mock_response.final_prose_content = "Redesigned prose content with improvements..."
            mock_response.redesign_applied = True
            mock_response.redesign_attempts = 2
            mock_response.corrections_applied = ["scene_type_correction", "part_rewriting"]
            mock_response.quality_improvement = 0.18
            mock_response.recommendations = ["Consider adding more sensory details"]
            
            mock_service.return_value.evaluate_scene.return_value = mock_response
            
            response = client.post("/scene/triage", json=sample_triage_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["decision"] == "MAYBE"
            assert data["redesign_applied"] is True
            assert data["redesign_summary"]["attempts"] == 2
            assert data["redesign_summary"]["quality_improvement"] == 0.18
    
    def test_triage_scene_no_decision(self, client, sample_triage_request):
        """Test scene triage with NO decision"""
        with patch('src.scene_engine.triage.service.SceneTriageService') as mock_service:
            mock_response = Mock()
            mock_response.success = True
            mock_response.decision = Mock()
            mock_response.decision.value = "NO"
            mock_response.classification_score = 0.32
            mock_response.final_scene_card = Mock()
            mock_response.final_scene_card.__dict__ = sample_triage_request["scene_card"]
            mock_response.final_prose_content = None
            mock_response.redesign_applied = False
            mock_response.redesign_attempts = 0
            mock_response.corrections_applied = []
            mock_response.quality_improvement = 0.0
            mock_response.recommendations = [
                "Scene lacks clear goal structure",
                "POV inconsistencies detected",
                "Conflict needs more specificity"
            ]
            
            mock_service.return_value.evaluate_scene.return_value = mock_response
            
            response = client.post("/scene/triage", json=sample_triage_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["decision"] == "NO"
            assert data["classification_score"] == 0.32
            assert len(data["recommendations"]) == 3
    
    def test_triage_scene_service_failure(self, client, sample_triage_request):
        """Test scene triage when service fails"""
        with patch('src.scene_engine.triage.service.SceneTriageService') as mock_service:
            mock_response = Mock()
            mock_response.success = False
            mock_response.identified_issues = ["Validation failed", "Structure incomplete"]
            
            mock_service.return_value.evaluate_scene.return_value = mock_response
            
            response = client.post("/scene/triage", json=sample_triage_request)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "Validation failed, Structure incomplete" in data["detail"]
    
    # Test GET /scene/{scene_id} endpoint
    def test_get_scene_success(self, client):
        """Test successful scene retrieval"""
        scene_id = "test_scene_123"
        
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_scene_card = Mock()
            mock_scene_card.__dict__ = {
                "scene_id": scene_id,
                "scene_type": "proactive",
                "scene_crucible": "Test crucible",
                "pov_character": "Test character"
            }
            
            mock_metadata = {
                "created_at": "2025-01-20T10:30:00Z",
                "last_modified": "2025-01-20T11:00:00Z",
                "version": 1,
                "triage_status": "YES"
            }
            
            mock_service.return_value.get_scene_card.return_value = mock_scene_card
            mock_service.return_value.get_scene_metadata.return_value = mock_metadata
            
            response = client.get(f"/scene/{scene_id}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["scene_id"] == scene_id
            assert "scene_card" in data
            assert "metadata" in data
            assert data["prose_content"] is None  # Not requested
    
    def test_get_scene_with_prose(self, client):
        """Test scene retrieval with prose content"""
        scene_id = "test_scene_456"
        sample_prose = "This is the generated prose content for the scene."
        
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_scene_card = Mock()
            mock_scene_card.__dict__ = {"scene_id": scene_id, "scene_type": "reactive"}
            
            mock_service.return_value.get_scene_card.return_value = mock_scene_card
            mock_service.return_value.get_scene_prose.return_value = sample_prose
            mock_service.return_value.get_scene_metadata.return_value = {}
            
            response = client.get(f"/scene/{scene_id}?include_prose=true")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["prose_content"] == sample_prose
    
    def test_get_scene_not_found(self, client):
        """Test scene retrieval for non-existent scene"""
        scene_id = "nonexistent_scene"
        
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_service.return_value.get_scene_card.side_effect = FileNotFoundError()
            
            response = client.get(f"/scene/{scene_id}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert f"Scene {scene_id} not found" in data["detail"]
    
    # Test utility endpoints
    def test_list_scenes(self, client):
        """Test listing scenes"""
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_service.return_value.list_scenes.return_value = ["scene_1", "scene_2"]
            
            # Mock scene cards and metadata
            mock_scene_1 = Mock()
            mock_scene_1.__dict__ = {
                "scene_id": "scene_1",
                "scene_type": SceneType.PROACTIVE,
                "pov_character": "Character 1",
                "scene_crucible": "Short crucible"
            }
            
            mock_scene_2 = Mock()
            mock_scene_2.__dict__ = {
                "scene_id": "scene_2", 
                "scene_type": SceneType.REACTIVE,
                "pov_character": "Character 2",
                "scene_crucible": "A" * 120  # Long crucible to test truncation
            }
            
            def mock_get_scene_card(scene_id):
                if scene_id == "scene_1":
                    return mock_scene_1
                elif scene_id == "scene_2":
                    return mock_scene_2
                raise FileNotFoundError()
            
            def mock_get_scene_metadata(scene_id):
                return {"created_at": "2025-01-20T10:00:00Z", "triage_status": "YES"}
            
            mock_service.return_value.get_scene_card.side_effect = mock_get_scene_card
            mock_service.return_value.get_scene_metadata.side_effect = mock_get_scene_metadata
            
            response = client.get("/scene/?limit=10&offset=0")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "scenes" in data
            assert data["total"] == 2
            assert len(data["scenes"]) == 2
            
            # Check truncation
            scene_2_data = next(s for s in data["scenes"] if s["scene_id"] == "scene_2")
            assert scene_2_data["scene_crucible"].endswith("...")
    
    def test_delete_scene(self, client):
        """Test scene deletion"""
        scene_id = "test_scene_delete"
        
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_scene_card = Mock()
            mock_service.return_value.get_scene_card.return_value = mock_scene_card
            mock_service.return_value.delete_scene.return_value = True
            
            response = client.delete(f"/scene/{scene_id}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert scene_id in data["message"]
    
    def test_delete_scene_not_found(self, client):
        """Test deleting non-existent scene"""
        scene_id = "nonexistent_scene"
        
        with patch('src.scene_engine.persistence.service.ScenePersistenceService') as mock_service:
            mock_service.return_value.get_scene_card.side_effect = FileNotFoundError()
            
            response = client.delete(f"/scene/{scene_id}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Error handling tests
    def test_general_exception_handling(self, client):
        """Test general exception handling"""
        with patch('src.scene_engine.planning.service.ScenePlanningService') as mock_service:
            mock_service.return_value.generate_scene_plan.side_effect = Exception("Unexpected error")
            
            request = {
                "scene_type": "proactive",
                "scene_crucible": "Test crucible",
                "pov_character": "Test character"
            }
            
            response = client.post("/scene/plan", json=request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["code"] == "INTERNAL_ERROR"
            assert "error_id" in data
            assert "timestamp" in data


# Fixture for pytest
@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async test backend"""
    return "asyncio"