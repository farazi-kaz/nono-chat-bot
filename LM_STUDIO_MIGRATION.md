# Ollama to LM Studio Migration Guide

## Overview
This project has been completely refactored to use **LM Studio** instead of **Ollama** for local LLM integration.

## Key Changes

### 1. Client Module
- **Old**: `app/ollama_client.py` → `OllamaLLM` class
- **New**: `app/lmstudio_client.py` → `LMStudioLLM` class
- Both implement the same interface for drop-in compatibility

### 2. API Differences

#### Ollama
- **Port**: 11434
- **API Format**: Custom Ollama API
- **Endpoints**:
  - `/api/generate` - Text generation
  - `/api/embed` - Embeddings
  - `/api/tags` - List models
  - `/api/pull` - Download models

#### LM Studio
- **Port**: 1234 (default)
- **API Format**: OpenAI-compatible REST API (faster, more compatible)
- **Endpoints**:
  - `/v1/chat/completions` - Chat completions
  - `/v1/embeddings` - Embeddings
  - `/v1/models` - List models

### 3. Configuration Changes

**Before (config.py)**:
```python
ollama_host: str = "http://localhost:11434"
model_name: str = "llama2"
embedding_model: str = "nomic-embed-text"
```

**After (config.py)**:
```python
lmstudio_host: str = "http://localhost:1234"
model_name: str = "local-model"
embedding_model: str = "local-model"
```

### 4. Environment Variables

Update your `.env` file:

```bash
# OLD (Ollama)
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=llama2
EMBEDDING_MODEL=nomic-embed-text

# NEW (LM Studio)
LMSTUDIO_HOST=http://localhost:1234
MODEL_NAME=local-model
EMBEDDING_MODEL=local-model
```

### 5. Docker Configuration

**Ollama in docker-compose.yml** (removed):
- Separate Ollama service running in container
- Automatic model pulling via API

**LM Studio** (new):
- Runs on host machine as a desktop application
- Docker container connects to host via `host.docker.internal:1234`
- Models are loaded manually in LM Studio UI

### 6. Dependencies

**Removed**:
- `ollama>=0.2.0` package (not used)

**Maintained**:
- `requests==2.31.0` (used for HTTP calls)
- All other dependencies unchanged

## Setup Instructions

### 1. Install LM Studio
Download and install LM Studio from: https://lmstudio.ai

### 2. Load a Model
1. Open LM Studio
2. Go to "Search" tab
3. Find and download a model (e.g., Mistral, Neural Chat, etc.)
4. Wait for download to complete

### 3. Start LM Studio Server
1. Go to "Local Server" tab
2. Click "Start Server"
3. Verify it shows: `Server running at http://localhost:1234`

### 4. Run the Application

**Local Development**:
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables or use .env
export LMSTUDIO_HOST=http://localhost:1234

# Run the application
python -m uvicorn app.main:app --reload
```

**Docker**:
```bash
# Build and start with Docker Compose
docker-compose up -d

# API will automatically connect to LM Studio on host
```

## LMStudioLLM Class API

### Methods

#### `__init__(host: str, model: str = None)`
Initialize the LM Studio client.

```python
client = LMStudioLLM("http://localhost:1234")
```

#### `health_check() -> bool`
Check if LM Studio service is running.

```python
if client.health_check():
    print("LM Studio is ready!")
```

#### `generate(prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 500) -> str`
Generate a response (non-streaming).

```python
response = client.generate(
    prompt="What is Python?",
    system="You are a helpful assistant.",
    temperature=0.7,
    max_tokens=500
)
```

#### `generate_stream(prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 500)`
Generate a response as a stream.

```python
for chunk in client.generate_stream(prompt="Hello!"):
    print(chunk, end="", flush=True)
```

#### `embed(text: str) -> List[float]`
Generate embeddings for text.

```python
embedding = client.embed("The quick brown fox")
```

#### `list_models() -> List[str]`
List available models.

```python
models = client.list_models()
print(models)
```

#### `load_model(model_name: str) -> bool`
Set the active model (models must be loaded in LM Studio UI first).

```python
if client.load_model("mistral"):
    print("Model loaded!")
```

## Troubleshooting

### "Connection refused" error
- Ensure LM Studio is running and the server is started
- Check that port 1234 is not blocked
- Verify LMSTUDIO_HOST environment variable is correct

### "No models available"
- Load a model in LM Studio UI before starting the application
- Check `/v1/models` endpoint manually: `curl http://localhost:1234/v1/models`

### Docker container can't connect to LM Studio
- Ensure you're using `host.docker.internal:1234` on Windows/Mac
- On Linux, use `172.17.0.1:1234` or configure network mode
- Or run both in the same Docker network

### Streaming not working
- LM Studio uses Server-Sent Events (SSE) format
- The `generate_stream()` method handles this automatically
- Check that streaming is enabled in LM Studio settings

## Performance Comparison

| Feature | Ollama | LM Studio |
|---------|--------|-----------|
| Memory Usage | Higher (~4GB+) | Lower (~2GB+) |
| API Format | Custom | OpenAI-compatible |
| Model Management | API-based | UI-based |
| Streaming | Supported | Supported (SSE) |
| Embeddings | Supported | Supported |
| Setup Complexity | Medium | Simple |
| Desktop Integration | Limited | Excellent |

## API Health Check Response

The `/health` endpoint response has been updated:

**Old (Ollama)**:
```json
{
  "status": "healthy",
  "redis": true,
  "ollama": true,
  "timestamp": "2025-10-20T20:25:40.123456"
}
```

**New (LM Studio)**:
```json
{
  "status": "healthy",
  "redis": true,
  "lmstudio": true,
  "timestamp": "2025-10-20T20:25:40.123456"
}
```

## Reverting to Ollama

If you need to revert to Ollama:

1. Keep `app/ollama_client.py` (still in git history)
2. Update `config.py` back to Ollama settings
3. Update `main.py` imports: `from app.ollama_client import OllamaLLM`
4. Change global variable: `ollama_client: Optional[OllamaLLM] = None`
5. Restore docker-compose.yml to include Ollama service
6. Run `git checkout requirements.txt` to restore ollama package

## Files Modified

### New Files
- `app/lmstudio_client.py` - LM Studio client implementation

### Modified Files
- `app/main.py` - Updated imports and client usage
- `config/config.py` - Updated LM Studio configuration
- `docker-compose.yml` - Removed Ollama service
- `requirements.txt` - Removed ollama package
- `tests/test_api.py` - Updated mock imports
- `tests/conftest.py` - Updated fixture names

### Backward Compatibility
- `app/ollama_client.py` - Kept for reference (not imported)
- Old configuration variables kept but unused

## Support

For LM Studio support: https://lmstudio.ai/support
For this project issues: Check project repository

---

**Migration Date**: 2025-10-20
**Status**: Complete Refactor ✓
