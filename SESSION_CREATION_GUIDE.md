# Session Creation Feature Guide

## Overview
Users can now create, manage, and switch between multiple chat sessions directly from the web interface.

## Features Implemented

### 1. **Create New Session** ➕
- Click the **"➕ New"** button in the header
- Fill in optional display name and select a persona
- Click "Create Session" to start a new conversation

### 2. **Manage Sessions** 📋
- Click the **"📋 Sessions"** button to view all active sessions
- See all session details including:
  - User/Display name
  - Persona type
  - Creation time
- Click on any session to switch to it

### 3. **User Identification**
- Each user has a unique identifier displayed in the header
- Session IDs are generated with timestamps for uniqueness

### 4. **Session Persistence**
- Chat history is stored in Redis
- Sessions automatically expire after the configured timeout (default 1 hour)
- Switching between sessions preserves conversation history

---

## Frontend Components

### Header Controls
- **User ID Display**: Shows current user identifier
- **New Session Button**: Opens session creation modal
- **Sessions Management Button**: Opens sessions list modal

### Session Creation Modal
Fields:
- **Display Name** (optional): Custom name for the session
- **Persona** (required): Choose conversation style
  - Default Assistant
  - Mental Health Nurse
  - Technical Support
  - Creative Writer

### Manage Sessions Modal
- Lists all active sessions
- Current session is highlighted
- Click to switch sessions
- Shows creation timestamp

---

## API Endpoints

### Create Session
```
POST /api/session/create
Content-Type: application/json

{
  "user_id": "John Doe",
  "persona": "mental_health_nurse",
  "metadata": {
    "custom_field": "value"
  }
}

Response:
{
  "session_id": "session_John Doe_1697856000",
  "user_id": "John Doe",
  "created_at": "2024-10-20T12:00:00",
  "persona": "mental_health_nurse"
}
```

### List All Sessions
```
GET /api/sessions

Response:
{
  "sessions": [
    {
      "user_id": "John Doe",
      "persona": "mental_health_nurse",
      "session_id": "session_John Doe_1697856000",
      "created_at": "2024-10-20T12:00:00",
      "last_activity": "2024-10-20T12:15:00",
      "message_count": 5
    },
    ...
  ],
  "count": 2
}
```

### Get Session History
```
GET /api/session/{user_id}/history

Response:
{
  "user_id": "John Doe",
  "message_count": 5,
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-10-20T12:00:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2024-10-20T12:00:01",
      "metadata": {}
    }
  ]
}
```

### Clear Session
```
DELETE /api/session/{user_id}/clear

Response:
{
  "status": "success",
  "message": "Session cleared for user John Doe"
}
```

---

## Backend Implementation

### Modified Files

#### `app/main.py`
- Updated `SessionCreateRequest` model to accept `persona` and `metadata`
- Enhanced `SessionCreateResponse` to include `persona`
- Added `SessionListItem` model for session details
- Added `SessionListResponse` model for session list responses
- Updated `/api/session/create` endpoint to handle new fields
- **Added `/api/sessions` endpoint** - Lists all active sessions

#### `app/session.py`
- **Added `list_sessions_detailed()` method** - Returns full session details for all active sessions

#### `public/index.html`
- **Added Session Creation Modal** with form for user input
- **Added Manage Sessions Modal** to view and switch between sessions
- **Enhanced Header** with:
  - User ID display
  - New Session button
  - Sessions Management button
- **Updated JavaScript** to handle:
  - Modal open/close functionality
  - Session creation
  - Session switching
  - Chat history loading
  - Session list management

---

## User Workflow

### First Time Users
1. Page loads → Automatic session created
2. User is assigned random ID (e.g., "user_1697856000")
3. Welcome message displayed

### Creating New Session
1. Click "➕ New" button
2. Enter display name (optional)
3. Select persona
4. Click "Create Session"
5. Chat area clears and new session begins

### Switching Sessions
1. Click "📋 Sessions" button
2. See list of all active sessions
3. Click a session to switch to it
4. Chat history loads automatically
5. Selected session is highlighted

---

## Technical Details

### Session Storage (Redis)
- Key format: `session:{user_id}`
- TTL: Configurable (default 3600 seconds)
- Data structure:
  ```json
  {
    "user_id": "string",
    "persona": "string",
    "created_at": "ISO timestamp",
    "last_activity": "ISO timestamp",
    "message_count": number,
    "metadata": object
  }
  ```

### Chat Memory Storage (Redis)
- Key format: `chat_history:{user_id}`
- Stores conversation messages in order
- Retrieved on session switch

### Session ID Generation
```python
session_id = f"session_{user_id}_{int(datetime.utcnow().timestamp())}"
```

---

## Configuration

### Session Timeout
Set in `config/config.py`:
```python
session_timeout = 3600  # seconds (1 hour)
```

### Available Personas
Defined in `config/personas.yaml`

---

## Troubleshooting

### Sessions Not Loading
- Check Redis connection: `GET /health`
- Verify Redis is running on configured URL
- Check browser console for errors

### Session Creation Fails
- Verify API server is running
- Check `/health` endpoint
- Ensure persona exists in `personas.yaml`

### Chat History Not Loading
- Session may have expired
- Try creating a new session
- Check Redis memory usage

---

## Future Enhancements

- [ ] Session export/import functionality
- [ ] Session naming and descriptions
- [ ] Session sharing between users
- [ ] Session archiving
- [ ] Session collaboration features
- [ ] Advanced filtering and search
- [ ] Session analytics and statistics

