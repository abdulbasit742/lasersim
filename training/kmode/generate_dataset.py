"""Synthetic laser beam dataset generator for K-mode experiments."""

import numpy as np


def create_sample(feature_size=3):
    intensity = np.random.random(feature_size)
    label = np.random.randint(0, 10)
    return intensity, label


def generate_dataset(samples=1000):
    features = []
    labels = []

    for _ in range(samples):
        x, y = create_sample()
        features.append(x)
        labels.append(y)

    return np.array(features), np.array(labels)
