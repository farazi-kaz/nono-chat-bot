"""Session management for multi-user chatbot."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from redis import Redis
import json

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions with timeout and context."""
    
    def __init__(self, redis_client: Redis, session_timeout: int = 3600):
        """Initialize session manager.
        
        Args:
            redis_client: Redis client instance
            session_timeout: Session timeout in seconds (default 1 hour)
        """
        self.redis = redis_client
        self.session_timeout = session_timeout
    
    def create_session(
        self,
        user_id: str,
        persona: str = "mental_health_nurse",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create new session for user.
        
        Args:
            user_id: Unique user identifier
            persona: Persona/role for the conversation
            metadata: Optional additional session metadata
            
        Returns:
            Session information
        """
        session_data = {
            "user_id": user_id,
            "persona": persona,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "message_count": 0,
            "metadata": metadata or {}
        }
        
        session_key = f"session:{user_id}"
        self.redis.setex(
            session_key,
            self.session_timeout,
            json.dumps(session_data)
        )
        
        logger.info(f"Created session for user {user_id} with persona {persona}")
        return session_data
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data or None if not found
        """
        session_key = f"session:{user_id}"
        session_data = self.redis.get(session_key)
        
        if session_data:
            try:
                return json.loads(session_data)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode session for user {user_id}")
                return None
        
        return None
    
    def update_session(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data.
        
        Args:
            user_id: User identifier
            updates: Dictionary of updates
            
        Returns:
            True if successful, False otherwise
        """
        session_data = self.get_session(user_id)
        if not session_data:
            return False
        
        session_data.update(updates)
        session_data["last_activity"] = datetime.utcnow().isoformat()
        
        session_key = f"session:{user_id}"
        self.redis.setex(
            session_key,
            self.session_timeout,
            json.dumps(session_data)
        )
        
        return True
    
    def extend_session(self, user_id: str) -> bool:
        """Extend session expiry time.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        session_key = f"session:{user_id}"
        session_exists = self.redis.expire(session_key, self.session_timeout)
        return session_exists > 0
    
    def delete_session(self, user_id: str) -> None:
        """Delete user session.
        
        Args:
            user_id: User identifier
        """
        session_key = f"session:{user_id}"
        self.redis.delete(session_key)
        logger.info(f"Deleted session for user {user_id}")
    
    def get_session_ttl(self, user_id: str) -> int:
        """Get remaining session TTL in seconds.
        
        Args:
            user_id: User identifier
            
        Returns:
            TTL in seconds, -1 if not found, -2 if no expiry
        """
        session_key = f"session:{user_id}"
        return self.redis.ttl(session_key)
    
    def list_active_sessions(self) -> list:
        """List all active sessions.
        
        Returns:
            List of user IDs with active sessions
        """
        cursor = 0
        active_users = []
        
        while True:
            cursor, keys = self.redis.scan(cursor, match="session:*")
            for key in keys:
                user_id = key.decode().replace("session:", "")
                active_users.append(user_id)
            
            if cursor == 0:
                break
        
        return active_users
    
    def list_sessions_detailed(self) -> list:
        """List all active sessions with detailed information.
        
        Returns:
            List of session details dictionaries
        """
        cursor = 0
        sessions = []
        
        while True:
            cursor, keys = self.redis.scan(cursor, match="session:*")
            for key in keys:
                user_id = key.decode().replace("session:", "")
                session_data = self.get_session(user_id)
                if session_data:
                    # Add session_id for compatibility
                    session_data['session_id'] = f"session_{user_id}_{int(datetime.utcnow().timestamp())}"
                    sessions.append(session_data)
            
            if cursor == 0:
                break
        
        return sessions
