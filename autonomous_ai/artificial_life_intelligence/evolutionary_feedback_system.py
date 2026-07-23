"""Evolutionary feedback system foundation for adaptive AI populations."""

from datetime import datetime


class EvolutionaryFeedbackSystem:
    def __init__(self):
        self.feedback_records = []

    def add_feedback(self, agent_group, feedback, improvement):
        record = {
            "agent_group": agent_group,
            "feedback": feedback,
            "improvement": improvement,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.feedback_records.append(record)
        return record

    def history(self):
        return list(self.feedback_records)
