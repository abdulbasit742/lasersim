"""
Adaptive Recovery Decision Intelligence
Foundation layer for selecting improved recovery decisions.
"""

from datetime import datetime


class AdaptiveRecoveryDecisionIntelligence:
    def __init__(self):
        self.decisions = []

    def evaluate_decision(self, situation, action, confidence=0.0):
        record = {
            "situation": situation,
            "action": action,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.decisions.append(record)
        return record

    def latest_decision(self):
        return self.decisions[-1] if self.decisions else None
