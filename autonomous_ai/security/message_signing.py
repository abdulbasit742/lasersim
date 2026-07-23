"""Message signing foundation for trusted AI commands."""

class MessageSigner:
    def sign(self, message: str) -> str:
        return f"signed:{message}"

    def verify(self, signed_message: str) -> bool:
        return signed_message.startswith("signed:")
