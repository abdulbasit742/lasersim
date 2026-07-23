"""AI alliance formation system foundation."""

from datetime import datetime


class AIAllianceFormationSystem:
    def __init__(self):
        self.alliances = []

    def form_alliance(self, members, purpose):
        alliance = {
            "members": members,
            "purpose": purpose,
            "formed_at": datetime.utcnow().isoformat(),
            "status": "forming",
        }
        self.alliances.append(alliance)
        return alliance

    def get_alliances(self):
        return self.alliances
