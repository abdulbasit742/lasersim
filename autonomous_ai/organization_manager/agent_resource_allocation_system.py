"""Agent resource allocation foundation."""

class AgentResourceAllocationSystem:
    def __init__(self):
        self.resources = {}

    def allocate(self, agent, resource):
        self.resources.setdefault(agent, []).append(resource)
        return self.resources[agent]
