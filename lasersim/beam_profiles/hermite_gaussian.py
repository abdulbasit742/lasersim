"""Hermite-Gaussian laser beam modes.

Provides normalized spatial mode generation for ML datasets
and optical propagation experiments.
"""

import numpy as np


def hermite_gaussian(x, y, mode_x=0, mode_y=0, waist=1.0):
    """Generate a Hermite-Gaussian transverse field profile."""
    X, Y = np.meshgrid(x, y)
    xi = np.sqrt(2) * X / waist
    yi = np.sqrt(2) * Y / waist

    hx = np.polynomial.hermite.hermval(xi, [0] * mode_x + [1])
    hy = np.polynomial.hermite.hermval(yi, [0] * mode_y + [1])

    field = hx * hy * np.exp(-(X**2 + Y**2) / waist**2)
    norm = np.sqrt(np.sum(np.abs(field) ** 2))
    return field / norm if norm else field
