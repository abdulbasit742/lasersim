"""LaserSim alert management foundation."""


class AlertManager:
    def __init__(self):
        self.alerts = []

    def trigger(self, name, severity, message):
        self.alerts.append({
            "name": name,
            "severity": severity,
            "message": message,
        })

    def get_alerts(self):
        return self.alerts
