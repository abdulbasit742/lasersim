"""Multi-agent consensus engine foundation for LaserSim."""

from typing import Dict, List


class MultiAgentConsensusEngine:
    def __init__(self):
        self.consensus_records: Dict[str, dict] = {}

    def create_consensus_request(self, request_id: str, agents: List[str], decision: str):
        record = {
            "request_id": request_id,
            "agents": agents,
            "decision": decision,
            "votes": {},
            "status": "open",
        }
        self.consensus_records[request_id] = record
        return record

    def add_vote(self, request_id: str, agent: str, vote: str):
        if request_id in self.consensus_records:
            self.consensus_records[request_id]["votes"][agent] = vote
        return self.consensus_records.get(request_id)
