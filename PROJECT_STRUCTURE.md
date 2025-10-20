# Project Structure Documentation

## Overview
Nono Chatbot - Multi-user conversational AI with persistent memory and customizable personas

## Directory Structure

```
nono-chat-bot/
│
├── app/                           # Main application package
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # FastAPI application (main entry point)
│   ├── ollama_client.py          # Ollama LLM integration
│   ├── memory.py                 # Memory management system
│   ├── session.py                # Session management
│   └── persona.py                # Persona/system prompt management
│
├── config/                        # Configuration files
│   ├── __init__.py               # Configuration package
│   ├── config.py                 # Settings and environment config
│   └── personas.yaml             # Persona definitions
│
├── docker/                        # Docker configuration
│   ├── Dockerfile                # FastAPI container definition
│   ├── start.sh                  # Service startup script
│   └── stop.sh                   # Service cleanup script
│
├── tests/                         # Test suite
│   ├── __init__.py               # Tests package
│   ├── conftest.py               # Pytest fixtures and configuration
│   ├── test_memory.py            # Memory management tests
│   ├── test_session.py           # Session management tests
│   ├── test_persona.py           # Persona management tests
│   └── test_api.py               # FastAPI integration tests
│
├── data/                          # Data storage (local development)
│   ├── redis_data/               # Redis persistence
│   └── ollama_data/              # Model cache
│
├── docker-compose.yml            # Multi-container orchestration
├── requirements.txt              # Python dependencies
├── .env.example                  # Example environment configuration
├── .gitignore                    # Git ignore patterns
├── README.md                     # Main documentation
├── API_DOCUMENTATION.md          # API endpoint documentation
├── DEPLOYMENT_GUIDE.md           # Deployment instructions
├── ARCHITECTURE.md               # System architecture details
├── client_example.py             # Python client example
├── pytest.ini                    # Pytest configuration
└── PROJECT_STRUCTURE.md          # This file
```

## Key Files

### Application Files
- **app/main.py** - FastAPI application with all endpoints
- **app/ollama_client.py** - Interface to Ollama local LLM
- **app/memory.py** - Conversation history and context management
- **app/session.py** - User session lifecycle management
- **app/persona.py** - Persona loading and system prompt management

### Configuration Files
- **config/config.py** - Environment variable management using Pydantic
- **config/personas.yaml** - Persona definitions with system prompts
- **.env.example** - Template for environment variables

### Docker & Deployment
- **docker-compose.yml** - Orchestrates FastAPI, Redis, and Ollama containers
- **docker/Dockerfile** - FastAPI application container
- **docker/start.sh** - Script to start all services
- **docker/stop.sh** - Script to stop services

### Documentation
- **README.md** - Quick start and usage guide
- **API_DOCUMENTATION.md** - Complete API reference
- **DEPLOYMENT_GUIDE.md** - Deployment instructions for various environments
- **ARCHITECTURE.md** - System design and architecture

### Testing
- **tests/** - Complete test suite with unit and integration tests
- **pytest.ini** - Pytest configuration
- **client_example.py** - Example client for testing

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.104+ |
| ASGI Server | Uvicorn | 0.24+ |
| Database/Cache | Redis | 7+ |
| LLM Runtime | Ollama | Latest |
| Message Encoding | Pydantic | 2.5+ |
| Async Support | asyncio | Built-in |
| Testing | pytest | 7.4+ |
| Containerization | Docker | 20+ |
| Orchestration | Docker Compose | 3.8+ |

## Core Features

### 1. Multi-User Session Management
- Independent user sessions via `user_id`
- Session persistence in Redis
- Automatic session cleanup on timeout
- Session metadata storage

### 2. Conversation Memory
- Short-term buffer memory (recent messages)
- Persistent message storage in Redis
- Context window for LLM prompts
- Message retrieval and history access

### 3. Persona System
- Multiple AI personalities
- System prompt injection
- Customizable temperature and token limits
- YAML-based persona configuration

### 4. LLM Integration
- Local Ollama model support
- Multiple model availability
- Streaming response generation
- Health checks and error handling

### 5. API Endpoints
- REST API for chat and session management
- WebSocket support for streaming responses
- Health check endpoint
- Session and persona management endpoints

## Data Models

### Session Data
```
session:{user_id}
├── user_id: str
├── persona: str
├── created_at: datetime
├── last_activity: datetime
├── message_count: int
└── metadata: dict
```

### Chat History
```
chat:{user_id}:history
└── List of messages:
    ├── role: "user" | "assistant"
    ├── content: str
    ├── timestamp: datetime
    └── metadata: dict
```

### Metadata Storage
```
chat:{user_id}:metadata
├── persona: str
├── session_started: datetime
└── custom_fields: dict
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/session/start` | Start new session |
| POST | `/chat` | Send message |
| GET | `/session/{user_id}/history` | Get conversation history |
| DELETE | `/session/{user_id}/clear` | Clear session |
| GET | `/personas` | List personas |
| GET | `/sessions/active` | List active sessions |
| WS | `/ws/chat/{user_id}` | WebSocket chat stream |

## Environment Variables

Key configuration variables:
- `FASTAPI_HOST` - API server host
- `FASTAPI_PORT` - API server port
- `REDIS_HOST` - Redis server hostname
- `REDIS_PORT` - Redis server port
- `OLLAMA_HOST` - Ollama API URL
- `MODEL_NAME` - LLM model to use
- `MAX_CONTEXT_MESSAGES` - Message buffer size
- `SESSION_TIMEOUT` - Session expiry time
- `LOG_LEVEL` - Logging level

## Deployment Scenarios

1. **Local Development** - Docker Compose with hot reload
2. **Docker Compose** - Production-ready single-machine setup
3. **Cloud (AWS/Azure/GCP)** - EC2, App Service, Cloud Run
4. **Kubernetes** - Multi-container orchestration
5. **GPU-Accelerated** - Faster LLM inference

## Testing Strategy

- **Unit Tests** - Memory, session, and persona managers
- **Integration Tests** - API endpoints and full workflows
- **Mock Services** - Redis, Ollama for isolated testing
- **Coverage** - Target >80% code coverage

## Performance Characteristics

- **Memory**: ~2GB for API + Redis + Ollama base
- **Latency**: 1-30 seconds depending on model and message length
- **Throughput**: 5-10 concurrent users on standard server
- **GPU Support**: 5-50x faster with NVIDIA GPU

## Security Considerations

- **Authentication**: Currently open (add JWT for production)
- **HTTPS**: Use reverse proxy (Nginx) with SSL/TLS
- **Rate Limiting**: Not implemented (add for production)
- **Data Privacy**: Consider encryption for Redis
- **Access Control**: Restrict API and Redis ports

## Monitoring & Logging

- JSON structured logging for all operations
- Health check endpoints for service verification
- Container health checks configured
- Optional Prometheus metrics integration
- Log aggregation support

## Dependencies

See `requirements.txt` for:
- Core: FastAPI, Uvicorn, Redis, LangChain
- Data: Pydantic, PyYAML
- Optional: Pytest, pytest-asyncio
- Testing: pytest-cov

## Future Enhancements

- [ ] PostgreSQL for long-term storage
- [ ] Advanced RAG capabilities
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Fine-tuning pipeline
- [ ] Mobile app integration
- [ ] Analytics dashboard
- [ ] Advanced security (OAuth, SAML)

## Contributing

1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Follow PEP 8 style guide
5. Use type hints

## Support & Documentation

- API Docs: http://localhost:8000/docs
- README: Main usage guide
- API_DOCUMENTATION.md: Endpoint details
- DEPLOYMENT_GUIDE.md: Deployment instructions
- Client Example: client_example.py

---

*Last Updated: 2024*
*Project Version: 0.1.0*
