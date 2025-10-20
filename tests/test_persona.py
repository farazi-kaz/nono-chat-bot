"""Unit tests for persona management."""
import pytest
from unittest.mock import Mock, patch, mock_open
import yaml
from app.persona import PersonaManager


@pytest.fixture
def persona_config():
    """Sample persona configuration."""
    return {
        "personas": {
            "mental_health_nurse": {
                "name": "Clara",
                "role": "Mental Health Nurse",
                "system_prompt": "You are Clara, a compassionate nurse.",
                "temperature": 0.7,
                "max_tokens": 500,
                "system_tags": ["supportive", "empathetic"]
            },
            "coach": {
                "name": "Alex",
                "role": "Life Coach",
                "system_prompt": "You are Alex, a motivating coach.",
                "temperature": 0.6,
                "max_tokens": 400,
                "system_tags": ["motivational"]
            }
        }
    }


@pytest.fixture
def persona_manager(persona_config):
    """Create PersonaManager with mocked file loading."""
    with patch("builtins.open", mock_open(read_data=yaml.dump(persona_config))):
        with patch("pathlib.Path.exists", return_value=True):
            manager = PersonaManager("config/personas.yaml")
    return manager


def test_load_personas(persona_manager):
    """Test loading personas from config."""
    assert len(persona_manager.personas) == 2
    assert "mental_health_nurse" in persona_manager.personas
    assert "coach" in persona_manager.personas


def test_get_persona(persona_manager):
    """Test retrieving persona configuration."""
    persona = persona_manager.get_persona("mental_health_nurse")
    
    assert persona is not None
    assert persona["name"] == "Clara"
    assert persona["role"] == "Mental Health Nurse"


def test_get_system_prompt(persona_manager):
    """Test getting system prompt for persona."""
    prompt = persona_manager.get_system_prompt("mental_health_nurse")
    
    assert "Clara" in prompt
    assert "compassionate" in prompt


def test_get_persona_info(persona_manager):
    """Test getting full persona information."""
    info = persona_manager.get_persona_info("mental_health_nurse")
    
    assert info["key"] == "mental_health_nurse"
    assert info["name"] == "Clara"
    assert info["temperature"] == 0.7
    assert len(info["tags"]) == 2


def test_list_personas(persona_manager):
    """Test listing all available personas."""
    personas = persona_manager.list_personas()
    
    assert len(personas) == 2
    assert "mental_health_nurse" in personas
    assert "coach" in personas


def test_get_default_persona(persona_manager):
    """Test getting default persona."""
    default = persona_manager.get_default_persona()
    
    assert default == "mental_health_nurse"


def test_get_nonexistent_persona(persona_manager):
    """Test getting non-existent persona."""
    persona = persona_manager.get_persona("nonexistent")
    
    assert persona is None


def test_get_system_prompt_nonexistent(persona_manager):
    """Test getting system prompt for non-existent persona."""
    prompt = persona_manager.get_system_prompt("nonexistent")
    
    assert prompt == ""


def test_load_personas_file_not_found():
    """Test loading personas when file doesn't exist."""
    with patch("pathlib.Path.exists", return_value=False):
        manager = PersonaManager("nonexistent.yaml")
        assert len(manager.personas) == 0
