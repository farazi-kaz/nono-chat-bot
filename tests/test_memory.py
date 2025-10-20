"""Unit tests for memory management."""
import pytest
import json
from unittest.mock import Mock, MagicMock
from app.memory import ChatMemoryManager


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    return MagicMock()


@pytest.fixture
def memory_manager(mock_redis):
    """Create ChatMemoryManager instance with mock Redis."""
    return ChatMemoryManager(mock_redis, "test_user", max_messages=5)


def test_add_message(memory_manager, mock_redis):
    """Test adding a message to history."""
    memory_manager.add_message("user", "Hello!")
    
    # Verify rpush was called
    mock_redis.rpush.assert_called_once()
    args, kwargs = mock_redis.rpush.call_args
    
    assert args[0] == "chat:test_user:history"
    message_data = json.loads(args[1])
    assert message_data["role"] == "user"
    assert message_data["content"] == "Hello!"
    assert "timestamp" in message_data


def test_get_messages(memory_manager, mock_redis):
    """Test retrieving messages from history."""
    # Mock lrange to return stored messages
    test_messages = [
        json.dumps({"role": "user", "content": "Hi", "timestamp": "2024-01-01T00:00:00"}),
        json.dumps({"role": "assistant", "content": "Hello!", "timestamp": "2024-01-01T00:00:01"}),
    ]
    mock_redis.lrange.return_value = test_messages
    
    messages = memory_manager.get_messages()
    
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_clear_history(memory_manager, mock_redis):
    """Test clearing conversation history."""
    memory_manager.clear_history()
    
    mock_redis.delete.assert_called_once_with("chat:test_user:history")


def test_context_window(memory_manager, mock_redis):
    """Test formatted context window."""
    test_messages = [
        json.dumps({"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"}),
        json.dumps({"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T00:00:01"}),
    ]
    mock_redis.lrange.return_value = test_messages
    
    context = memory_manager.get_context_window()
    
    assert "User: Hello" in context
    assert "Assistant: Hi there!" in context


def test_metadata_operations(memory_manager, mock_redis):
    """Test metadata get/set operations."""
    test_metadata = {"persona": "nurse", "mood": "supportive"}
    
    # Test set
    memory_manager.set_metadata(test_metadata)
    mock_redis.set.assert_called_once()
    
    # Test get
    mock_redis.get.return_value = json.dumps(test_metadata)
    metadata = memory_manager.get_metadata()
    
    assert metadata["persona"] == "nurse"
    assert metadata["mood"] == "supportive"


def test_session_info(memory_manager, mock_redis):
    """Test getting complete session information."""
    test_messages = [
        json.dumps({"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"})
    ]
    mock_redis.lrange.return_value = test_messages
    mock_redis.get.return_value = json.dumps({"persona": "nurse"})
    mock_redis.llen.return_value = 1
    
    info = memory_manager.get_session_info()
    
    assert info["user_id"] == "test_user"
    assert len(info["messages"]) == 1
    assert info["metadata"]["persona"] == "nurse"
    assert info["message_count"] == 1
