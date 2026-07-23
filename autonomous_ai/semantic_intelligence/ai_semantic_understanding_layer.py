"""Semantic understanding layer foundation for LaserSim AI."""


class SemanticUnderstandingLayer:
    def __init__(self):
        self.semantic_context = []

    def register_context(self, context):
        self.semantic_context.append(context)

    def get_context(self):
        return list(self.semantic_context)
