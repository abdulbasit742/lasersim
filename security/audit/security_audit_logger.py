"""Security audit event logging foundation."""

class SecurityAuditLogger:
    def __init__(self):
        self.events = []

    def record(self, event, user=None):
        self.events.append({"event": event, "user": user})

    def history(self):
        return self.events
