# Nono Chatbot - Multi-User Conversational AI with Memory and Persona

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated multi-user chatbot system with persistent memory, customizable personas, and local LLM integration via Ollama.

## 🎯 Key Features

- **Multi-User Support**: Isolated sessions per user with independent conversation history
- **Persistent Memory**: Redis-backed storage for conversation history and context
- **Customizable Personas**: Define and switch between different AI personalities/roles
- **Local LLM Integration**: Run models locally via Ollama (no external API costs)
- **REST & WebSocket APIs**: HTTP endpoints + streaming WebSocket support
- **Hybrid Memory System**: Combines buffer memory (recent messages) with semantic retrieval
- **Docker Ready**: Complete Docker Compose setup for easy deployment
- **Production Ready**: Health checks, logging, error handling, and monitoring

## 🏗️ Architecture

```
┌─────────────────┐
│   Client/UI     │
└────────┬────────┘
         │
    HTTP/WebSocket
         │
┌────────▼─────────────────────────┐
│   FastAPI Application (Port 8000) │
│  ├─ Session Management            │
│  ├─ Conversation Routing          │
│  └─ Memory Integration            │
└────────┬──────────────┬───────────┘
         │              │
         │              │
┌────────▼────┐  ┌──────▼────────┐
│ Redis       │  │ Ollama LLM    │
│ (Port 6379) │  │ (Port 11434)  │
└─────────────┘  └───────────────┘
```

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- Ollama (for local LLM)
- 8GB+ RAM (recommended for LLM models)
- GPU support (optional, for faster inference)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd nono-chat-bot

# Create virtual environment (optional for local dev)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Configure Environment

```bash
# Copy example environment
cp .env.example .env

# Edit .env with your settings (optional)
# Default values are configured for local development
```

### 3. Start Docker Services

```bash
# Linux/Mac
chmod +x docker/start.sh
./docker/start.sh

# Windows (PowerShell)
docker-compose up -d
```

The script will:
- Start Redis (port 6379)
- Start Ollama (port 11434)
- Start FastAPI application (port 8000)
- Pull the default model (llama2) on first run

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 Usage Examples

### Starting a Session

```bash
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "persona": "mental_health_nurse",
    "metadata": {"name": "John"}
  }'
```

### Sending a Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hi, I'\''ve been feeling stressed lately"
  }'
```

### Getting Conversation History

```bash
curl http://localhost:8000/session/user123/history
```

### Listing Available Personas

```bash
curl http://localhost:8000/personas
```

### Viewing Active Sessions

```bash
curl http://localhost:8000/sessions/active
```

### Clearing a Session

```bash
curl -X DELETE http://localhost:8000/session/user123/clear
```

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FASTAPI_HOST` | `0.0.0.0` | FastAPI server host |
| `FASTAPI_PORT` | `8000` | FastAPI server port |
| `REDIS_HOST` | `redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama API URL |
| `MODEL_NAME` | `llama2` | LLM model to use |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |
| `MAX_CONTEXT_MESSAGES` | `10` | Messages to keep in memory buffer |
| `SESSION_TIMEOUT` | `3600` | Session timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `development` | Environment (development/production) |

### Personas Configuration

Edit `config/personas.yaml` to customize AI personalities:

```yaml
personas:
  your_persona:
    name: "Name"
    role: "Role"
    system_prompt: |
      Your custom system instructions...
    temperature: 0.7
    max_tokens: 500
    system_tags:
      - tag1
      - tag2
```

## 📊 Available Personas

### Mental Health Nurse (Default)
- **Name**: Clara
- **Role**: Compassionate listener and support provider
- **Features**: Empathetic, non-judgmental, wellness-focused

### Life Coach
- **Name**: Alex
- **Role**: Motivating coach and goal facilitator
- **Features**: Uplifting, practical, growth-oriented

Add more personas in `config/personas.yaml`!

## 🔄 WebSocket Streaming

For real-time streaming responses:

```python
import asyncio
import websockets
import json

async def stream_chat():
    uri = "ws://localhost:8000/ws/chat/user123"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "text": "Hello! How are you?"
        }))
        
        # Receive streamed chunks
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data["type"] == "chunk":
                print(data["content"], end="", flush=True)
            elif data["type"] == "complete":
                print("\n[Response complete]")
                break
            elif data["type"] == "error":
                print(f"Error: {data['message']}")
                break

asyncio.run(stream_chat())
```

## 📁 Project Structure

```
nono-chat-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── ollama_client.py     # Ollama LLM interface
│   ├── memory.py            # Memory management
│   ├── session.py           # Session handling
│   └── persona.py           # Persona management
├── config/
│   ├── config.py            # Configuration management
│   └── personas.yaml        # Persona definitions
├── docker/
│   ├── Dockerfile           # App container
│   ├── start.sh             # Start script
│   └── stop.sh              # Stop script
├── tests/
│   ├── test_memory.py       # Memory tests
│   ├── test_session.py      # Session tests
│   ├── test_persona.py      # Persona tests
│   └── test_api.py          # API integration tests
├── docker-compose.yml       # Multi-container orchestration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment config
└── README.md               # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_memory.py -v

# Run specific test
pytest tests/test_memory.py::test_add_message -v
```

## 🐳 Docker Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f redis
docker-compose logs -f ollama
```

### Stop Services

```bash
docker-compose down
```

### Remove Everything (including volumes)

```bash
docker-compose down -v
```

### Restart Services

```bash
docker-compose restart
```

### View Running Containers

```bash
docker-compose ps
```

## 🔍 Monitoring

### Health Endpoints

```bash
# Full health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "redis": true,
#   "ollama": true,
#   "timestamp": "2024-01-01T00:00:00"
# }
```

### Container Health

```bash
# Check container status
docker-compose ps

# View resource usage
docker stats
```

## 🚨 Troubleshooting

### Redis Connection Error

```bash
# Check Redis is running
docker-compose ps redis

# Verify connection
docker-compose exec redis redis-cli ping

# Check logs
docker-compose logs redis
```

### Ollama Not Responding

```bash
# Check Ollama container
docker-compose ps ollama

# Check Ollama API
curl http://localhost:11434/api/tags

# Pull model manually
docker-compose exec ollama ollama pull llama2

# View logs
docker-compose logs ollama
```

### API Connection Issues

```bash
# Test API health
curl http://localhost:8000/health

# Check API logs
docker-compose logs api

# Verify ports are not in use
netstat -an | grep LISTEN  # Unix
netstat -ano | findstr LISTEN  # Windows
```

### Memory Issues

```bash
# Reduce MAX_CONTEXT_MESSAGES in .env
MAX_CONTEXT_MESSAGES=5

# Restart services
docker-compose restart
```

## 📊 Performance Optimization

### For Development
- Use smaller models (e.g., `mistral`)
- Reduce `MAX_CONTEXT_MESSAGES`
- Disable unnecessary logging

### For Production
- Use GPU acceleration with Ollama
- Implement model caching
- Enable Redis persistence
- Use connection pooling
- Add reverse proxy (Nginx)
- Enable HTTPS

## 🔐 Security Considerations

1. **Authentication**: Add JWT or API key authentication
2. **HTTPS**: Use reverse proxy with SSL/TLS
3. **Rate Limiting**: Implement request throttling
4. **Input Validation**: Sanitize user inputs
5. **Data Privacy**: Encrypt sensitive data in Redis
6. **Access Control**: Restrict Ollama and Redis ports

## 🚀 Deployment

### Local Development

```bash
docker-compose up -d
```

### Cloud Deployment (e.g., AWS)

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-uri>
docker build -t <ecr-uri>/nono-api:latest .
docker push <ecr-uri>/nono-api:latest

# Deploy on ECS, EKS, or similar
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace nono-chatbot

# Deploy using Helm or kubectl
kubectl apply -f k8s/
```

## 📈 Scaling Strategies

1. **Horizontal Scaling**: Multiple API instances with load balancer
2. **Redis Clustering**: For distributed caching
3. **Model Serving**: Use TensorFlow Serving or vLLM for inference
4. **Database**: Add PostgreSQL for long-term persistence
5. **Message Queue**: Implement async task processing (Celery)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI framework
- Ollama for local LLM integration
- Redis for caching and memory
- LangChain for memory abstractions
- Docker for containerization

## 📞 Support

For issues and questions:
- Create an Issue on GitHub
- Check existing documentation
- Review test cases for usage examples

## 🗺️ Roadmap

- [ ] PostgreSQL integration for long-term storage
- [ ] Advanced analytics and mood tracking
- [ ] Multi-language support
- [ ] Voice input/output integration
- [ ] Advanced RAG (Retrieval-Augmented Generation)
- [ ] Model fine-tuning capabilities
- [ ] Dashboard UI
- [ ] Mobile app support

---

**Built with ❤️ for meaningful AI conversations**
