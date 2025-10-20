# Code Changes for Groq LLM Integration

This file shows the exact changes needed to support Groq instead of Ollama for Fly.io deployment.

## 1. Update `requirements.txt`

Add this line:

```txt
groq>=0.4.0
```

Full updated requirements.txt:
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
redis==5.0.1
langchain==0.1.3
langchain-community>=0.0.14
pydantic==2.5.0
pydantic-settings==2.1.0
requests==2.31.0
httpx>=0.27.0
aioredis==2.0.1
groq>=0.4.0
pyyaml==6.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
python-multipart==0.0.6
websockets==12.0
```

## 2. Create or Update `app/groq_client.py`

```python
"""Groq LLM client for Fly.io deployment."""
import os
import logging
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)


class GroqLLM:
    """Groq LLM client wrapper."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "mixtral-8x7b-32768"
    ):
        """Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not provided. Set environment variable or pass api_key."
            )
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        logger.info(f"Groq LLM initialized with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate response from Groq.
        
        Args:
            prompt: User prompt
            system_prompt: System message to provide context
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0-1)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ):
        """Stream response from Groq.
        
        Args:
            prompt: User prompt
            system_prompt: System message
            max_tokens: Maximum tokens
            temperature: Temperature
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise
```

## 3. Update `app/main.py`

Change the imports section (around line 12):

```python
# OLD:
from app.ollama_client import OllamaLLM

# NEW:
from app.groq_client import GroqLLM
```

Update the startup event (around line 60-85):

```python
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    global redis_client, ollama_client, session_manager, persona_manager
    
    # Initialize Redis
    try:
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize Groq LLM (instead of Ollama)
    try:
        ollama_client = GroqLLM(
            api_key=os.getenv("GROQ_API_KEY"),
            model=settings.model_name or "mixtral-8x7b-32768"
        )
        logger.info("Groq LLM initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Groq LLM: {e}")
        logger.warning("Continuing without LLM - chat functionality may be limited")
        ollama_client = None
    
    # Initialize session manager
    session_manager = SessionManager(redis_client, settings.session_timeout)
    logger.info("Session manager initialized")
    
    # Initialize persona manager
    persona_manager = PersonaManager("config/personas.yaml")
    logger.info(f"Loaded {len(persona_manager.list_personas())} personas")
```

## 4. Update Environment Variables

When deploying with Fly.io, set this secret:

```powershell
flyctl secrets set GROQ_API_KEY="your-groq-api-key-here"
```

Get your Groq API key from: https://console.groq.com/keys

## 5. Test Locally (Optional)

Before deploying, test with Groq locally:

```powershell
# Set environment variable
$env:GROQ_API_KEY = "your-api-key"

# Install package
pip install groq

# Test
python -c "
from app.groq_client import GroqLLM
llm = GroqLLM(model='mixtral-8x7b-32768')
response = llm.generate('Hello, how are you?')
print(response)
"
```

## 6. Deploy to Fly.io

```powershell
cd d:\git\test\nono-chat-bot
flyctl auth login
flyctl launch
flyctl secrets set GROQ_API_KEY="your-key"
flyctl deploy
```

## Available Groq Models

- `mixtral-8x7b-32768` - Fast, powerful, 32K context
- `llama2-70b-4096` - Most accurate, 4K context
- `gemma-7b-it` - Fast inference, 8K context

Groq is **extremely fast** (~200ms for 70B model) because it uses special inference hardware.

## No Code Changes Needed If Using Ollama Locally

This guide is only for **Fly.io deployment**. If you want to keep using Ollama locally for development, you can:

1. Keep both files: `app/ollama_client.py` and `app/groq_client.py`
2. Use Ollama locally with environment variable:
   ```python
   if os.getenv("USE_GROQ"):
       llm = GroqLLM()
   else:
       llm = OllamaLLM()
   ```
3. Set `USE_GROQ=true` only in Fly.io deployment

This way you can test both locally!
