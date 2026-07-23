"""Gaussian laser beam profiles."""

import numpy as np


def gaussian_intensity(x, y, waist=1.0, power=1.0):
    """Return normalized Gaussian beam intensity.

    Parameters
    ----------
    x, y : array_like
        Spatial coordinates.
    waist : float
        Beam waist radius.
    power : float
        Scaling factor.
    """
    r2 = np.asarray(x) ** 2 + np.asarray(y) ** 2
    return power * np.exp(-2.0 * r2 / waist**2)
