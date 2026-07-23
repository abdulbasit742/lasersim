"""AI defense decision engine foundation."""


class DefenseDecisionEngine:
    def __init__(self):
        self.rules = {}

    def add_rule(self, name, action):
        self.rules[name] = action

    def decide(self, threat_type):
        return self.rules.get(threat_type, "observe")
