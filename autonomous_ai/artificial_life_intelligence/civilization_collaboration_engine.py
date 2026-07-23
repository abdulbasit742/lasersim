"""Civilization collaboration engine foundation."""

from datetime import datetime


class CivilizationCollaborationEngine:
    def __init__(self):
        self.collaborations = []

    def create_collaboration(self, civilization_a, civilization_b, objective):
        record = {
            "civilization_a": civilization_a,
            "civilization_b": civilization_b,
            "objective": objective,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        self.collaborations.append(record)
        return record

    def list_collaborations(self):
        return self.collaborations
