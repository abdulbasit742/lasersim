"""Natural language explanation system foundation."""


class NaturalLanguageExplanationSystem:
    def __init__(self):
        self.explanations = []

    def generate_explanation(self, decision, reason):
        explanation = f"Decision: {decision}. Reason: {reason}."
        self.explanations.append(explanation)
        return explanation
