"""Laguerre-Gaussian laser beam modes."""

import numpy as np


def laguerre_gaussian(r, phi, radial_mode=0, azimuthal_mode=0, waist=1.0):
    """Generate normalized Laguerre-Gaussian transverse field."""
    R, P = np.meshgrid(r, phi)
    rho = np.sqrt(2) * R / waist

    radial = rho ** abs(azimuthal_mode)
    radial *= np.exp(-R**2 / waist**2)
    phase = np.exp(1j * azimuthal_mode * P)

    field = radial * phase
    norm = np.sqrt(np.sum(np.abs(field) ** 2))
    return field / norm if norm else field
