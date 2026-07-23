"""Threat visualization data layer foundation."""


class ThreatVisualizer:
    def __init__(self):
        self.threats = []

    def add_threat(self, category, level, source):
        self.threats.append({
            "category": category,
            "level": level,
            "source": source,
        })
        return self.threats[-1]

    def get_dashboard_data(self):
        return {
            "active_threats": len(self.threats),
            "items": self.threats,
        }
