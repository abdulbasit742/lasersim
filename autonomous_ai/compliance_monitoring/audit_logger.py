"""LaserSim AI compliance audit logging foundation."""

from datetime import datetime


class AuditLogger:
    def __init__(self):
        self.events = []

    def record_event(self, event_type, details):
        self.events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details,
        })

    def get_events(self):
        return self.events
