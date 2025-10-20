"""Persona and system prompt management."""
import logging
import yaml
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class PersonaManager:
    """Manages personas and system prompts."""
    
    def __init__(self, personas_file: str = "config/personas.yaml"):
        """Initialize persona manager.
        
        Args:
            personas_file: Path to personas YAML configuration file
        """
        self.personas_file = personas_file
        self.personas: Dict[str, Dict[str, Any]] = {}
        self._load_personas()
    
    def _load_personas(self) -> None:
        """Load personas from YAML file."""
        try:
            personas_path = Path(self.personas_file)
            if not personas_path.exists():
                logger.warning(f"Personas file not found: {self.personas_file}")
                return
            
            with open(personas_path, 'r') as f:
                config = yaml.safe_load(f) or {}
                self.personas = config.get('personas', {})
                logger.info(f"Loaded {len(self.personas)} personas")
        
        except Exception as e:
            logger.error(f"Failed to load personas: {e}")
    
    def get_persona(self, persona_key: str) -> Optional[Dict[str, Any]]:
        """Get persona configuration by key.
        
        Args:
            persona_key: Persona identifier (e.g., 'mental_health_nurse')
            
        Returns:
            Persona configuration dict or None
        """
        return self.personas.get(persona_key)
    
    def get_system_prompt(self, persona_key: str) -> str:
        """Get system prompt for persona.
        
        Args:
            persona_key: Persona identifier
            
        Returns:
            System prompt string
        """
        persona = self.get_persona(persona_key)
        if not persona:
            logger.warning(f"Persona not found: {persona_key}")
            return ""
        
        return persona.get("system_prompt", "")
    
    def get_persona_info(self, persona_key: str) -> Dict[str, Any]:
        """Get full persona information.
        
        Args:
            persona_key: Persona identifier
            
        Returns:
            Persona info including name, role, and configuration
        """
        persona = self.get_persona(persona_key)
        if not persona:
            return {}
        
        return {
            "key": persona_key,
            "name": persona.get("name", ""),
            "role": persona.get("role", ""),
            "temperature": persona.get("temperature", 0.7),
            "max_tokens": persona.get("max_tokens", 500),
            "tags": persona.get("system_tags", [])
        }
    
    def list_personas(self) -> list:
        """List all available personas.
        
        Returns:
            List of persona keys
        """
        return list(self.personas.keys())
    
    def get_default_persona(self) -> str:
        """Get default persona key.
        
        Returns:
            Default persona key (first one or 'mental_health_nurse')
        """
        if "mental_health_nurse" in self.personas:
            return "mental_health_nurse"
        if self.personas:
            return list(self.personas.keys())[0]
        return ""
