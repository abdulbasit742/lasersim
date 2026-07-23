"""AI chat session management foundation for LaserSim."""

class AIChatSession:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def history(self):
        return self.messages
