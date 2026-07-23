"""Secure token management foundation for LaserSim remote access."""

class TokenManager:
    def __init__(self):
        self.active_tokens = {}

    def issue_token(self, user_id):
        token = f"token_{user_id}"
        self.active_tokens[token] = user_id
        return token

    def validate_token(self, token):
        return self.active_tokens.get(token)
