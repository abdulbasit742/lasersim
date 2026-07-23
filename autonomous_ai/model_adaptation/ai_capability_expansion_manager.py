"""AI capability expansion manager foundation."""


class AICapabilityExpansionManager:
    def __init__(self):
        self.capabilities = []

    def register_capability(self, capability):
        self.capabilities.append(capability)

    def list_capabilities(self):
        return self.capabilities
