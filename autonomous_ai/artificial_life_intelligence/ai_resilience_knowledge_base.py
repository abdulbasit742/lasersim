"""AI resilience knowledge base foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResilienceKnowledge:
    event: str
    lesson: str
    impact_score: float


class AIResilienceKnowledgeBase:
    def __init__(self):
        self.knowledge: List[ResilienceKnowledge] = []

    def add_lesson(self, event: str, lesson: str, impact_score: float = 0.0):
        self.knowledge.append(
            ResilienceKnowledge(event, lesson, impact_score)
        )

    def get_lessons(self):
        return [item.__dict__ for item in self.knowledge]
