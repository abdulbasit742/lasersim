"""Large-scale beam dataset management helpers."""

class BeamDatasetManager:
    def __init__(self, source=None):
        self.source = source
        self.samples = []

    def add_sample(self, sample):
        self.samples.append(sample)

    def size(self):
        return len(self.samples)
