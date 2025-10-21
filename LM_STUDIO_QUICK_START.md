# Quick Start: LM Studio Setup

## TL;DR - Get Running in 5 Minutes

### Step 1: Install LM Studio
- Download from https://lmstudio.ai
- Install and run the application

### Step 2: Load a Model
1. Open LM Studio
2. Click "Search" tab
3. Download a model (e.g., `Mistral 7B` or `Neural Chat`)
4. Wait for it to finish

### Step 3: Start the Server
1. Go to "Local Server" tab
2. Click "Start Server" button
3. You should see: `Server running at http://localhost:1234`

### Step 4: Run the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python -m uvicorn app.main:app --reload
```

### Step 5: Test It
```bash
# In another terminal
curl http://localhost:8000/health

# Should see:
# {"status":"healthy","redis":true,"lmstudio":true,"timestamp":"..."}
```

## Docker Setup

```bash
# Make sure LM Studio server is running first!

# Build and start
docker-compose up -d

# Check logs
docker-compose logs api
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure LM Studio server is running at localhost:1234 |
| No models available | Load a model in LM Studio UI first |
| Docker can't connect | Use `host.docker.internal:1234` on Windows/Mac |
| Port 8000 in use | `docker-compose down` or kill the process |

## Verify Everything Works

```bash
# 1. Check LM Studio health
curl http://localhost:1234/v1/models

# 2. Check API health
curl http://localhost:8000/health

# 3. Test chat API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "user_message": "Hello!",
    "persona_name": "default"
  }'
```

## Next Steps

- Read `LM_STUDIO_MIGRATION.md` for detailed information
- Check `README.md` for project overview
- See `API_DOCUMENTATION.md` for endpoint details

---

**Status**: ✅ Ollama → LM Studio Refactor Complete
