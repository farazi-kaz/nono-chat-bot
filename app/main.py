"""FastAPI application and route handlers."""
import logging
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis

from config.config import settings
from app.ollama_client import OllamaLLM
from app.memory import ChatMemoryManager
from app.session import SessionManager
from app.persona import PersonaManager

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nono Chatbot API",
    description="Multi-user conversational AI with memory and persona",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
redis_client: Optional[Redis] = None
ollama_client: Optional[OllamaLLM] = None
session_manager: Optional[SessionManager] = None
persona_manager: Optional[PersonaManager] = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    global redis_client, ollama_client, session_manager, persona_manager
    
    try:
        # Connect to Redis
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    try:
        # Initialize Ollama client
        ollama_client = OllamaLLM(settings.ollama_host, settings.model_name)
        if not ollama_client.health_check():
            logger.warning("Ollama service not responding, but continuing startup")
        else:
            logger.info(f"Connected to Ollama: {settings.model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama: {e}")
        raise
    
    # Initialize session manager
    session_manager = SessionManager(redis_client, settings.session_timeout)
    logger.info("Session manager initialized")
    
    # Initialize persona manager
    persona_manager = PersonaManager("config/personas.yaml")
    logger.info(f"Loaded {len(persona_manager.list_personas())} personas")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    if redis_client:
        redis_client.close()
        logger.info("Closed Redis connection")


# ============================================================================
# Data Models
# ============================================================================

class ChatRequest(BaseModel):
    """User message request."""
    message: str
    user_id: str


class ChatResponse(BaseModel):
    """Assistant response."""
    response: str
    user_id: str
    timestamp: str
    tokens_used: Optional[int] = None


class SessionStart(BaseModel):
    """Session initialization request."""
    user_id: str
    persona: str = "mental_health_nurse"
    metadata: Optional[dict] = None


class SessionInfo(BaseModel):
    """Session information."""
    user_id: str
    persona: str
    message_count: int
    created_at: str
    last_activity: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    redis: bool
    ollama: bool
    timestamp: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint for all services."""
    redis_ok = False
    ollama_ok = False
    
    try:
        if redis_client:
            redis_client.ping()
            redis_ok = True
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
    
    try:
        if ollama_client:
            ollama_ok = ollama_client.health_check()
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
    
    status = "healthy" if (redis_ok and ollama_ok) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        redis=redis_ok,
        ollama=ollama_ok,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/session/start", response_model=SessionInfo)
async def start_session(request: SessionStart) -> SessionInfo:
    """Start or resume user session."""
    if not session_manager or not redis_client:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    # Check if persona exists
    if not persona_manager.get_persona(request.persona):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona: {request.persona}"
        )
    
    # Create session
    session_data = session_manager.create_session(
        request.user_id,
        request.persona,
        request.metadata
    )
    
    # Initialize memory
    memory = ChatMemoryManager(redis_client, request.user_id)
    memory.set_metadata({
        "persona": request.persona,
        "session_started": datetime.utcnow().isoformat()
    })
    
    return SessionInfo(
        user_id=request.user_id,
        persona=request.persona,
        message_count=0,
        created_at=session_data["created_at"],
        last_activity=session_data["last_activity"]
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send message and get response."""
    if not session_manager or not redis_client or not ollama_client or not persona_manager:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    # Get or create session
    session_data = session_manager.get_session(request.user_id)
    if not session_data:
        # Auto-create session if doesn't exist
        session_data = session_manager.create_session(
            request.user_id,
            "mental_health_nurse"
        )
    
    persona_key = session_data.get("persona", "mental_health_nurse")
    persona_info = persona_manager.get_persona_info(persona_key)
    system_prompt = persona_manager.get_system_prompt(persona_key)
    
    # Get memory
    memory = ChatMemoryManager(redis_client, request.user_id)
    memory.add_message("user", request.message)
    
    # Build context
    context = memory.get_context_window()
    
    # Prepare prompt for LLM
    if context:
        full_prompt = f"{context}\n\nUser: {request.message}\nAssistant:"
    else:
        full_prompt = f"User: {request.message}\nAssistant:"
    
    try:
        # Generate response
        response_text = ollama_client.generate(
            prompt=full_prompt,
            system=system_prompt,
            temperature=persona_info.get("temperature", 0.7),
            max_tokens=persona_info.get("max_tokens", 500)
        )
        
        # Store response
        memory.add_message("assistant", response_text)
        
        # Update session
        session_manager.update_session(request.user_id, {
            "message_count": memory.redis.llen(memory.history_key) // 2
        })
        
        return ChatResponse(
            response=response_text,
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@app.get("/session/{user_id}/history")
async def get_history(user_id: str):
    """Get conversation history for user."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    memory = ChatMemoryManager(redis_client, user_id)
    messages = memory.get_messages()
    
    return {
        "user_id": user_id,
        "message_count": len(messages),
        "messages": messages
    }


@app.delete("/session/{user_id}/clear")
async def clear_session(user_id: str):
    """Clear user session and history."""
    if not session_manager or not redis_client:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    # Clear memory
    memory = ChatMemoryManager(redis_client, user_id)
    memory.clear_history()
    
    # Delete session
    session_manager.delete_session(user_id)
    
    return {"status": "success", "message": f"Session cleared for user {user_id}"}


@app.get("/personas")
async def list_personas():
    """List available personas."""
    if not persona_manager:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    personas = persona_manager.list_personas()
    persona_details = [
        persona_manager.get_persona_info(p) for p in personas
    ]
    
    return {"personas": persona_details}


@app.get("/sessions/active")
async def list_active_sessions():
    """List all active user sessions."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    active_users = session_manager.list_active_sessions()
    return {"active_users": active_users, "count": len(active_users)}


# ============================================================================
# WebSocket Endpoints (Optional Streaming)
# ============================================================================

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for streaming responses."""
    if not session_manager or not redis_client or not ollama_client or not persona_manager:
        await websocket.close(code=1008, reason="Service unavailable")
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Get session and memory
            session_data = session_manager.get_session(user_id)
            if not session_data:
                await websocket.send_json({
                    "type": "error",
                    "message": "Session not found"
                })
                continue
            
            persona_key = session_data.get("persona", "mental_health_nurse")
            persona_info = persona_manager.get_persona_info(persona_key)
            system_prompt = persona_manager.get_system_prompt(persona_key)
            
            memory = ChatMemoryManager(redis_client, user_id)
            memory.add_message("user", message.get("text", ""))
            
            # Build context
            context = memory.get_context_window()
            if context:
                full_prompt = f"{context}\n\nUser: {message.get('text', '')}\nAssistant:"
            else:
                full_prompt = f"User: {message.get('text', '')}\nAssistant:"
            
            # Stream response
            try:
                for chunk in ollama_client.generate_stream(
                    prompt=full_prompt,
                    system=system_prompt,
                    temperature=persona_info.get("temperature", 0.7),
                    max_tokens=persona_info.get("max_tokens", 500)
                ):
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk
                    })
                
                # Collect full response
                response_text = ""
                for chunk in ollama_client.generate_stream(
                    prompt=full_prompt,
                    system=system_prompt,
                    temperature=persona_info.get("temperature", 0.7),
                    max_tokens=persona_info.get("max_tokens", 500)
                ):
                    response_text += chunk
                
                memory.add_message("assistant", response_text)
                
                await websocket.send_json({
                    "type": "complete",
                    "response": response_text
                })
            
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.fastapi_host, port=settings.fastapi_port)
