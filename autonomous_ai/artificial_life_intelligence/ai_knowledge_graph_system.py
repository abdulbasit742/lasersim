"""AI Knowledge Graph System foundation for LaserSim.
Tracks entities, relationships, and evolving knowledge structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeNode:
    node_id: str
    concept: str
    metadata: Dict = field(default_factory=dict)


class AIKnowledgeGraphSystem:
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relationships: List[dict] = []

    def add_node(self, node_id: str, concept: str, metadata=None):
        self.nodes[node_id] = KnowledgeNode(node_id, concept, metadata or {})

    def add_relationship(self, source: str, target: str, relation: str):
        self.relationships.append({
            "source": source,
            "target": target,
            "relation": relation,
        })

    def summary(self):
        return {
            "nodes": len(self.nodes),
            "relationships": len(self.relationships),
        }
