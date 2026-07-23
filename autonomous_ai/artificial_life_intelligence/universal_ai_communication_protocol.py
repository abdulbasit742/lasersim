"""Universal AI Communication Protocol foundation.

Provides a structured foundation for communication between large-scale AI
systems, civilizations, and federated intelligence networks.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class CommunicationMessage:
    sender: str
    receiver: str
    message_type: str
    payload: str
    timestamp: str


class UniversalAICommunicationProtocol:
    def __init__(self):
        self.messages: List[CommunicationMessage] = []

    def transmit(self, sender: str, receiver: str, message_type: str, payload: str):
        message = CommunicationMessage(
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.messages.append(message)
        return message
