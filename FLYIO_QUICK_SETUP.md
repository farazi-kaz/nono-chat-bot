# Fly.io Deployment Checklist

## Quick Start

Follow these steps to deploy your chatbot to Fly.io:

### 1. Install Fly CLI
```powershell
curl https://fly.io/install.ps1 -o install.ps1; .\install.ps1
flyctl version
```

### 2. Login to Fly.io
```powershell
flyctl auth login
```

### 3. Initialize Fly App
```powershell
cd d:\git\test\nono-chat-bot
flyctl launch
```

When prompted:
- App name: `nono-chatbot`
- Region: Choose one closest to you (e.g., `sjc`)
- Database: **No** for PostgreSQL
- Redis: **Yes** for free Redis

### 4. Set Up Redis
```powershell
flyctl redis create --plan free
```

Copy the Redis URL provided and set it:
```powershell
flyctl secrets set REDIS_URL="redis://..."
```

### 5. Choose Your LLM Provider

**IMPORTANT:** Ollama won't work on Fly.io's free tier (needs 4GB RAM, free tier has 256MB)

Choose one of these alternatives:

#### Option A: Groq (Recommended - Fastest)
1. Sign up: https://console.groq.com
2. Get API key
3. Install: `pip install groq`
4. Set secret:
```powershell
flyctl secrets set GROQ_API_KEY="your-key"
```

#### Option B: Together AI
1. Sign up: https://together.ai
2. Get API key
3. Install: `pip install together`
4. Set secret:
```powershell
flyctl secrets set TOGETHER_API_KEY="your-key"
```

#### Option C: Hugging Face
1. Sign up: https://huggingface.co
2. Get token
3. Install: `pip install huggingface-hub`
4. Set secret:
```powershell
flyctl secrets set HUGGINGFACE_TOKEN="your-token"
```

### 6. Update Code to Use External LLM

**Modify `app/ollama_client.py`** to support your chosen provider.

Example using Groq:
```python
import os
from groq import Groq

class GroqLLM:
    def __init__(self, api_key: str = None, model: str = "mixtral-8x7b-32768"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return response.choices[0].message.content
```

Then update `app/main.py`:
```python
from app.ollama_client import GroqLLM  # Change import

@app.on_event("startup")
async def startup_event():
    global ollama_client
    
    # Use Groq instead of Ollama
    ollama_client = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
    logger.info("Groq LLM client initialized")
```

### 7. Update requirements.txt

Add the LLM provider package:

For Groq:
```
groq>=0.4.0
```

For Together AI:
```
together>=0.2.0
```

For Hugging Face:
```
huggingface-hub>=0.16.0
```

### 8. Deploy!

```powershell
flyctl deploy
```

Monitor the build:
```powershell
flyctl logs --tail 100
```

### 9. Access Your App

Once deployed, visit:
```
https://your-app-name.fly.dev
```

## Useful Commands

```powershell
# View status
flyctl status

# Check logs
flyctl logs

# View secrets
flyctl secrets list

# Update a secret
flyctl secrets set GROQ_API_KEY="new-key"

# SSH into app
flyctl ssh console

# Restart app
flyctl restart

# Scale (keep 1 VM always running for free tier)
flyctl scale vm=1

# View resource usage
flyctl status --detailed

# Destroy app (delete everything)
flyctl destroy
```

## Troubleshooting

### "Build failed"
- Check `flyctl logs` for errors
- Verify all imports in `requirements.txt`
- Ensure Dockerfile is valid

### "Out of memory"
- Free tier has 256MB RAM
- Remove unnecessary dependencies
- Use lightweight models

### "Redis connection failed"
- Verify `REDIS_URL` secret is set: `flyctl secrets list`
- Check Redis is running: `flyctl redis status`

### "LLM not responding"
- Verify API key is correct: `flyctl secrets list`
- Check service status: `flyctl logs`
- Test API key locally first

## Free Tier Limits

- **VMs**: 3 shared instances (you're using 1)
- **Memory**: 256MB per VM
- **Bandwidth**: 160GB/month
- **Storage**: 3GB persistent
- **Redis**: 100MB free

**Total Cost**: $0/month ✅

## Next Steps

1. ✅ Install Fly CLI
2. ✅ Choose LLM provider
3. ✅ Update `ollama_client.py`
4. ✅ Update `requirements.txt`
5. ✅ Deploy with `flyctl deploy`
6. ✅ Monitor with `flyctl logs`
7. ✅ Share your live URL!

Good luck! 🚀
