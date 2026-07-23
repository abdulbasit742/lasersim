"""Infrastructure health intelligence foundation."""

class InfrastructureHealthIntelligence:
    def __init__(self):
        self.health_records = []

    def record_health(self, resource, status):
        record = {"resource": resource, "status": status}
        self.health_records.append(record)
        return record

    def history(self):
        return list(self.health_records)
