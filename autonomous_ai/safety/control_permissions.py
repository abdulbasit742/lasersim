class ControlPermissions:
    """Permission layer for AI experiment control."""

    def __init__(self):
        self.permissions = {
            "simulate": True,
            "recommend": True,
            "execute": False
        }

    def can_execute(self):
        return self.permissions["execute"]
