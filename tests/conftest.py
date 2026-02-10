"""
Root test configuration for Snowflake pipeline.

Sets mock API keys so AIGenerator.__init__() doesn't raise ValueError,
and patches AIGenerator.generate() to return mock responses instead of
making real API calls.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock


# Default mock response that satisfies Step 0 validation (most common in tests)
MOCK_STEP0_RESPONSE = json.dumps({
    "category": "Psychological Thriller",
    "story_kind": "Cat-and-mouse whodunit with unreliable narrator and conspiracy backdrop.",
    "audience_delight": "Plot twists, mind games, shocking reveal, morally grey characters, psychological tension."
})


@pytest.fixture(autouse=True, scope="session")
def mock_api_keys():
    """Set mock API keys for the entire test session."""
    os.environ['ANTHROPIC_API_KEY'] = 'test-key-mock-anthropic-12345'
    os.environ['OPENAI_API_KEY'] = 'test-key-mock-openai-67890'
    yield
    for key in ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY']:
        if key in os.environ and 'test-key-mock' in os.environ[key]:
            del os.environ[key]


@pytest.fixture(autouse=True)
def mock_ai_clients():
    """Mock AI client libraries to prevent any real API calls."""
    with patch('src.ai.generator.Anthropic') as mock_anthropic, \
         patch('src.ai.generator.OpenAI') as mock_openai:
        # Configure mock Anthropic client
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=MOCK_STEP0_RESPONSE)]
        mock_anthropic_instance.messages.create.return_value = mock_msg

        # Configure mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        mock_choice = MagicMock()
        mock_choice.message.content = MOCK_STEP0_RESPONSE
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_openai_instance.chat.completions.create.return_value = mock_completion

        yield {
            'anthropic': mock_anthropic_instance,
            'openai': mock_openai_instance,
        }
