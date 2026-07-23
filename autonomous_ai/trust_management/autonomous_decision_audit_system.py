class AutonomousDecisionAuditSystem:
    def __init__(self):
        self.audit_logs = []

    def record_decision(self, decision, result):
        self.audit_logs.append({"decision": decision, "result": result})

    def get_audit_logs(self):
        return self.audit_logs
