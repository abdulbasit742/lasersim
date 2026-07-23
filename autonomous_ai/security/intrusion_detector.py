"""Security event monitoring foundation."""


class IntrusionDetector:
    def __init__(self):
        self.events = []

    def record_event(self, event):
        self.events.append(event)

    def analyze(self):
        return {
            "events_checked": len(self.events),
            "status": "normal"
        }
