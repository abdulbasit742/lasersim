"""
Autonomous Operational Memory
Stores operational intelligence history for future adaptation.
"""

from datetime import datetime


class AutonomousOperationalMemory:
    def __init__(self):
        self.memory_records = []

    def store_experience(self, event, outcome):
        record = {
            "event": event,
            "outcome": outcome,
            "created_at": datetime.utcnow().isoformat()
        }
        self.memory_records.append(record)
        return record

    def retrieve_memory(self):
        return self.memory_records
