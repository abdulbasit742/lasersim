"""Autonomous recovery manager foundation for LaserSim."""


class RecoveryManager:
    def __init__(self):
        self.recovery_actions = []

    def register_action(self, action_name):
        self.recovery_actions.append(action_name)

    def evaluate_fault(self, fault):
        return {"fault": fault, "recovery_required": True}
