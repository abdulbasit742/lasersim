"""
Inter-Civilization Communication Network
Foundation layer for autonomous AI civilization communication.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CommunicationRecord:
    source: str
    target: str
    message_type: str
    status: str = "pending"


class InterCivilizationCommunicationNetwork:
    def __init__(self):
        self.records: List[CommunicationRecord] = []
        self.civilizations: Dict[str, Dict] = {}

    def register_civilization(self, name: str, capabilities=None):
        self.civilizations[name] = {
            "capabilities": capabilities or [],
            "connections": []
        }

    def send_message(self, source: str, target: str, message_type: str):
        record = CommunicationRecord(source, target, message_type, "sent")
        self.records.append(record)
        return record
