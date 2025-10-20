"""Unit tests for session management."""
import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock
from app.session import SessionManager


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    return MagicMock()


@pytest.fixture
def session_manager(mock_redis):
    """Create SessionManager instance."""
    return SessionManager(mock_redis, session_timeout=3600)


def test_create_session(session_manager, mock_redis):
    """Test creating a new session."""
    session_data = session_manager.create_session(
        "user123",
        "mental_health_nurse",
        {"test": "data"}
    )
    
    assert session_data["user_id"] == "user123"
    assert session_data["persona"] == "mental_health_nurse"
    assert session_data["message_count"] == 0
    assert session_data["metadata"]["test"] == "data"
    
    # Verify Redis call
    mock_redis.setex.assert_called_once()


def test_get_session(session_manager, mock_redis):
    """Test retrieving an existing session."""
    test_session = {
        "user_id": "user123",
        "persona": "mental_health_nurse",
        "message_count": 5
    }
    mock_redis.get.return_value = json.dumps(test_session)
    
    session = session_manager.get_session("user123")
    
    assert session["user_id"] == "user123"
    assert session["message_count"] == 5


def test_get_session_not_found(session_manager, mock_redis):
    """Test getting non-existent session."""
    mock_redis.get.return_value = None
    
    session = session_manager.get_session("nonexistent")
    
    assert session is None


def test_update_session(session_manager, mock_redis):
    """Test updating session data."""
    test_session = {
        "user_id": "user123",
        "persona": "mental_health_nurse",
        "message_count": 5
    }
    mock_redis.get.return_value = json.dumps(test_session)
    
    result = session_manager.update_session("user123", {"message_count": 6})
    
    assert result is True
    mock_redis.setex.assert_called_once()


def test_extend_session(session_manager, mock_redis):
    """Test extending session expiry."""
    mock_redis.expire.return_value = 1
    
    result = session_manager.extend_session("user123")
    
    assert result is True
    mock_redis.expire.assert_called_once_with("session:user123", 3600)


def test_delete_session(session_manager, mock_redis):
    """Test deleting a session."""
    session_manager.delete_session("user123")
    
    mock_redis.delete.assert_called_once_with("session:user123")


def test_get_session_ttl(session_manager, mock_redis):
    """Test getting session TTL."""
    mock_redis.ttl.return_value = 3000
    
    ttl = session_manager.get_session_ttl("user123")
    
    assert ttl == 3000
    mock_redis.ttl.assert_called_once_with("session:user123")


def test_list_active_sessions(session_manager, mock_redis):
    """Test listing active sessions."""
    # Mock scan results
    mock_redis.scan.side_effect = [
        (0, [b"session:user1", b"session:user2"])
    ]
    
    active_users = session_manager.list_active_sessions()
    
    assert len(active_users) == 2
    assert "user1" in active_users
    assert "user2" in active_users
