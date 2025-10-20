"""Application configuration management."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    model_name: str = "llama2"
    embedding_model: str = "nomic-embed-text"
    
    # Chat Configuration
    max_context_messages: int = 10
    vector_store_dimension: int = 384
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Session Configuration
    session_timeout: int = 3600
    max_sessions_per_user: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL from configuration."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
