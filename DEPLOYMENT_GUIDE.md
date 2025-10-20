# Deployment Guide

This guide covers deploying Nono Chatbot to various environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Compose (Recommended)](#docker-compose-recommended)
3. [Cloud Deployment](#cloud-deployment)
4. [Kubernetes](#kubernetes)

---

## Local Development

### Prerequisites
- Python 3.11+
- Docker (for Redis and Ollama)
- Git

### Setup Steps

```bash
# Clone repository
git clone <repo-url>
cd nono-chat-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start dependencies (Redis and Ollama)
docker-compose up redis ollama -d

# Run API
python -m uvicorn app.main:app --reload

# Access at http://localhost:8000
```

---

## Docker Compose (Recommended)

### Quick Start

```bash
# Clone and navigate
git clone <repo-url>
cd nono-chat-bot

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Configuration

Edit `.env` file to customize:
```bash
cp .env.example .env
# Edit .env with your settings
```

Key settings:
- `MODEL_NAME`: LLM model to use (llama2, mistral, etc.)
- `OLLAMA_HOST`: Ollama service URL
- `REDIS_HOST`: Redis service URL
- `SESSION_TIMEOUT`: Session expiry time in seconds

### Pulling Custom Models

```bash
# Enter Ollama container
docker-compose exec ollama bash

# Pull a model
ollama pull mistral
ollama pull neural-chat

# Exit
exit
```

### Managing Services

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Start services
docker-compose start

# Remove everything
docker-compose down

# Remove with volumes (careful!)
docker-compose down -v
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 + Docker Compose

```bash
# 1. Launch EC2 instance (t3.large or larger recommended)
# - Ubuntu 22.04 LTS
# - 8GB+ RAM
# - 50GB+ storage

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 4. Clone repository
git clone <repo-url>
cd nono-chat-bot

# 5. Configure environment
cp .env.example .env
# Edit .env for your needs

# 6. Start services
docker-compose up -d

# 7. Verify
curl http://localhost:8000/health
```

#### Option 2: ECS (Elastic Container Service)

```bash
# Build and push image to ECR
aws ecr create-repository --repository-name nono-api

aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t nono-api:latest .
docker tag nono-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nono-api:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nono-api:latest

# Create ECS task definition and service
# (Use AWS Console or AWS CLI)
```

#### Option 3: Lambda + API Gateway (Serverless)

Not recommended for this application due to:
- Long-running LLM inference
- Stateful memory requirements
- Model loading overhead

Use EC2 or ECS instead.

---

### Azure Deployment

#### Azure Container Instances (ACI)

```bash
# 1. Create resource group
az group create --name nono-rg --location eastus

# 2. Create container registry
az acr create --resource-group nono-rg \
  --name nonoacr --sku Basic

# 3. Build and push image
az acr build --registry nonoacr \
  --image nono-api:latest .

# 4. Deploy to ACI
az container create \
  --resource-group nono-rg \
  --name nono-api \
  --image nonoacr.azurecr.io/nono-api:latest \
  --cpu 2 --memory 4 \
  --registry-login-server nonoacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8000 \
  --environment-variables OLLAMA_HOST=http://ollama:11434
```

#### Azure App Service

```bash
# Using Docker container
az appservice plan create --name nono-plan \
  --resource-group nono-rg --sku B2

az webapp create --resource-group nono-rg \
  --plan nono-plan --name nono-api \
  --deployment-container-image-name nonoacr.azurecr.io/nono-api:latest
```

---

### Google Cloud Deployment

#### Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/nono-api

# Deploy
gcloud run deploy nono-api \
  --image gcr.io/PROJECT_ID/nono-api \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600
```

Note: This requires stateful storage considerations for Redis.

---

### GPU Acceleration

For faster inference, use GPU-enabled instances:

#### AWS
- Use `g3` or `g4` instance types
- Configure Ollama to use GPU

#### Azure
- Use `NC-series` or `ND-series` VMs
- Install NVIDIA drivers and CUDA

#### Google Cloud
- Use `n1-highmem-4` with Tesla T4 GPUs
- Install NVIDIA drivers and CUDA

#### Ollama GPU Setup
```bash
# Ollama automatically detects and uses GPU
# For manual configuration:
export CUDA_VISIBLE_DEVICES=0
docker-compose up -d ollama

# Check GPU usage
docker-compose exec ollama nvidia-smi
```

---

## Kubernetes

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Docker image pushed to registry

### Deployment

```bash
# Create namespace
kubectl create namespace nono-chatbot

# Create ConfigMap for personas
kubectl create configmap personas-config \
  --from-file=config/personas.yaml \
  -n nono-chatbot

# Create secrets for sensitive data
kubectl create secret generic redis-secret \
  --from-literal=password=redispass \
  -n nono-chatbot

# Deploy using manifests
kubectl apply -f k8s/redis.yaml -n nono-chatbot
kubectl apply -f k8s/ollama.yaml -n nono-chatbot
kubectl apply -f k8s/api.yaml -n nono-chatbot

# Check status
kubectl get pods -n nono-chatbot
kubectl get svc -n nono-chatbot

# Access service
kubectl port-forward svc/nono-api 8000:8000 -n nono-chatbot
```

### Example Kubernetes Manifests

Create `k8s/api.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nono-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nono-api
  template:
    metadata:
      labels:
        app: nono-api
    spec:
      containers:
      - name: api
        image: your-registry/nono-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis
        - name: OLLAMA_HOST
          value: http://ollama:11434
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: nono-api
spec:
  type: LoadBalancer
  selector:
    app: nono-api
  ports:
  - port: 8000
    targetPort: 8000
```

### Horizontal Scaling

```bash
# Scale API deployment
kubectl scale deployment nono-api --replicas=3 -n nono-chatbot

# Auto-scaling
kubectl autoscale deployment nono-api \
  --min=2 --max=5 \
  --cpu-percent=80 \
  -n nono-chatbot
```

---

## Monitoring & Logging

### Docker Compose

```bash
# View logs
docker-compose logs -f api

# Specific service logs
docker-compose logs -f redis
docker-compose logs -f ollama

# Real-time monitoring
docker stats

# Health check
curl http://localhost:8000/health
```

### Kubernetes

```bash
# View logs
kubectl logs -f deployment/nono-api -n nono-chatbot

# View pod events
kubectl describe pod <pod-name> -n nono-chatbot

# Dashboard
kubectl port-forward -n kube-system svc/kubernetes-dashboard 8443:443
```

### Prometheus Metrics (Optional)

Add to `app/main.py`:
```python
from prometheus_client import Counter, Histogram, generate_latest

chat_counter = Counter('chat_messages_total', 'Total chat messages')
chat_latency = Histogram('chat_response_seconds', 'Chat response latency')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## Production Best Practices

### Security
1. Enable HTTPS/TLS
2. Add authentication (JWT/API Key)
3. Restrict API access
4. Secure Redis with password
5. Use private subnets

### Reliability
1. Enable health checks
2. Set up auto-restart
3. Use load balancer
4. Enable redundancy
5. Regular backups

### Performance
1. Use GPU when possible
2. Cache frequently used models
3. Optimize batch processing
4. Monitor resource usage
5. Scale based on load

### Maintenance
1. Regular updates
2. Model version management
3. Log rotation
4. Database maintenance
5. Security patches

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check port conflicts
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Restart services
docker-compose restart
```

### High memory usage
```bash
# Reduce model size
export MODEL_NAME=mistral  # Smaller than llama2

# Limit context size
MAX_CONTEXT_MESSAGES=5

# Monitor
docker stats
```

### Slow responses
```bash
# Check GPU usage
docker-compose exec ollama nvidia-smi

# Enable GPU
export CUDA_VISIBLE_DEVICES=0

# Restart with GPU
docker-compose up -d ollama
```

---

## Support & Resources

- GitHub Issues
- Documentation: `/README.md`
- API Docs: `/API_DOCUMENTATION.md`
- Example Client: `/client_example.py`
