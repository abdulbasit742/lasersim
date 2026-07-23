"""AI reliability learning accelerator foundation."""

from dataclasses import dataclass


@dataclass
class ReliabilityLearningRecord:
    lesson: str
    improvement_score: float


class AIReliabilityLearningAccelerator:
    def __init__(self):
        self.records = []

    def learn(self, lesson: str, improvement_score: float):
        record = ReliabilityLearningRecord(lesson, improvement_score)
        self.records.append(record)
        return record

    def best_learning(self):
        if not self.records:
            return None
        return max(self.records, key=lambda item: item.improvement_score)
