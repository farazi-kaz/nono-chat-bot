# Fly.io Deployment Guide

This guide covers deploying the Nono Chatbot to Fly.io using the free tier.

## Prerequisites

- [Fly CLI installed](https://fly.io/docs/getting-started/installing-flyctl/)
- GitHub account (optional, for CI/CD)
- Free Fly.io account (https://fly.io)

## Step 1: Install Fly CLI

### Windows (PowerShell)
```powershell
curl https://fly.io/install.ps1 -o install.ps1; .\install.ps1
```

### macOS/Linux
```bash
curl -L https://fly.io/install.sh | sh
```

Verify installation:
```powershell
flyctl version
```

## Step 2: Authenticate with Fly.io

```powershell
flyctl auth login
```

This opens a browser to authenticate your account.

## Step 3: Initialize the Application

From the project root:

```powershell
flyctl launch
```

When prompted:
- **App name**: `nono-chatbot` (or your preferred name)
- **Select region**: Choose closest to you (e.g., `sjc` for US West)
- **Would you like to set up a PostgreSQL database?**: No
- **Would you like to set up an upstash Redis database?**: Yes (for free tier)

The CLI will generate `fly.toml` (already included in this repo).

## Step 4: Create Redis Database

Create a free Redis instance on Upstash:

```powershell
flyctl redis create --plan free
```

Note the Redis URL provided. Set it as an environment variable:

```powershell
flyctl secrets set REDIS_URL="redis://your-redis-url"
```

Or manually in `fly.toml`:
```toml
[env]
  REDIS_URL = "redis://username:password@host:port"
```

## Step 5: Configure Environment Variables

```powershell
flyctl secrets set OLLAMA_HOST="http://localhost:11434"
flyctl secrets set MODEL_NAME="mistral"
flyctl secrets set LOG_LEVEL="INFO"
```

## Step 6: Handle Ollama Limitation ⚠️

**Ollama won't work on Fly.io's free tier** due to memory constraints (256MB vs 4GB required).

### Option A: Use External LLM (Recommended)

Replace Ollama with a free API service:

#### 1. **Groq (Free Tier)**
- Sign up: https://console.groq.com
- Get API key
- Set environment variable:
```powershell
flyctl secrets set GROQ_API_KEY="your-api-key"
```

#### 2. **Hugging Face Inference API**
- Create account: https://huggingface.co
- Get API token
- Set environment variable:
```powershell
flyctl secrets set HUGGINGFACE_API_KEY="your-token"
```

#### 3. **Together AI (Free)**
- Sign up: https://together.ai
- Get API key
- Set environment variable:
```powershell
flyctl secrets set TOGETHER_API_KEY="your-key"
```

### Modify `ollama_client.py`

Update your `app/ollama_client.py` to support external LLM:

```python
# Option: Use Groq instead of Ollama
from groq import Groq

class GroqLLM:
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return response.choices[0].message.content
```

Then update `app/main.py` to use the external LLM instead of Ollama.

## Step 7: Deploy

```powershell
flyctl deploy
```

This:
1. Builds Docker image
2. Pushes to Fly.io registry
3. Deploys application
4. Assigns public URL

Check deployment status:
```powershell
flyctl status
```

View logs:
```powershell
flyctl logs
```

## Step 8: Access Your Application

After deployment, your app is available at:
```
https://your-app-name.fly.dev
```

## Monitoring & Maintenance

### View Logs
```powershell
flyctl logs
```

### Scale Application
```powershell
flyctl scale vm=2  # Replicate to 2 VMs (uses free tier)
```

### Update Secrets
```powershell
flyctl secrets set KEY="value"
```

### Stop Application
```powershell
flyctl suspend
```

### Delete Application
```powershell
flyctl destroy
```

## Troubleshooting

### Application crashes on startup
```powershell
flyctl logs --tail 100
```

### Memory issues
- The free tier has 256MB RAM
- Reduce Python memory footprint
- Use lightweight LLM models

### Redis connection issues
- Verify Redis URL is set: `flyctl secrets list`
- Check Redis status: `flyctl redis status`

### Cold starts taking too long
- This is normal on free tier
- Add `scale_to_zero = false` in `fly.toml` to always keep 1 VM running

## Cost Analysis

**Free Tier Limits:**
- 3 shared VMs (currently using 1)
- 160GB/month bandwidth
- 3GB persistent storage
- Free Redis (up to 100MB)

**Estimated Cost:** $0/month (stays within free tier)

## Next Steps

1. Modify `app/ollama_client.py` to use external LLM
2. Test locally before deploying
3. Set up GitHub Actions for CI/CD (optional)
4. Monitor logs and adjust as needed

## References

- [Fly.io Docs](https://fly.io/docs/)
- [Fly.io Pricing](https://fly.io/docs/about/pricing/)
- [Redis on Fly.io](https://fly.io/docs/reference/redis/)
