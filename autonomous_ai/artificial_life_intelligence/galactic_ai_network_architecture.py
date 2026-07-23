"""Galactic AI network architecture foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GalacticNetwork:
    name: str
    civilizations: List[str] = field(default_factory=list)
    connections: Dict[str, List[str]] = field(default_factory=dict)

    def register_civilization(self, civilization: str):
        if civilization not in self.civilizations:
            self.civilizations.append(civilization)
        self.connections.setdefault(civilization, [])

    def connect(self, source: str, target: str):
        self.connections.setdefault(source, [])
        if target not in self.connections[source]:
            self.connections[source].append(target)

    def status(self):
        return {
            "network": self.name,
            "civilizations": self.civilizations,
            "connections": self.connections,
        }
