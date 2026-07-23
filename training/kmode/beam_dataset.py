"""Synthetic beam dataset generator for K-mode learning."""

import numpy as np


class BeamModeDataset:
    def __init__(self):
        self.samples = []
        self.labels = []

    def add_sample(self, profile, mode):
        self.samples.append(np.asarray(profile))
        self.labels.append(mode)

    def as_arrays(self):
        return np.array(self.samples), np.array(self.labels)

    def generate_features(self):
        X = []
        for sample in self.samples:
            intensity = np.abs(sample) ** 2
            X.append([
                float(np.mean(intensity)),
                float(np.max(intensity)),
                float(np.std(intensity))
            ])
        return np.array(X)
