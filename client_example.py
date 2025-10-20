"""Example client for interacting with Nono Chatbot API."""
import requests
import json
from typing import Optional, List, Dict, Any


class NonoChatbotClient:
    """Python client for Nono Chatbot API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize chatbot client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def start_session(
        self,
        user_id: str,
        persona: str = "mental_health_nurse",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Start a new conversation session.
        
        Args:
            user_id: Unique user identifier
            persona: Persona to use
            metadata: Optional session metadata
            
        Returns:
            Session information
        """
        payload = {
            "user_id": user_id,
            "persona": persona,
            "metadata": metadata or {}
        }
        
        response = requests.post(
            f"{self.base_url}/session/start",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Send a message and get response.
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            API response with assistant's message
        """
        payload = {
            "user_id": user_id,
            "message": message
        }
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_history(self, user_id: str) -> Dict[str, Any]:
        """Get conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation history
        """
        response = requests.get(f"{self.base_url}/session/{user_id}/history")
        response.raise_for_status()
        return response.json()
    
    def clear_session(self, user_id: str) -> Dict[str, Any]:
        """Clear user session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Success response
        """
        response = requests.delete(f"{self.base_url}/session/{user_id}/clear")
        response.raise_for_status()
        return response.json()
    
    def list_personas(self) -> Dict[str, Any]:
        """List available personas.
        
        Returns:
            List of personas
        """
        response = requests.get(f"{self.base_url}/personas")
        response.raise_for_status()
        return response.json()
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """List active user sessions.
        
        Returns:
            Active sessions information
        """
        response = requests.get(f"{self.base_url}/sessions/active")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the client."""
    client = NonoChatbotClient()
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"Health: {health['status']}")
    
    # Start session
    print("\nStarting session...")
    user_id = "demo_user_123"
    session = client.start_session(
        user_id,
        persona="mental_health_nurse",
        metadata={"demo": True}
    )
    print(f"Session started: {session['user_id']}")
    
    # List personas
    print("\nAvailable personas:")
    personas = client.list_personas()
    for persona in personas["personas"]:
        print(f"  - {persona['name']} ({persona['key']}): {persona['role']}")
    
    # Send messages
    messages = [
        "Hi, I've been feeling overwhelmed lately",
        "Work has been really stressful",
        "What can I do to manage stress better?"
    ]
    
    print("\n--- Conversation ---")
    for user_message in messages:
        print(f"\nYou: {user_message}")
        
        response = client.send_message(user_id, user_message)
        assistant_message = response["response"]
        
        print(f"Clara: {assistant_message}")
    
    # Get history
    print("\n--- Conversation History ---")
    history = client.get_history(user_id)
    print(f"Total messages: {history['message_count']}")
    
    for i, msg in enumerate(history["messages"], 1):
        role = "You" if msg["role"] == "user" else "Clara"
        print(f"{i}. {role}: {msg['content'][:100]}...")
    
    # List active sessions
    print("\n--- Active Sessions ---")
    active = client.list_active_sessions()
    print(f"Active users: {active['count']}")
    
    # Cleanup
    print("\nCleaning up...")
    client.clear_session(user_id)
    print("Session cleared")


if __name__ == "__main__":
    main()
