"""LM Studio LLM integration module."""
import logging
import requests
import json
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LMStudioLLM:
    """Interface for interacting with LM Studio local LLM via OpenAI-compatible API."""
    
    def __init__(self, host: str, model: str = None):
        """Initialize LM Studio LLM client.
        
        Args:
            host: URL of LM Studio service (e.g., http://localhost:1234)
            model: Name of the model to use (optional, LM Studio uses loaded model)
        """
        self.host = host.rstrip('/')
        self.model = model or "local-model"  # LM Studio doesn't require specific model name
        self.chat_completions_endpoint = f"{self.host}/v1/chat/completions"
        self.embeddings_endpoint = f"{self.host}/v1/embeddings"
        self.models_endpoint = f"{self.host}/v1/models"
        
    def health_check(self) -> bool:
        """Check if LM Studio service is available."""
        try:
            response = requests.get(f"{self.host}/v1/models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LM Studio health check failed: {e}")
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
        # Convert prompt format to chat completion format
        messages = []
        
        if system:
            messages.append({
                "role": "system",
                "content": system
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(
                self.chat_completions_endpoint,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    return choice["message"].get("content", "").strip()
                elif "text" in choice:
                    return choice["text"].strip()
            
            return ""
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LM Studio generate: {e}")
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
        # Convert prompt format to chat completion format
        messages = []
        
        if system:
            messages.append({
                "role": "system",
                "content": system
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            response = requests.post(
                self.chat_completions_endpoint,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                    
                    # Skip the [DONE] marker
                    if line_str == "data: [DONE]":
                        continue
                    
                    # Parse SSE format: "data: {json}"
                    if line_str.startswith("data: "):
                        json_str = line_str[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(json_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                choice = data["choices"][0]
                                if "delta" in choice:
                                    delta = choice["delta"]
                                    if "content" in delta:
                                        yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LM Studio generate stream: {e}")
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
                self.embeddings_endpoint,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            # OpenAI format returns embeddings in data["data"]
            if "data" in data and len(data["data"]) > 0:
                embedding_obj = data["data"][0]
                if "embedding" in embedding_obj:
                    return embedding_obj["embedding"]
            
            raise ValueError("No embeddings returned from LM Studio")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LM Studio embed: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available models on LM Studio server."""
        try:
            response = requests.get(f"{self.host}/v1/models", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("id") for model in data.get("data", [])]
            return [m for m in models if m]  # Filter out None values
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing LM Studio models: {e}")
            return []
    
    def load_model(self, model_name: str) -> bool:
        """Load a model in LM Studio.
        
        Note: LM Studio loads models via UI, not API. This method attempts to notify
        the server about the model to use.
        
        Args:
            model_name: Model name to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # LM Studio doesn't have a direct load API, but we can verify the model is available
            models = self.list_models()
            if model_name in models:
                self.model = model_name
                logger.info(f"Model set to: {model_name}")
                return True
            else:
                logger.warning(f"Model {model_name} not found in available models: {models}")
                return False
            
        except Exception as e:
            logger.error(f"Error loading LM Studio model {model_name}: {e}")
            return False
