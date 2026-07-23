"""LaserSim API authentication foundation."""

class APIAuthenticator:
    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id):
        token = f"session-{user_id}"
        self.sessions[token] = user_id
        return token

    def validate(self, token):
        return token in self.sessions
