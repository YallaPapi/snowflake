# Scene Engine API Tests

**TaskMaster Task 47.7: API Integration and Performance Tests**

Comprehensive test suite for Scene Engine REST API endpoints covering integration testing, performance testing, and stress testing.

## Overview

This test suite validates all Scene Engine API endpoints:

- `POST /scene/plan` - Scene planning endpoint
- `POST /scene/draft` - Scene drafting endpoint  
- `POST /scene/triage` - Scene triage endpoint
- `GET /scene/{id}` - Scene retrieval endpoint
- Utility endpoints (list, delete)

## Test Categories

### Integration Tests
- **File**: `test_scene_engine_integration.py`
- **Purpose**: End-to-end testing of API endpoints
- **Coverage**: Happy path, error cases, edge cases
- **Features**:
  - Request/response validation
  - Error handling verification
  - Business logic validation
  - Mock-based service testing

### Performance Tests
- **File**: `test_scene_engine_performance.py`
- **Purpose**: Response time and scalability testing
- **Coverage**: Individual endpoints, concurrent requests, sustained load
- **Metrics**:
  - Response time measurement
  - Concurrent request handling
  - Memory usage tracking
  - Error rate monitoring

### Stress Tests
- **Subset**: Performance tests with `@pytest.mark.stress`
- **Purpose**: Extended load testing
- **Coverage**: Sustained high load scenarios
- **Duration**: Longer running tests (30+ seconds)

## Quick Start

### 1. Install Dependencies

```bash
# Install test dependencies
python src/api/tests/run_tests.py --install-deps

# Or manually
pip install -r src/api/tests/requirements-test.txt
```

### 2. Run Tests

```bash
# Quick smoke test (fastest)
python src/api/tests/run_tests.py --quick

# Integration tests
python src/api/tests/run_tests.py --integration --verbose

# Performance tests  
python src/api/tests/run_tests.py --performance

# All tests with coverage
python src/api/tests/run_tests.py --all --coverage

# Include stress tests (long running)
python src/api/tests/run_tests.py --performance --stress
```

### 3. View Results

Test reports are generated in `src/api/tests/reports/`:

- `integration_report.html` - Integration test results
- `performance_report.html` - Performance test results  
- `full_test_report.html` - Complete test results
- `coverage_*/index.html` - Coverage reports
- `test_summary.txt` - Test execution summary

## Test Structure

```
src/api/tests/
├── __init__.py                           # Package init
├── conftest.py                          # Test configuration and fixtures
├── test_scene_engine_integration.py    # Integration tests
├── test_scene_engine_performance.py    # Performance tests
├── requirements-test.txt               # Test dependencies
├── run_tests.py                        # Test runner script
├── README.md                           # This file
└── reports/                            # Generated test reports
```

## Key Features

### Mocked Services
Tests use mocked Scene Engine services to:
- Ensure consistent test behavior
- Avoid external dependencies
- Enable fast test execution
- Test error scenarios

### Comprehensive Coverage
- All API endpoints tested
- Request validation testing
- Response format validation
- Error handling verification
- Performance benchmarking

### Flexible Test Execution
- Multiple test categories
- Configurable verbosity
- Coverage reporting
- HTML report generation
- JSON result export

## Test Data

### Sample Requests
The test suite includes comprehensive sample data:

```python
# Proactive scene planning
{
    "scene_type": "proactive",
    "scene_crucible": "The detective must solve the case before the killer strikes again",
    "pov_character": "Detective Sarah Wilson",
    "pov": "third_limited",
    "tense": "past"
}

# Scene drafting with style preferences
{
    "scene_card": {...},
    "target_word_count": 800,
    "style_preferences": {
        "dialogue_percentage": 0.3,
        "exposition_budget": {
            "max_backstory_words": 100
        }
    }
}
```

### Mock Responses
Services return realistic mock responses:

```python
# Successful scene planning response
{
    "success": True,
    "scene_card": {...},
    "scene_id": "mock_scene_123",
    "planning_details": {
        "structure_adherence": 0.85,
        "recommendations": ["Consider adding more specific conflict details"]
    }
}
```

## Performance Benchmarks

### Response Time Targets
- Scene retrieval: < 500ms
- Scene planning: < 1000ms  
- Scene drafting: < 1500ms
- Scene triage: < 2000ms

### Load Testing
- Concurrent requests: 5-10 simultaneous
- Sustained load: 30+ seconds
- Memory usage: < 50MB increase
- Error rate: < 5%

### Stress Testing
- Extended duration testing
- High concurrency scenarios
- Memory leak detection
- Performance degradation monitoring

## Error Scenarios

Tests cover all error conditions:

### Validation Errors (422)
- Invalid scene types
- Missing required fields
- Invalid field values
- Malformed requests

### Client Errors (400, 404)
- Invalid scene card format
- Scene not found
- Invalid parameters

### Server Errors (500)
- Service failures
- Unexpected exceptions
- Database errors

## Custom Fixtures

### `mock_scene_services`
Mocks all Scene Engine services with successful responses.

### `sample_scene_data`
Provides realistic test data for various scenarios.

### `api_test_data`
API-specific test data including valid/invalid requests.

### `test_helper`
Utility functions for common test assertions.

## Test Markers

```python
@pytest.mark.integration  # Integration tests
@pytest.mark.performance  # Performance tests
@pytest.mark.stress      # Stress tests (long running)
@pytest.mark.unit        # Unit tests
```

## Running Specific Tests

```bash
# Run only integration tests
pytest -m integration

# Run performance tests excluding stress
pytest -m "performance and not stress"

# Run specific test function
pytest -k "test_plan_proactive_scene_success"

# Run with coverage
pytest --cov=src.api --cov=src.scene_engine
```

## Continuous Integration

### GitHub Actions Integration
```yaml
- name: Run API Tests
  run: |
    python src/api/tests/run_tests.py --all --coverage
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: src/api/tests/reports/coverage_full.xml
```

### Docker Testing
```dockerfile
# Run tests in container
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r src/api/tests/requirements-test.txt
CMD ["python", "src/api/tests/run_tests.py", "--all"]
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/snowflake"
```

**Missing Dependencies**
```bash
# Install all test dependencies
python src/api/tests/run_tests.py --install-deps
```

**Slow Tests**
```bash
# Run without stress tests
python src/api/tests/run_tests.py --all --no-stress
```

**Mock Failures**
Check that service mocks are properly configured in `conftest.py`.

## Contributing

### Adding New Tests

1. **Integration Tests**: Add to `test_scene_engine_integration.py`
2. **Performance Tests**: Add to `test_scene_engine_performance.py`
3. **Test Data**: Update fixtures in `conftest.py`
4. **Documentation**: Update this README

### Test Naming Convention

```python
def test_[endpoint]_[scenario]_[expected_result]():
    """Test [description]"""
    pass

# Examples:
def test_plan_scene_proactive_success():
def test_draft_scene_invalid_card_error():
def test_triage_scene_maybe_with_redesign():
```

### Mock Service Updates

When adding new service features, update mocks in `conftest.py`:

```python
# Add new mock response attributes
mock_response.new_feature = "mock_value"
mock_service.return_value.new_method.return_value = mock_response
```

## Reports and Metrics

### HTML Reports
- Test execution results
- Coverage analysis  
- Performance benchmarks
- Error details

### JSON Exports
- Machine-readable test results
- Benchmark data
- Coverage metrics
- CI/CD integration data

### Summary Reports
- Test execution overview
- Performance metrics
- Coverage statistics  
- Recommendations

---

## TaskMaster Task 47.7 Completion

✅ **API Integration Tests**: Comprehensive endpoint testing  
✅ **Performance Tests**: Response time and load testing  
✅ **Test Infrastructure**: Fixtures, mocks, and utilities  
✅ **Test Runner**: Automated execution and reporting  
✅ **Documentation**: Complete testing guide

**Total Test Coverage**: All Scene Engine API endpoints with happy path, error cases, and performance validation.