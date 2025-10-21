# Bug Fix: Session Memory Isolation

## Issue
When creating a new session and sending the first message, the bot would respond as if it was continuing a previous conversation, saying things like "It seems like we're still in the 'hello' loop..."

### Root Cause
Multiple sessions for the same user were **sharing the same chat history** in Redis because:

1. The `ChatMemoryManager` was using only `user_id` as the Redis key: `chat:{user_id}:history`
2. When you created a new session, it generated a new `session_id` but extracted the same `user_id`
3. The `/api/chat` endpoint didn't pass `session_id` to `ChatMemoryManager`
4. Result: All sessions for a user shared the same memory → bot sees old conversations

**Example:**
```
Session 1: user_123_abc → Memory key: chat:user_123:history ← OLD MESSAGES HERE
Session 2: user_123_xyz → Memory key: chat:user_123:history ← SAME KEY!
```

## Solution
Changed the memory system to be **keyed by `session_id`** instead of just `user_id`:

### Changes Made

#### 1. **`app/memory.py`** - Added `session_id` parameter
```python
def __init__(self, redis_client: Redis, user_id: str, max_messages: int = 10, session_id: Optional[str] = None):
    # Use session_id if provided, otherwise fall back to user_id
    memory_key = session_id if session_id else user_id
    self.history_key = f"chat:{memory_key}:history"
```

**Result:** Each session now has isolated memory:
- Session 1: `chat:user_123_abc:history` ← Only messages from Session 1
- Session 2: `chat:user_123_xyz:history` ← Only messages from Session 2

#### 2. **`app/main.py`** - Pass `session_id` to memory manager
- Updated `/api/chat` endpoint to pass `session_id` when creating `ChatMemoryManager`
- Updated `/session/{user_id}/history` endpoint to accept `session_id` as query parameter
- Updated `/session/{user_id}/clear` endpoint to accept `session_id` for session-specific clearing

#### 3. **`public/index.html`** - Pass `session_id` to history API
- Updated `loadChatHistory()` to include `session_id` query parameter:
  ```javascript
  const response = await fetch(`${API_BASE_URL}/api/session/${userId}/history?session_id=${sessionId}`, ...);
  ```

## Testing the Fix

1. Create a new session
2. Send message: "hi"
3. Bot should respond normally without any "loop" references
4. Create another session with the same user
5. Send message: "hello"
6. Each session should have independent chat history

## Impact
- ✅ Fresh sessions start with clean memory
- ✅ Multiple sessions per user are now isolated
- ✅ No more cross-session conversation bleed
- ✅ Backward compatible (falls back to user_id if session_id not provided)

## Files Modified
1. `app/memory.py` - Added optional `session_id` parameter
2. `app/main.py` - Updated 3 endpoints to use session_id
3. `public/index.html` - Updated history API call with session_id
