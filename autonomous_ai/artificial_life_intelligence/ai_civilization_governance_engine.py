"""AI Civilization Governance Engine foundation.

Provides a lightweight foundation for tracking governance structures,
policies, and decision events inside autonomous AI civilizations.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GovernancePolicy:
    name: str
    status: str = "active"


@dataclass
class CivilizationGovernanceEngine:
    policies: Dict[str, GovernancePolicy] = field(default_factory=dict)
    decisions: List[dict] = field(default_factory=list)

    def register_policy(self, policy: GovernancePolicy) -> None:
        self.policies[policy.name] = policy

    def record_decision(self, decision: dict) -> None:
        self.decisions.append(decision)
