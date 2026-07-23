"""Secrets vault abstraction for LaserSim production security."""

class SecretsVault:
    def __init__(self):
        self._secrets = {}

    def store(self, key, value):
        self._secrets[key] = value

    def get(self, key):
        return self._secrets.get(key)
