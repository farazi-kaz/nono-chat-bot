# Quick Start Guide - Nono Chatbot

Get up and running in 5 minutes!

## Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM available
- Ports 8000 (API), 6379 (Redis), 11434 (Ollama) free

## Step 1: Clone and Setup (1 min)

```bash
git clone <repository-url>
cd nono-chat-bot
```

## Step 2: Create Environment File (< 1 min)

```bash
cp .env.example .env
```

No changes needed for local development - defaults work out of the box!

## Step 3: Start Services (2 min)

```bash
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

Should show all services as "Up".

## Step 4: Test the API (1 min)

Visit API docs in your browser:
```
http://localhost:8000/docs
```

Or test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Start a chat session
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user1","persona":"mental_health_nurse"}'

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user1","message":"Hello!"}'
```

## Step 5: Use the Python Client (Optional)

```bash
# Install requests if not already installed
pip install requests

# Run the example
python client_example.py
```

## 🎉 You're Done!

Your multi-user chatbot is running!

## Common Commands

### View Logs
```bash
docker-compose logs -f api      # API logs
docker-compose logs -f redis    # Redis logs
docker-compose logs -f ollama   # Ollama logs
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Pull Different Model
```bash
# List available models on Ollama
curl http://localhost:11434/api/tags

# Pull a different model
docker-compose exec ollama ollama pull mistral

# Update .env
# MODEL_NAME=mistral

# Restart API
docker-compose restart api
```

## Next Steps

1. **Read the README** - `README.md` for full documentation
2. **Explore API Docs** - http://localhost:8000/docs
3. **Check Examples** - `client_example.py` for Python client usage
4. **Customize Personas** - Edit `config/personas.yaml`
5. **Deploy to Cloud** - See `DEPLOYMENT_GUIDE.md`

## Troubleshooting

**Services won't start?**
```bash
# Check what's using the ports
lsof -i :8000      # macOS/Linux
netstat -ano | grep 8000  # Windows

# Restart Docker
docker-compose down -v
docker-compose up -d
```

**API not responding?**
```bash
# Check API container logs
docker-compose logs api

# Restart API
docker-compose restart api
```

**Ollama too slow?**
- Use a smaller model: `mistral` instead of `llama2`
- Update `.env`: `MODEL_NAME=mistral`
- For GPU support, see `DEPLOYMENT_GUIDE.md`

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check service health |
| `/session/start` | POST | Start chat session |
| `/chat` | POST | Send message |
| `/personas` | GET | List personalities |
| `/session/{id}/history` | GET | View conversation |
| `/docs` | GET | Interactive API docs |

## Available Personas

- **mental_health_nurse** (Clara) - Compassionate listener and support
- **supportive_coach** (Alex) - Motivating coach

Add more in `config/personas.yaml`!

---

**Need help?**
- Check README.md for detailed documentation
- Review client_example.py for usage patterns
- Check container logs: `docker-compose logs -f`
- Read API_DOCUMENTATION.md for endpoint details

**Happy chatting! 💬**
