"""Autonomous System Stability Analyzer foundation for LaserSim."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class StabilityReport:
    system: str
    stability_score: float
    created_at: str


class AutonomousSystemStabilityAnalyzer:
    def __init__(self):
        self.reports: List[StabilityReport] = []

    def analyze(self, system: str, stability_score: float):
        report = StabilityReport(
            system,
            stability_score,
            datetime.utcnow().isoformat()
        )
        self.reports.append(report)
        return report

    def latest_reports(self):
        return self.reports[-10:]
