"""Ollama LLM integration module."""
import logging
import requests
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaLLM:
    """Interface for interacting with Ollama local LLM."""
    
    def __init__(self, host: str, model: str):
        """Initialize Ollama LLM client.
        
        Args:
            host: URL of Ollama service (e.g., http://localhost:11434)
            model: Name of the model to use (e.g., llama2, mistral)
        """
        self.host = host.rstrip('/')
        self.model = model
        self.generate_endpoint = f"{self.host}/api/generate"
        self.embed_endpoint = f"{self.host}/api/embed"
        
    def health_check(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False
    ) -> str:
        """Generate text response from the model.
        
        Args:
            prompt: Input prompt for the model
            system: Optional system prompt/instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text response
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            if stream:
                return response.text
            else:
                data = response.json()
                return data.get("response", "").strip()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama generate: {e}")
            raise
    
    def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """Generate text response as a stream.
        
        Args:
            prompt: Input prompt for the model
            system: Optional system prompt/instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks as they are generated
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama generate stream: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": self.model,
            "input": text
        }
        
        try:
            response = requests.post(
                self.embed_endpoint,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            # Ollama returns embeddings in data["embeddings"]
            if "embeddings" in data and len(data["embeddings"]) > 0:
                return data["embeddings"][0]
            
            raise ValueError("No embeddings returned from Ollama")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama embed: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available models on Ollama server."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry.
        
        Args:
            model: Model name to pull
            
        Returns:
            True if successful, False otherwise
        """
        payload = {"name": model}
        
        try:
            response = requests.post(
                f"{self.host}/api/pull",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            logger.info(f"Successfully pulled model: {model}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling Ollama model {model}: {e}")
            return False
