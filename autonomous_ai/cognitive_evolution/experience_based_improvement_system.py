"""Experience based improvement system foundation."""

class ExperienceBasedImprovementSystem:
    def __init__(self):
        self.improvements = []

    def record_improvement(self, item):
        self.improvements.append(item)

    def get_history(self):
        return list(self.improvements)
