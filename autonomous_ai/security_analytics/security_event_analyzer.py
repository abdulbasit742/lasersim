"""Security event analytics foundation for LaserSim AI operations."""

from datetime import datetime


class SecurityEventAnalyzer:
    def __init__(self):
        self.events = []

    def record_event(self, event_type, severity, details=None):
        event = {
            "type": event_type,
            "severity": severity,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.events.append(event)
        return event

    def summarize(self):
        return {
            "total_events": len(self.events),
            "latest": self.events[-1] if self.events else None,
        }
