"""Beam profile generation and analysis tools.

This package provides reusable optical field profiles for simulation and
machine-learning dataset generation.
"""

from .gaussian_beam import gaussian_intensity

__all__ = ["gaussian_intensity"]
