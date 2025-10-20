#!/bin/bash
# Development startup script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Nono Chatbot Stack...${NC}"

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.example${NC}"
    cp .env.example .env
fi

# Start Docker Compose
echo -e "${GREEN}Starting Docker Compose services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check Redis
echo -e "${GREEN}Checking Redis...${NC}"
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
    exit 1
fi

# Check Ollama
echo -e "${GREEN}Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${RED}✗ Ollama failed to start${NC}"
    exit 1
fi

# Check API
echo -e "${GREEN}Checking FastAPI...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ FastAPI is running${NC}"
else
    echo -e "${YELLOW}! FastAPI is starting, please wait...${NC}"
fi

echo -e "${GREEN}Nono Chatbot Stack is ready!${NC}"
echo -e "${GREEN}API available at: http://localhost:8000${NC}"
echo -e "${GREEN}API Docs at: http://localhost:8000/docs${NC}"
echo -e "${GREEN}View logs: docker-compose logs -f${NC}"
