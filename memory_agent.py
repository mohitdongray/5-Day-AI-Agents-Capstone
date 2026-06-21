"""
memory_agent.py
Handles storing and retrieving user conversation history and long-term preferences.
Now with logging for observability.
"""
from memory_hub import MemoryHub
import logging

logger = logging.getLogger("MemoryAgent")


class MemoryAgent:
    def __init__(self, hub: MemoryHub):
        self.name = "MemoryAgent"
        self.hub = hub

    def run(self, action: str, user_id: str, **kwargs):
        logger.info(f"Executing action '{action}' for user '{user_id}'")

        if action == "remember_conversation":
            content = kwargs.get("content", "")
            self.hub.save_memory(user_id, content, "conversation")
            return {"status": "ok", "note": "Memory saved", "agent": self.name}

        elif action == "recall":
            memories = self.hub.get_recent_memories(user_id)
            logger.info(f"Recalled {len(memories)} memories for user '{user_id}'")
            return {"status": "ok", "memories": memories, "agent": self.name}

        elif action == "set_preference":
            key = kwargs.get("key")
            value = kwargs.get("value")
            self.hub.save_preference(user_id, key, value)
            return {"status": "ok", "preference_set": f"{key}={value}", "agent": self.name}

        elif action == "get_preference":
            key = kwargs.get("key")
            value = self.hub.get_preference(user_id, key)
            return {"status": "ok", "value": value, "agent": self.name}

        else:
            logger.warning(f"Unknown action '{action}' requested")
            return {"status": "error", "message": f"Unknown action {action}", "agent": self.name}