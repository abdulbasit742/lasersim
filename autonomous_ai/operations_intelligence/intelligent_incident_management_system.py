"""Intelligent Incident Management System foundation for LaserSim AI."""

from datetime import datetime


class IntelligentIncidentManagementSystem:
    def __init__(self):
        self.incidents = []

    def register_incident(self, component, severity, description):
        incident = {
            "component": component,
            "severity": severity,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
        }
        self.incidents.append(incident)
        return incident

    def resolve_incident(self, index):
        if 0 <= index < len(self.incidents):
            self.incidents[index]["status"] = "resolved"
            return self.incidents[index]
        return None
