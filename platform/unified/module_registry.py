"""Unified module registry for LaserSim services."""

class ModuleRegistry:
    def __init__(self):
        self.registry = {}

    def add(self, name, module):
        self.registry[name] = module

    def list_modules(self):
        return list(self.registry.keys())
