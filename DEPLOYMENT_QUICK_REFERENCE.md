# 🚀 Fly.io Deployment - Quick Reference

## Your Deployment Path

```
┌─────────────────────────────────────────────┐
│  FastAPI Chatbot (your-app-name.fly.dev)   │
│  - 256MB RAM (free tier)                    │
│  - Auto-scaling enabled                     │
│  - Always-on (free tier)                    │
└────────────┬────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
  ┌───────┐    ┌──────────────┐
  │ Redis │    │  Groq LLM    │
  │100 MB │    │  (Free API)  │
  │(Free) │    │  Ultra-fast  │
  └───────┘    └──────────────┘
```

## 5-Step Quick Start

### 1️⃣ Install Fly CLI (5 min)
```powershell
curl https://fly.io/install.ps1 -o install.ps1; .\install.ps1
```

### 2️⃣ Create Accounts (10 min)
- Fly.io: https://fly.io (free account)
- Groq: https://console.groq.com (get API key)

### 3️⃣ Update Code (15 min)
See: `GROQ_INTEGRATION.md`

Files to create/update:
- ✅ `app/groq_client.py` (NEW)
- ✅ `requirements.txt` (add groq)
- ✅ `app/main.py` (update imports & startup)

### 4️⃣ Deploy (5 min)
```powershell
flyctl auth login
flyctl launch
flyctl secrets set GROQ_API_KEY="your-key"
flyctl deploy
```

### 5️⃣ Monitor (2 min)
```powershell
flyctl logs --tail
# Visit: https://your-app-name.fly.dev
```

**Total Time: ~45 minutes** ⏱️

---

## 📋 Configuration Files Already Created

| File | Purpose |
|------|---------|
| `fly.toml` | ✅ Fly.io settings (shared CPU, 256MB RAM, region) |
| `Dockerfile` | ✅ Container configuration |
| `.dockerignore` | ✅ Files to exclude from build |
| `FLYIO_SUMMARY.md` | 📖 Overview and LLM options |
| `FLYIO_QUICK_SETUP.md` | 📖 Step-by-step deployment |
| `DEPLOYMENT_FLYIO.md` | 📖 Detailed troubleshooting |
| `GROQ_INTEGRATION.md` | 📖 Exact code changes needed |

---

## 💰 Cost Breakdown

| Service | Free Tier | Your Usage |
|---------|-----------|-----------|
| Fly.io VMs | 3 × shared-cpu-1x 256MB | 1 VM used |
| Redis | 100MB | ~10-50MB |
| Bandwidth | 160GB/month | ~1-5GB/month |
| Groq LLM | Free tier + $5 credit | ~0.1-1 credits/month |
| **Monthly Cost** | - | **$0** ✅ |

---

## 📚 Documentation Files

### Quick References
- `FLYIO_SUMMARY.md` - Overview, cost analysis, why Fly.io
- `FLYIO_QUICK_SETUP.md` - Step-by-step deployment checklist

### Detailed Guides
- `DEPLOYMENT_FLYIO.md` - Full setup with all options (Groq, Together AI, HuggingFace)
- `GROQ_INTEGRATION.md` - Exact code changes, example code

### Troubleshooting Commands

```powershell
# View application status
flyctl status

# View live logs
flyctl logs --tail 100

# SSH into app
flyctl ssh console

# List stored secrets
flyctl secrets list

# Update a secret
flyctl secrets set KEY="new-value"

# Restart app
flyctl restart

# Scale replicas
flyctl scale vm=1

# View detailed status
flyctl status --detailed
```

---

## 🎯 What Happens During `flyctl deploy`

1. ✅ Builds Docker image from `Dockerfile`
2. ✅ Pushes image to Fly.io registry
3. ✅ Starts container with allocated resources
4. ✅ Assigns public URL (https://your-app-name.fly.dev)
5. ✅ Sets up auto-scaling & health checks
6. ✅ Routes traffic automatically

**Build time**: ~2-3 minutes
**Total deployment**: ~5 minutes

---

## 🔑 Important: Environment Variables

**Set before deployment:**

```powershell
flyctl secrets set GROQ_API_KEY="sk-..."
flyctl secrets set REDIS_URL="redis://..."  # Auto-generated
flyctl secrets set MODEL_NAME="mixtral-8x7b-32768"
flyctl secrets set LOG_LEVEL="INFO"
```

---

## ✨ Groq LLM Highlights

Why we chose Groq over alternatives:

| Feature | Groq | Together AI | HuggingFace |
|---------|------|-------------|-------------|
| Speed | ⚡ 70B in ~200ms | 🟡 1-5s | 🟡 2-10s |
| Free Tier | ⭐ Best | ⭐ Good | 🟡 Limited |
| Models | ✅ 3 great ones | ✅ Many | ✅ Many |
| Rate Limit | ✅ Generous | 🟡 Moderate | 🟡 Strict |
| **Best for** | **This project** | Budget builds | Research |

**Groq models:**
- `mixtral-8x7b-32768` (Recommended - balanced)
- `llama2-70b-4096` (Most accurate)
- `gemma-7b-it` (Fastest)

---

## 🎓 How It Works After Deployment

1. User sends message via web interface
2. FastAPI receives request
3. Session manager retrieves user context from Redis
4. Groq API generates response (via `GroqLLM` class)
5. Response stored in Redis for history
6. Response returned to user
7. All on free tier! 🎉

---

## 📞 Support & Help

### When Something Goes Wrong

```powershell
# Get last 100 lines of logs
flyctl logs --tail 100

# SSH into container to debug
flyctl ssh console

# Check if health check is passing
curl https://your-app-name.fly.dev/health

# Check resource usage
flyctl status --detailed
```

### Documentation Links

- **Fly.io Docs**: https://fly.io/docs/
- **Groq API**: https://console.groq.com/docs
- **Redis on Fly**: https://fly.io/docs/reference/redis/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## ✅ Pre-Deployment Checklist

- [ ] `fly.toml` ✅ (created)
- [ ] `Dockerfile` ✅ (created)
- [ ] `.dockerignore` ✅ (created)
- [ ] Fly CLI installed
- [ ] Fly.io account created
- [ ] Groq account & API key ready
- [ ] `app/groq_client.py` created (see GROQ_INTEGRATION.md)
- [ ] `requirements.txt` updated with `groq>=0.4.0`
- [ ] `app/main.py` updated to use Groq
- [ ] `.env` file has `GROQ_API_KEY` (for local testing)

---

## 🚀 Ready to Go?

**Start here:**

1. Read `FLYIO_SUMMARY.md` (5 min overview)
2. Follow `FLYIO_QUICK_SETUP.md` (step-by-step)
3. Use `GROQ_INTEGRATION.md` (for code changes)
4. Deploy with `flyctl deploy`
5. Check `flyctl logs`

**Questions?** See `DEPLOYMENT_FLYIO.md` troubleshooting section.

---

**Your free deployment awaits! 🎊**

Questions? Run: `flyctl help` or visit https://fly.io/docs
