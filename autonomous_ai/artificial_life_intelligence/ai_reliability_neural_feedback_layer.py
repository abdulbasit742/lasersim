"""AI Reliability Neural Feedback Layer foundation.

Provides feedback storage for future adaptive reliability learning.
"""


class AIReliabilityNeuralFeedbackLayer:
    def __init__(self):
        self.feedback_records = []

    def add_feedback(self, source, outcome, impact):
        record = {
            "source": source,
            "outcome": outcome,
            "impact": impact,
        }
        self.feedback_records.append(record)
        return record

    def latest_feedback(self):
        return self.feedback_records[-1] if self.feedback_records else None
