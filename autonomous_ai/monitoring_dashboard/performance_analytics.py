"""Experiment and AI performance analytics foundation."""


class PerformanceAnalytics:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def summary(self):
        return {
            "total_records": len(self.records),
            "latest": self.records[-1] if self.records else None,
        }
