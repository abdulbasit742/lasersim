"""Cognitive association engine foundation for LaserSim autonomous AI."""


class CognitiveAssociationEngine:
    def __init__(self):
        self.associations = []

    def add_association(self, concept_a, concept_b, relation):
        self.associations.append({
            "from": concept_a,
            "to": concept_b,
            "relation": relation,
        })

    def get_associations(self):
        return list(self.associations)
