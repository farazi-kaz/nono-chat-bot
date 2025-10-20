"""Test configuration and fixtures."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_redis():
    """Create mock Redis client for testing."""
    return MagicMock()


@pytest.fixture
def mock_ollama():
    """Create mock Ollama client for testing."""
    return MagicMock()


@pytest.fixture
def mock_session_manager():
    """Create mock session manager for testing."""
    return MagicMock()


@pytest.fixture
def mock_persona_manager():
    """Create mock persona manager for testing."""
    return MagicMock()
