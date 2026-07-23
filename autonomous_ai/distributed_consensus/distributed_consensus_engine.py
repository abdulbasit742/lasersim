"""Distributed consensus engine foundation for LaserSim autonomous agents."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ConsensusDecision:
    topic: str
    proposals: List[str] = field(default_factory=list)
    selected: str | None = None


class DistributedConsensusEngine:
    def __init__(self):
        self.decisions = []

    def collect_proposal(self, decision: ConsensusDecision, proposal: str):
        decision.proposals.append(proposal)

    def reach_consensus(self, decision: ConsensusDecision):
        decision.selected = decision.proposals[0] if decision.proposals else None
        self.decisions.append(decision)
        return decision.selected
