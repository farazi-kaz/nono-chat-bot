# Fly.io Deployment Summary

## Files Created for Deployment

✅ **`fly.toml`** - Fly.io configuration
✅ **`Dockerfile`** - Container configuration  
✅ **`.dockerignore`** - Files to exclude from Docker build
✅ **`FLYIO_QUICK_SETUP.md`** - Quick deployment guide
✅ **`DEPLOYMENT_FLYIO.md`** - Detailed deployment guide

## What You Need to Do

### Step 1: Install Fly CLI (One-time)

```powershell
curl https://fly.io/install.ps1 -o install.ps1; .\install.ps1
```

### Step 2: Create Free Account

Go to https://fly.io and create a free account

### Step 3: Choose Your LLM Provider

Since Ollama won't work on Fly.io's free tier, pick ONE:

| Provider | Pros | Cons |
|----------|------|------|
| **Groq** | Fastest, most generous free tier | Inference only |
| **Together AI** | Good free tier, various models | Slower than Groq |
| **Hugging Face** | Many models available | Rate limited free tier |

**Recommendation: Groq** (best performance & free tier)

### Step 4: Update Your Code

Your `ollama_client.py` needs to support the chosen LLM provider instead of Ollama.

### Step 5: Deploy

```powershell
cd d:\git\test\nono-chat-bot
flyctl auth login
flyctl launch
```

Then follow the prompts.

## Why Fly.io is Better for Free Tier

| Feature | Render | Fly.io |
|---------|--------|--------|
| Free RAM | 0.5 GB | 0.25 GB × 3 VMs |
| Cold start | ~30s | ~5s |
| Auto-scaling | No | Yes |
| Always-on option | Paid | Free tier OK |
| Redis | Paid | Free tier (100MB) |
| **Best for** | Simple apps | Your chatbot |

## Key Limitations & Solutions

### ⚠️ Problem: Memory is Limited (256MB)

**Solution:**
- Use lightweight LLM API (Groq - 70B inference in <200ms)
- Optimize Python imports
- Use connection pooling for Redis

### ⚠️ Problem: Ollama Doesn't Fit

**Solution:**
- Switch to external LLM API (Groq/Together AI)
- Free tier models available
- Better performance than running locally

### ⚠️ Problem: Cold Starts

**Solution:**
- Configure `scale_to_zero = false` in `fly.toml`
- Keep 1 VM always running (within free tier limits)

## Free Tier Cost Analysis

- **Monthly cost**: $0
- **Constraints**: 
  - Max 3 shared VMs (using 1)
  - 256MB RAM each
  - 100MB Redis
  - 160GB bandwidth
  
**Your usage** = stays within free tier ✅

## Next Actions

1. **Install Fly CLI**
   ```powershell
   curl https://fly.io/install.ps1 -o install.ps1; .\install.ps1
   ```

2. **Create Fly.io account** (https://fly.io)

3. **Choose LLM provider**
   - Sign up for API key
   - Add to `requirements.txt`
   - Update `ollama_client.py`

4. **Update `requirements.txt`** with LLM provider

5. **Run deployment**
   ```powershell
   flyctl auth login
   flyctl launch
   ```

6. **Monitor live**
   ```powershell
   flyctl logs --tail
   ```

## Example: Using Groq

### Install Package
```powershell
pip install groq
```

### Update requirements.txt
```
groq>=0.4.0
```

### Update app/main.py

Replace:
```python
from app.ollama_client import OllamaLLM
```

With:
```python
from groq import Groq
```

Update startup:
```python
@app.on_event("startup")
async def startup_event():
    global ollama_client
    
    ollama_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    logger.info("Groq LLM initialized")
```

### Deploy
```powershell
flyctl deploy
```

## Estimated Timeline

- Install Fly CLI: **5 minutes**
- Create account & login: **5 minutes**
- Choose LLM provider: **5 minutes**
- Update code: **10 minutes**
- Deploy: **5 minutes**
- **Total: ~30 minutes**

## Support & Documentation

- Fly.io Docs: https://fly.io/docs/
- Redis on Fly: https://fly.io/docs/reference/redis/
- Groq Docs: https://console.groq.com/docs/speech-text
- Troubleshooting: See `FLYIO_QUICK_SETUP.md`

---

**Ready to deploy?** Start with Step 1: Install Fly CLI
