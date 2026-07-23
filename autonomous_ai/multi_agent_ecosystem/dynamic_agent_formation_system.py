"""Dynamic agent formation system foundation for LaserSim."""

from dataclasses import dataclass, field


@dataclass
class AgentTeam:
    team_id: str
    members: list[str] = field(default_factory=list)
    objective: str = ""


class DynamicAgentFormationSystem:
    def __init__(self):
        self.teams: dict[str, AgentTeam] = {}

    def create_team(self, team_id: str, members: list[str], objective: str):
        self.teams[team_id] = AgentTeam(team_id, members, objective)

    def get_team(self, team_id: str):
        return self.teams.get(team_id)
