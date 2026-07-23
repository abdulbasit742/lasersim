"""Civilization-scale knowledge sharing foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeSharingSystem:
    shared_knowledge: Dict[str, List[str]] = field(default_factory=dict)

    def publish(self, civilization: str, knowledge: str):
        self.shared_knowledge.setdefault(civilization, []).append(knowledge)

    def get_knowledge(self, civilization: str):
        return self.shared_knowledge.get(civilization, [])

    def network_summary(self):
        return {
            "civilizations": list(self.shared_knowledge.keys()),
            "knowledge_count": sum(len(v) for v in self.shared_knowledge.values()),
        }
