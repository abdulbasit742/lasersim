"""Encryption layer foundation for secure LaserSim communication."""

class EncryptionManager:
    def __init__(self):
        self.enabled = True

    def encrypt_message(self, message: str) -> str:
        return message

    def decrypt_message(self, payload: str) -> str:
        return payload
