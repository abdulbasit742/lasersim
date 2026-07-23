"""
Autonomous Healing Decision Network
Foundation for recovery decision coordination.
"""


class AutonomousHealingDecisionNetwork:
    def __init__(self):
        self.decisions = []

    def register_decision(self, situation, action, confidence):
        record = {
            "situation": situation,
            "action": action,
            "confidence": confidence,
        }
        self.decisions.append(record)
        return record

    def best_decision(self):
        if not self.decisions:
            return None
        return max(self.decisions, key=lambda item: item["confidence"])
