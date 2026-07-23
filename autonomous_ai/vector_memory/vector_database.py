"""Vector database abstraction for LaserSim AI memory."""

class VectorMemoryStore:
    def __init__(self):
        self.records = []

    def add_record(self, embedding):
        self.records.append(embedding)

    def search(self, query_vector):
        """Similarity search placeholder."""
        return self.records
