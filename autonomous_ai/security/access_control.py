"""Role and permission control foundation."""

class AccessControl:
    def __init__(self):
        self.permissions = {}

    def assign_permission(self, role, action):
        self.permissions.setdefault(role, []).append(action)

    def can_execute(self, role, action):
        return action in self.permissions.get(role, [])
