"""
Scene Engine API Performance Tests

TaskMaster Task 47.7: API Performance Tests
Performance and load testing for Scene Engine REST API endpoints.
Tests response times, concurrent request handling, and scalability limits.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from fastapi import status

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.main import app


class TestSceneEnginePerformance:
    """Performance tests for Scene Engine API endpoints"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_requests(self):
        """Sample requests for performance testing"""
        return {
            "plan_request": {
                "scene_type": "proactive",
                "scene_crucible": "The spy must escape the enemy compound before the alarm system activates",
                "pov_character": "Agent Riley",
                "pov": "third_limited",
                "tense": "past",
                "setting": "enemy military base"
            },
            "draft_request": {
                "scene_card": {
                    "scene_id": "perf_test_scene",
                    "scene_type": "proactive", 
                    "scene_crucible": "Racing against time to defuse the bomb",
                    "pov_character": "Bomb Disposal Expert",
                    "pov": "third_limited",
                    "tense": "past",
                    "setting": "underground facility",
                    "proactive": {
                        "goal": "defuse the bomb before detonation",
                        "conflict": "complex wiring and limited time",
                        "setback": "wrong wire cuts trigger backup timer"
                    }
                },
                "target_word_count": 1000
            },
            "triage_request": {
                "scene_card": {
                    "scene_id": "triage_perf_test",
                    "scene_type": "reactive",
                    "scene_crucible": "Dealing with the aftermath of betrayal",
                    "pov_character": "Betrayed Hero",
                    "pov": "first_person",
                    "tense": "past",
                    "setting": "abandoned safehouse",
                    "reactive": {
                        "reaction": "overwhelming anger and disbelief",
                        "dilemma": "trust the team or go alone",
                        "decision": "decides to confront the betrayer alone"
                    }
                },
                "prose_content": "I couldn't believe what had just happened. The betrayal cut deeper than any physical wound.",
                "triage_options": {
                    "auto_redesign_maybe": False  # Disable to speed up tests
                }
            }
        }
    
    def mock_successful_services(self):
        """Mock all services to return successful responses quickly"""
        # Mock scene planning service
        plan_patch = patch('src.scene_engine.planning.service.ScenePlanningService')
        plan_mock = plan_patch.start()
        
        plan_response = Mock()
        plan_response.success = True
        plan_response.scene_card = Mock()
        plan_response.scene_card.__dict__ = {"scene_type": "proactive", "scene_crucible": "test"}
        plan_response.validation_results = {}
        plan_response.structure_score = 0.8
        plan_response.recommendations = []
        plan_response.processing_time_seconds = 0.1
        plan_mock.return_value.generate_scene_plan.return_value = plan_response
        
        # Mock scene drafting service
        draft_patch = patch('src.scene_engine.drafting.service.SceneDraftingService')
        draft_mock = draft_patch.start()
        
        draft_response = Mock()
        draft_response.success = True
        draft_response.scene_card = Mock()
        draft_response.scene_card.__dict__ = {"scene_type": "proactive"}
        draft_response.prose_content = "Generated prose content for performance test."
        draft_response.structure_adherence_score = 0.85
        draft_response.pov_consistency_score = 0.9
        draft_response.exposition_usage = {"backstory": 50}
        draft_mock.return_value.draft_scene_prose.return_value = draft_response
        
        # Mock scene triage service
        triage_patch = patch('src.scene_engine.triage.service.SceneTriageService')
        triage_mock = triage_patch.start()
        
        triage_response = Mock()
        triage_response.success = True
        triage_response.decision = Mock()
        triage_response.decision.value = "YES"
        triage_response.classification_score = 0.87
        triage_response.final_scene_card = Mock()
        triage_response.final_scene_card.__dict__ = {"scene_type": "reactive"}
        triage_response.final_prose_content = "Enhanced prose content."
        triage_response.redesign_applied = False
        triage_response.redesign_attempts = 0
        triage_response.corrections_applied = []
        triage_response.quality_improvement = 0.0
        triage_response.recommendations = []
        triage_mock.return_value.evaluate_scene.return_value = triage_response
        
        # Mock persistence service
        persistence_patch = patch('src.scene_engine.persistence.service.ScenePersistenceService')
        persistence_mock = persistence_patch.start()
        
        mock_scene_card = Mock()
        mock_scene_card.__dict__ = {"scene_id": "test", "scene_type": "proactive"}
        persistence_mock.return_value.get_scene_card.return_value = mock_scene_card
        persistence_mock.return_value.get_scene_prose.return_value = "Sample prose"
        persistence_mock.return_value.get_scene_metadata.return_value = {
            "created_at": "2025-01-20T10:00:00Z",
            "triage_status": "YES"
        }
        persistence_mock.return_value.list_scenes.return_value = ["scene_1", "scene_2"]
        persistence_mock.return_value.delete_scene.return_value = True
        
        return [plan_patch, draft_patch, triage_patch, persistence_patch]
    
    def measure_response_time(self, func, *args, **kwargs) -> tuple:
        """Measure function execution time and return (result, time_ms)"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time) * 1000
    
    def test_plan_scene_response_time(self, client, sample_requests):
        """Test scene planning endpoint response time"""
        patches = self.mock_successful_services()
        try:
            response, time_ms = self.measure_response_time(
                client.post, "/scene/plan", json=sample_requests["plan_request"]
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert time_ms < 1000  # Should respond within 1 second
            print(f"Scene planning response time: {time_ms:.2f}ms")
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_draft_scene_response_time(self, client, sample_requests):
        """Test scene drafting endpoint response time"""
        patches = self.mock_successful_services()
        try:
            response, time_ms = self.measure_response_time(
                client.post, "/scene/draft", json=sample_requests["draft_request"]
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert time_ms < 1500  # Drafting may take longer
            print(f"Scene drafting response time: {time_ms:.2f}ms")
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_triage_scene_response_time(self, client, sample_requests):
        """Test scene triage endpoint response time"""
        patches = self.mock_successful_services()
        try:
            response, time_ms = self.measure_response_time(
                client.post, "/scene/triage", json=sample_requests["triage_request"]
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert time_ms < 2000  # Triage may be most complex
            print(f"Scene triage response time: {time_ms:.2f}ms")
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_get_scene_response_time(self, client):
        """Test scene retrieval endpoint response time"""
        patches = self.mock_successful_services()
        try:
            response, time_ms = self.measure_response_time(
                client.get, "/scene/test_scene_123"
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert time_ms < 500  # Simple retrieval should be fast
            print(f"Scene retrieval response time: {time_ms:.2f}ms")
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_concurrent_plan_requests(self, client, sample_requests):
        """Test concurrent scene planning requests"""
        patches = self.mock_successful_services()
        try:
            num_requests = 10
            
            def make_plan_request():
                return self.measure_response_time(
                    client.post, "/scene/plan", json=sample_requests["plan_request"]
                )
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_plan_request) for _ in range(num_requests)]
                results = []
                
                for future in as_completed(futures):
                    response, response_time = future.result()
                    results.append((response, response_time))
                    assert response.status_code == status.HTTP_200_OK
            
            total_time = (time.time() - start_time) * 1000
            response_times = [rt for _, rt in results]
            
            print(f"\nConcurrent Planning Test ({num_requests} requests):")
            print(f"Total time: {total_time:.2f}ms")
            print(f"Average response time: {statistics.mean(response_times):.2f}ms")
            print(f"Min response time: {min(response_times):.2f}ms")
            print(f"Max response time: {max(response_times):.2f}ms")
            print(f"Requests per second: {num_requests / (total_time / 1000):.2f}")
            
            # Assert reasonable performance
            assert statistics.mean(response_times) < 2000  # Average under 2 seconds
            assert total_time < 5000  # Total under 5 seconds
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_mixed_endpoint_load(self, client, sample_requests):
        """Test mixed load across different endpoints"""
        patches = self.mock_successful_services()
        try:
            num_requests_per_endpoint = 5
            
            def make_plan_request():
                return ("plan", self.measure_response_time(
                    client.post, "/scene/plan", json=sample_requests["plan_request"]
                ))
            
            def make_draft_request():
                return ("draft", self.measure_response_time(
                    client.post, "/scene/draft", json=sample_requests["draft_request"]
                ))
            
            def make_triage_request():
                return ("triage", self.measure_response_time(
                    client.post, "/scene/triage", json=sample_requests["triage_request"]
                ))
            
            def make_get_request():
                return ("get", self.measure_response_time(
                    client.get, "/scene/test_scene_123"
                ))
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                
                # Submit mixed requests
                for _ in range(num_requests_per_endpoint):
                    futures.extend([
                        executor.submit(make_plan_request),
                        executor.submit(make_draft_request),
                        executor.submit(make_triage_request),
                        executor.submit(make_get_request)
                    ])
                
                results_by_endpoint = {
                    "plan": [],
                    "draft": [],
                    "triage": [],
                    "get": []
                }
                
                for future in as_completed(futures):
                    endpoint_type, (response, response_time) = future.result()
                    results_by_endpoint[endpoint_type].append(response_time)
                    assert response.status_code == status.HTTP_200_OK
            
            total_time = (time.time() - start_time) * 1000
            total_requests = sum(len(times) for times in results_by_endpoint.values())
            
            print(f"\nMixed Load Test ({total_requests} total requests):")
            print(f"Total time: {total_time:.2f}ms")
            print(f"Overall requests per second: {total_requests / (total_time / 1000):.2f}")
            
            for endpoint, times in results_by_endpoint.items():
                if times:
                    print(f"{endpoint.capitalize()} - Avg: {statistics.mean(times):.2f}ms, "
                          f"Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
            
            # Performance assertions
            assert total_time < 10000  # Total under 10 seconds
            assert total_requests / (total_time / 1000) > 2  # At least 2 RPS
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_memory_usage_under_load(self, client, sample_requests):
        """Test memory usage during high load"""
        import psutil
        import os
        
        patches = self.mock_successful_services()
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            num_requests = 20
            
            def make_requests():
                # Make multiple requests in sequence
                for _ in range(5):
                    client.post("/scene/plan", json=sample_requests["plan_request"])
                    client.post("/scene/draft", json=sample_requests["draft_request"])
                    client.post("/scene/triage", json=sample_requests["triage_request"])
                    client.get("/scene/test_scene_123")
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(make_requests) for _ in range(4)]
                
                for future in as_completed(futures):
                    future.result()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"\nMemory Usage Test:")
            print(f"Initial memory: {initial_memory:.2f}MB")
            print(f"Final memory: {final_memory:.2f}MB")
            print(f"Memory increase: {memory_increase:.2f}MB")
            
            # Assert memory usage is reasonable (allow up to 50MB increase)
            assert memory_increase < 50, f"Memory usage increased by {memory_increase:.2f}MB"
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()
    
    def test_error_handling_performance(self, client):
        """Test performance of error handling paths"""
        # Test validation error performance
        invalid_request = {
            "scene_type": "invalid",
            "scene_crucible": "",  # Too short
            "pov_character": ""    # Empty
        }
        
        response, time_ms = self.measure_response_time(
            client.post, "/scene/plan", json=invalid_request
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert time_ms < 100  # Validation errors should be very fast
        print(f"Validation error response time: {time_ms:.2f}ms")
        
        # Test 404 error performance
        response, time_ms = self.measure_response_time(
            client.get, "/scene/nonexistent_scene"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert time_ms < 500  # 404 responses should be fast
        print(f"404 error response time: {time_ms:.2f}ms")
    
    def test_large_payload_handling(self, client):
        """Test handling of large request payloads"""
        patches = self.mock_successful_services()
        try:
            # Create large scene crucible (but within reasonable limits)
            large_crucible = "A" * 1000  # 1KB of text
            large_context = {
                "character_background": "B" * 2000,
                "setting_details": "C" * 1500,
                "previous_events": "D" * 1000
            }
            
            large_request = {
                "scene_type": "proactive",
                "scene_crucible": large_crucible,
                "pov_character": "Test Character",
                "pov": "third_limited",
                "tense": "past",
                "setting": "Large setting description",
                "context": large_context
            }
            
            response, time_ms = self.measure_response_time(
                client.post, "/scene/plan", json=large_request
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert time_ms < 2000  # Should handle large payloads reasonably
            print(f"Large payload response time: {time_ms:.2f}ms")
            
        finally:
            for patch_obj in patches:
                patch_obj.stop()


class TestSceneEngineStress:
    """Stress tests for Scene Engine API"""
    
    @pytest.fixture(scope="class") 
    def client(self):
        return TestClient(app)
    
    @pytest.mark.stress
    def test_sustained_load(self, client):
        """Test sustained load over extended period"""
        with patch('src.scene_engine.planning.service.ScenePlanningService') as mock_service:
            # Mock quick response
            mock_response = Mock()
            mock_response.success = True
            mock_response.scene_card = Mock()
            mock_response.scene_card.__dict__ = {"scene_type": "proactive"}
            mock_response.validation_results = {}
            mock_response.structure_score = 0.8
            mock_response.recommendations = []
            mock_response.processing_time_seconds = 0.1
            mock_service.return_value.generate_scene_plan.return_value = mock_response
            
            request = {
                "scene_type": "proactive",
                "scene_crucible": "Stress test scene",
                "pov_character": "Test character"
            }
            
            # Run requests for 30 seconds
            start_time = time.time()
            end_time = start_time + 30  # 30 seconds
            request_count = 0
            response_times = []
            errors = 0
            
            while time.time() < end_time:
                try:
                    req_start = time.time()
                    response = client.post("/scene/plan", json=request)
                    req_end = time.time()
                    
                    response_times.append((req_end - req_start) * 1000)
                    
                    if response.status_code != 200:
                        errors += 1
                    
                    request_count += 1
                    
                    # Small delay to prevent overwhelming
                    time.sleep(0.01)
                    
                except Exception as e:
                    errors += 1
                    print(f"Request error: {e}")
            
            total_time = time.time() - start_time
            
            print(f"\nSustained Load Test Results ({total_time:.1f}s):")
            print(f"Total requests: {request_count}")
            print(f"Successful requests: {request_count - errors}")
            print(f"Error rate: {errors / request_count * 100:.2f}%")
            print(f"Requests per second: {request_count / total_time:.2f}")
            
            if response_times:
                print(f"Average response time: {statistics.mean(response_times):.2f}ms")
                print(f"95th percentile response time: {statistics.quantiles(response_times, n=20)[18]:.2f}ms")
            
            # Performance assertions
            assert errors / request_count < 0.05  # Less than 5% error rate
            assert request_count / total_time > 1   # At least 1 RPS
            if response_times:
                assert statistics.mean(response_times) < 5000  # Average under 5 seconds


# Configuration for pytest performance tests
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "stress: mark test as a stress test (may take longer to run)"
    )