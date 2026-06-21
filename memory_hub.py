"""
memory_hub.py
Central storage that all agents share.
Now with logging and confidence scoring for observability.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Set up professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MemoryHub")


class MemoryHub:
    def __init__(self):
        self.user_memories: Dict[str, List[Dict]] = {}
        self.preferences: Dict[str, Dict[str, str]] = {}
        self.agent_messages: Dict[str, List[Dict]] = {}
        self.code_cache: Dict[str, Dict[str, Any]] = {}  # Now stores confidence score too
        self.operation_log: List[Dict] = []  # For observability

    def _log_operation(self, operation: str, details: Dict):
        """Central logging for all hub operations."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            **details
        }
        self.operation_log.append(log_entry)
        logger.info(f"{operation}: {details}")

    # ----- User memory (long term) -----
    def save_memory(self, user_id: str, content: str, mem_type: str = "conversation") -> None:
        if user_id not in self.user_memories:
            self.user_memories[user_id] = []
        self.user_memories[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": mem_type,
            "content": content
        })
        self._log_operation("save_memory", {"user_id": user_id, "content_preview": content[:40]})

    def get_recent_memories(self, user_id: str, limit: int = 5) -> List[str]:
        if user_id not in self.user_memories:
            self._log_operation("get_memories_no_data", {"user_id": user_id})
            return []
        memories = [m["content"] for m in self.user_memories[user_id][-limit:]]
        self._log_operation("get_recent_memories", {"user_id": user_id, "count": len(memories)})
        return memories

    # ----- Preferences -----
    def save_preference(self, user_id: str, key: str, value: str) -> None:
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        self.preferences[user_id][key] = value
        self._log_operation("save_preference", {"user_id": user_id, "key": key})

    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        value = self.preferences.get(user_id, {}).get(key)
        self._log_operation("get_preference", {"user_id": user_id, "key": key, "found": value is not None})
        return value

    # ----- Agent-to-agent communication -----
    def send_message(self, conv_id: str, from_agent: str, to_agent: str, msg: str) -> None:
        if conv_id not in self.agent_messages:
            self.agent_messages[conv_id] = []
        self.agent_messages[conv_id].append({
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "message": msg
        })
        self._log_operation("send_message", {"conv_id": conv_id, "from": from_agent, "to": to_agent})

    def get_messages_for(self, conv_id: str, agent_name: str) -> List[str]:
        if conv_id not in self.agent_messages:
            return []
        messages = [m["message"] for m in self.agent_messages[conv_id] if m["to"] == agent_name]
        self._log_operation("get_messages_for", {"conv_id": conv_id, "agent": agent_name, "count": len(messages)})
        return messages

    # ----- Code explanation cache with confidence scoring -----
    def cache_code(self, code_hash: str, explanation: str, confidence: float = 0.0) -> None:
        self.code_cache[code_hash] = {
            "explanation": explanation,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        self._log_operation("cache_code", {"code_hash": code_hash[:8], "confidence": confidence})

    def get_cached_code(self, code_hash: str) -> Optional[Dict]:
        return self.code_cache.get(code_hash)

    # ----- Observability utilities -----
    def get_operation_summary(self) -> Dict:
        """Return a summary of all operations for monitoring."""
        return {
            "total_operations": len(self.operation_log),
            "memories_stored": len(self.user_memories),
            "preferences_stored": len(self.preferences),
            "messages_passed": sum(len(v) for v in self.agent_messages.values()),
            "code_cache_hits": len(self.code_cache)
        }