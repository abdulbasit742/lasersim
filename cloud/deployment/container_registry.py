"""Container image registry workflow foundation for LaserSim.

Provides structure for building, tagging, and tracking deployment images.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContainerImage:
    name: str
    tag: str
    created_at: str


class ContainerRegistry:
    def __init__(self):
        self.images = []

    def register(self, name: str, tag: str):
        image = ContainerImage(name, tag, datetime.utcnow().isoformat())
        self.images.append(image)
        return image
