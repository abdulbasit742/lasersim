"""Advanced experience replay engine foundation for lifelong AI learning."""

from collections import deque


class AdvancedExperienceReplayEngine:
    def __init__(self, capacity=1000):
        self.memory = deque(maxlen=capacity)

    def store_experience(self, experience):
        self.memory.append(experience)

    def retrieve_recent(self, limit=10):
        return list(self.memory)[-limit:]

    def size(self):
        return len(self.memory)
