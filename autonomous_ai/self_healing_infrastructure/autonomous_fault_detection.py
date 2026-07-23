"""Autonomous fault detection foundation."""


class AutonomousFaultDetection:
    def __init__(self):
        self.faults = []

    def register_fault(self, source, severity):
        fault = {"source": source, "severity": severity}
        self.faults.append(fault)
        return fault

    def get_faults(self):
        return self.faults
