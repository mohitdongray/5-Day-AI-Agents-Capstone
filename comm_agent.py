"""
comm_agent.py
Enables agents to talk to each other via a shared message bus.
Now with logging for observability.
"""
from memory_hub import MemoryHub
import logging

logger = logging.getLogger("CommAgent")


class CommunicationAgent:
    def __init__(self, hub: MemoryHub):
        self.name = "CommAgent"
        self.hub = hub

    def run(self, action: str, conversation_id: str, **kwargs):
        logger.info(f"Executing action '{action}' in conversation '{conversation_id}'")

        if action == "send":
            from_agent = kwargs.get("from_agent", "unknown")
            to_agent = kwargs.get("to_agent")
            message = kwargs.get("message", "")
            self.hub.send_message(conversation_id, from_agent, to_agent, message)
            return {"status": "sent", "agent": self.name}

        elif action == "poll":
            agent_name = kwargs.get("agent_name")
            messages = self.hub.get_messages_for(conversation_id, agent_name)
            logger.info(f"Retrieved {len(messages)} messages for agent '{agent_name}'")
            return {"status": "ok", "messages": messages, "agent": self.name}

        else:
            logger.warning(f"Unknown action '{action}' requested")
            return {"status": "error", "message": f"Unknown action {action}", "agent": self.name}