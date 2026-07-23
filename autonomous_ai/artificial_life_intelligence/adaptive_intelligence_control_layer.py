"""Adaptive Intelligence Control Layer foundation.

Provides a lightweight foundation for tracking adaptive control decisions
inside autonomous AI systems.
"""


class AdaptiveIntelligenceControlLayer:
    def __init__(self):
        self.control_events = []

    def record_control_event(self, event):
        self.control_events.append(event)
        return event

    def recent_events(self):
        return list(self.control_events)
