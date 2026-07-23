"""Reliability governance intelligence fusion foundation.

Provides a lightweight structure for combining governance signals,
reliability metrics, and policy evaluation results.
"""


class ReliabilityGovernanceIntelligenceFusion:
    def __init__(self):
        self.sources = []
        self.fusion_history = []

    def add_source(self, name, score):
        self.sources.append({"name": name, "score": score})

    def fuse(self):
        if not self.sources:
            return 0
        score = sum(item["score"] for item in self.sources) / len(self.sources)
        self.fusion_history.append(score)
        return score
