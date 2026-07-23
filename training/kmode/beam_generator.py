"""Generate synthetic beam intensity maps for K-mode experiments."""

import numpy as np


def gaussian_beam(size=64, sigma=12):
    x = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, x)
    return np.exp(-(X**2 + Y**2) * size / sigma)


def generate_dataset(samples=100):
    return np.array([gaussian_beam() for _ in range(samples)])
