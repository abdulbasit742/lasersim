class AutonomousAITrustManagementLayer:
    def __init__(self):
        self.trust_records = []

    def record_trust_event(self, component, score):
        self.trust_records.append({"component": component, "score": score})

    def get_trust_history(self):
        return self.trust_records
