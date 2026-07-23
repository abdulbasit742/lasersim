"""Multi-agent memory sharing foundation for LaserSim autonomous AI."""

from datetime import datetime


class MultiAgentMemorySharingSystem:
    def __init__(self):
        self.shared_memory = []

    def store_shared_memory(self, agent_id, knowledge):
        self.shared_memory.append({
            "agent_id": agent_id,
            "knowledge": knowledge,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_shared_memory(self):
        return list(self.shared_memory)
