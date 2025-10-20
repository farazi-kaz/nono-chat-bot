"""Integration tests for FastAPI endpoints."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


# Mock imports before creating app
with patch('app.main.Redis'):
    with patch('app.main.OllamaLLM'):
        with patch('app.main.SessionManager'):
            with patch('app.main.PersonaManager'):
                from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


def test_list_personas_endpoint(client):
    """Test list personas endpoint."""
    with patch('app.main.persona_manager') as mock_pm:
        mock_pm.list_personas.return_value = ["mental_health_nurse", "coach"]
        mock_pm.get_persona_info.side_effect = [
            {
                "key": "mental_health_nurse",
                "name": "Clara",
                "role": "Nurse",
                "temperature": 0.7,
                "tags": ["supportive"]
            },
            {
                "key": "coach",
                "name": "Alex",
                "role": "Coach",
                "temperature": 0.6,
                "tags": ["motivational"]
            }
        ]
        
        response = client.get("/personas")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["personas"]) == 2


def test_start_session(client):
    """Test session start endpoint."""
    with patch('app.main.session_manager') as mock_sm, \
         patch('app.main.redis_client') as mock_redis, \
         patch('app.main.persona_manager') as mock_pm:
        
        mock_pm.get_persona.return_value = {"name": "Clara"}
        mock_sm.create_session.return_value = {
            "user_id": "user123",
            "persona": "mental_health_nurse",
            "created_at": "2024-01-01T00:00:00",
            "last_activity": "2024-01-01T00:00:00",
            "message_count": 0
        }
        
        payload = {
            "user_id": "user123",
            "persona": "mental_health_nurse"
        }
        
        response = client.post("/session/start", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["persona"] == "mental_health_nurse"


def test_chat_endpoint(client):
    """Test chat endpoint."""
    with patch('app.main.session_manager') as mock_sm, \
         patch('app.main.redis_client') as mock_redis, \
         patch('app.main.ollama_client') as mock_ollama, \
         patch('app.main.persona_manager') as mock_pm, \
         patch('app.main.ChatMemoryManager') as mock_memory_class:
        
        # Setup mocks
        mock_sm.get_session.return_value = {
            "user_id": "user123",
            "persona": "mental_health_nurse"
        }
        
        mock_pm.get_persona_info.return_value = {
            "temperature": 0.7,
            "max_tokens": 500
        }
        mock_pm.get_system_prompt.return_value = "You are Clara."
        
        mock_memory = MagicMock()
        mock_memory.get_context_window.return_value = ""
        mock_memory_class.return_value = mock_memory
        
        mock_ollama.generate.return_value = "Hello! I'm here to help."
        mock_redis.llen.return_value = 2
        
        payload = {
            "user_id": "user123",
            "message": "Hello"
        }
        
        response = client.post("/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert "response" in data
        assert "timestamp" in data


def test_clear_session(client):
    """Test clearing session endpoint."""
    with patch('app.main.session_manager') as mock_sm, \
         patch('app.main.redis_client') as mock_redis, \
         patch('app.main.ChatMemoryManager') as mock_memory_class:
        
        mock_memory = MagicMock()
        mock_memory_class.return_value = mock_memory
        
        response = client.delete("/session/user123/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


def test_get_history(client):
    """Test getting conversation history."""
    with patch('app.main.redis_client') as mock_redis, \
         patch('app.main.ChatMemoryManager') as mock_memory_class:
        
        mock_memory = MagicMock()
        mock_memory.get_messages.return_value = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
        mock_memory_class.return_value = mock_memory
        
        response = client.get("/session/user123/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["message_count"] == 2
        assert len(data["messages"]) == 2


def test_list_active_sessions(client):
    """Test listing active sessions."""
    with patch('app.main.session_manager') as mock_sm:
        mock_sm.list_active_sessions.return_value = ["user1", "user2", "user3"]
        
        response = client.get("/sessions/active")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["active_users"]) == 3
