"""Memory management with LangChain and Redis."""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from redis import Redis
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger(__name__)


class ChatMemoryManager:
    """Manages conversation history and context using Redis."""
    
    def __init__(self, redis_client: Redis, user_id: str, max_messages: int = 10, session_id: Optional[str] = None):
        """Initialize memory manager for a user.
        
        Args:
            redis_client: Redis client instance
            user_id: Unique user identifier
            max_messages: Maximum number of messages to keep in buffer
            session_id: Optional session identifier (if provided, memory is keyed by session)
        """
        self.redis = redis_client
        self.user_id = user_id
        self.session_id = session_id
        self.max_messages = max_messages
        
        # Redis key prefixes - use session_id if provided for session-specific memory
        # Otherwise fall back to user_id for backward compatibility
        memory_key = session_id if session_id else user_id
        self.history_key = f"chat:{memory_key}:history"
        self.metadata_key = f"chat:{memory_key}:metadata"
        self.session_key = f"chat:{memory_key}:session"
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to conversation history.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata about the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store as JSON in Redis list
        self.redis.rpush(self.history_key, json.dumps(message))
        
        # Trim to max messages
        list_length = self.redis.llen(self.history_key)
        if list_length > self.max_messages:
            self.redis.ltrim(self.history_key, list_length - self.max_messages, -1)
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve recent messages from history.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        count = limit or self.max_messages
        
        messages_raw = self.redis.lrange(self.history_key, -count, -1)
        messages = []
        
        for msg_json in messages_raw:
            try:
                msg = json.loads(msg_json)
                messages.append(msg)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to decode message: {e}")
        
        return messages
    
    def get_langchain_messages(self, limit: Optional[int] = None) -> List[BaseMessage]:
        """Get messages in LangChain format.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of LangChain Message objects
        """
        messages = self.get_messages(limit)
        langchain_messages = []
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        return langchain_messages
    
    def clear_history(self) -> None:
        """Clear all conversation history for user."""
        self.redis.delete(self.history_key)
        logger.info(f"Cleared conversation history for user: {self.user_id}")
    
    def get_context_window(self) -> str:
        """Get formatted context window for LLM prompt.
        
        Returns:
            Formatted string with recent conversation history
        """
        messages = self.get_messages()
        if not messages:
            return ""
        
        context_lines = []
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Store session metadata.
        
        Args:
            metadata: Metadata dictionary to store
        """
        current = self.get_metadata()
        current.update(metadata)
        self.redis.set(self.metadata_key, json.dumps(current))
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retrieve session metadata.
        
        Returns:
            Metadata dictionary
        """
        data = self.redis.get(self.metadata_key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get complete session information.
        
        Returns:
            Session info including messages and metadata
        """
        return {
            "user_id": self.user_id,
            "messages": self.get_messages(),
            "metadata": self.get_metadata(),
            "message_count": self.redis.llen(self.history_key)
        }
    
    def delete_session(self) -> None:
        """Delete all session data for user."""
        self.redis.delete(self.history_key)
        self.redis.delete(self.metadata_key)
        self.redis.delete(self.session_key)
        logger.info(f"Deleted session for user: {self.user_id}")
