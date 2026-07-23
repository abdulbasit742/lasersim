"""AI experience prioritization foundation."""

class AIExperiencePrioritization:
    def __init__(self):
        self.experiences = []

    def add_experience(self, experience, value=1):
        self.experiences.append({"experience": experience, "value": value})

    def prioritize(self):
        return sorted(
            self.experiences,
            key=lambda item: item["value"],
            reverse=True,
        )
