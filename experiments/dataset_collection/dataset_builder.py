"""Collect experiment outputs for AI training datasets."""

class DatasetBuilder:
    def __init__(self):
        self.samples = []

    def add_sample(self, beam_data, label):
        self.samples.append({"data": beam_data, "label": label})

    def export(self):
        return self.samples
