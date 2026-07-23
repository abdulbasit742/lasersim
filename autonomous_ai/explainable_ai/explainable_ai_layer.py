"""Explainable AI foundation for LaserSim autonomous intelligence."""

class ExplainableAILayer:
    def __init__(self):
        self.explanations = []

    def record_explanation(self, decision, reason):
        self.explanations.append({"decision": decision, "reason": reason})

    def latest(self):
        return self.explanations[-1] if self.explanations else None
