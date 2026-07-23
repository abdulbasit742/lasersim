"""Security monitoring dashboard data foundation."""


class SecurityMonitor:
    def __init__(self):
        self.alerts = []

    def add_alert(self, alert):
        self.alerts.append(alert)

    def summary(self):
        return {
            "total_alerts": len(self.alerts),
            "healthy": len(self.alerts) == 0
        }
