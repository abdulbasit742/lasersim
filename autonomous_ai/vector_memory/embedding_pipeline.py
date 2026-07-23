"""Embedding pipeline foundation for LaserSim experiment memory."""

class EmbeddingPipeline:
    def __init__(self, model_name="beam-experiment-embedding"):
        self.model_name = model_name

    def create_embedding(self, experiment_record):
        """Create an embedding representation for an experiment record."""
        return {
            "model": self.model_name,
            "vector": [],
            "source": experiment_record,
        }
