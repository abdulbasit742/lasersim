"""
Intelligent Experience Retrieval Engine
Provides foundation for retrieving past operational experiences.
"""


class IntelligentExperienceRetrievalEngine:
    def __init__(self):
        self.experiences = []

    def store_experience(self, experience):
        self.experiences.append(experience)

    def retrieve_related_experiences(self, keyword):
        return [
            item for item in self.experiences
            if keyword.lower() in str(item).lower()
        ]
