# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API is open (no authentication). For production, consider adding JWT or API key authentication.

## Response Format
All responses are in JSON format.

---

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Description:** Check the health status of all services (Redis, Ollama).

**Response (200):**
```json
{
  "status": "healthy",
  "redis": true,
  "ollama": true,
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### Session Management

#### Start Session

**Endpoint:** `POST /session/start`

**Description:** Create or retrieve a user session.

**Request Body:**
```json
{
  "user_id": "user123",
  "persona": "mental_health_nurse",
  "metadata": {
    "name": "John",
    "email": "john@example.com"
  }
}
```

**Parameters:**
- `user_id` (required): Unique user identifier
- `persona` (optional): Persona key (default: "mental_health_nurse")
- `metadata` (optional): Additional session metadata

**Response (200):**
```json
{
  "user_id": "user123",
  "persona": "mental_health_nurse",
  "message_count": 0,
  "created_at": "2024-01-01T12:00:00",
  "last_activity": "2024-01-01T12:00:00"
}
```

**Error Responses:**
- `400`: Unknown persona
- `503`: Service unavailable

---

#### Get Session History

**Endpoint:** `GET /session/{user_id}/history`

**Description:** Retrieve conversation history for a user.

**Path Parameters:**
- `user_id`: User identifier

**Response (200):**
```json
{
  "user_id": "user123",
  "message_count": 3,
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T12:00:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you today?",
      "timestamp": "2024-01-01T12:00:01",
      "metadata": {}
    }
  ]
}
```

---

#### Clear Session

**Endpoint:** `DELETE /session/{user_id}/clear`

**Description:** Clear all conversation history and session data for a user.

**Path Parameters:**
- `user_id`: User identifier

**Response (200):**
```json
{
  "status": "success",
  "message": "Session cleared for user user123"
}
```

---

### Chat

#### Send Message

**Endpoint:** `POST /chat`

**Description:** Send a message and get a response from the AI.

**Request Body:**
```json
{
  "user_id": "user123",
  "message": "I've been feeling stressed lately"
}
```

**Parameters:**
- `user_id` (required): User identifier
- `message` (required): User message text

**Response (200):**
```json
{
  "response": "I'm sorry to hear you've been feeling stressed. That's a common experience. Can you tell me a bit more about what's been causing you stress? Understanding the source can help us work together on managing it better.",
  "user_id": "user123",
  "timestamp": "2024-01-01T12:00:05",
  "tokens_used": null
}
```

**Error Responses:**
- `500`: Failed to generate response
- `503`: Service unavailable

---

### Personas

#### List Personas

**Endpoint:** `GET /personas`

**Description:** List all available personas.

**Response (200):**
```json
{
  "personas": [
    {
      "key": "mental_health_nurse",
      "name": "Clara",
      "role": "Mental Health Nurse",
      "temperature": 0.7,
      "max_tokens": 500,
      "tags": ["supportive", "empathetic", "non-judgmental", "wellness-focused"]
    },
    {
      "key": "supportive_coach",
      "name": "Alex",
      "role": "Supportive Life Coach",
      "temperature": 0.7,
      "max_tokens": 500,
      "tags": ["motivational", "practical", "encouraging", "growth-focused"]
    }
  ]
}
```

---

### Sessions

#### List Active Sessions

**Endpoint:** `GET /sessions/active`

**Description:** List all users with active sessions (admin endpoint).

**Response (200):**
```json
{
  "active_users": ["user123", "user456", "user789"],
  "count": 3
}
```

---

## WebSocket Endpoints

### Chat Streaming

**Endpoint:** `WebSocket /ws/chat/{user_id}`

**Description:** Real-time chat with streaming responses.

**Protocol:**
1. Client connects to WebSocket
2. Client sends JSON message: `{"text": "Your message"}`
3. Server streams responses as JSON chunks
4. Message types:
   - `"chunk"`: Contains response content
   - `"complete"`: Response generation finished
   - `"error"`: An error occurred

**Example Client (JavaScript):**
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat/user123");

ws.onopen = () => {
  ws.send(JSON.stringify({text: "Hello!"}));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "chunk") {
    console.log(data.content);
  } else if (data.type === "complete") {
    console.log("Done!");
  } else if (data.type === "error") {
    console.error(data.message);
  }
};
```

**Example Client (Python):**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat/user123"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"text": "Hello!"}))
        
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "chunk":
                print(data["content"], end="", flush=True)
            elif data["type"] == "complete":
                print("\nDone!")
                break

asyncio.run(chat())
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Not found
- `500`: Internal server error
- `503`: Service unavailable (Redis, Ollama, or API down)

---

## Rate Limiting
Currently no rate limiting is implemented. For production, consider adding:
- Per-user rate limits
- Per-IP rate limits
- Concurrent request limits

---

## Pagination
Currently not implemented. Conversation history returns all messages. Consider implementing pagination for large conversations.

---

## Versioning
Current API version: v1 (no explicit versioning in URL yet)

Future: Plan to add `/api/v1/` prefix for versioning support.

---

## Examples

### cURL Examples

Start a session:
```bash
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","persona":"mental_health_nurse"}'
```

Send a message:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","message":"Hello!"}'
```

Get history:
```bash
curl http://localhost:8000/session/user123/history
```

### Python Examples

See `client_example.py` for a complete working example.

---

## Interactive API Documentation

The API provides interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide a user-friendly interface to explore and test endpoints directly.
