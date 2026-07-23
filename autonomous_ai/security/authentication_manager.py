"""Authentication foundation for LaserSim remote AI services."""

class AuthenticationManager:
    def __init__(self):
        self.users = {}

    def register_user(self, user_id, role):
        self.users[user_id] = {"role": role}
        return True

    def authenticate(self, user_id):
        return user_id in self.users
