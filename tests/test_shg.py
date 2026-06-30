"""Validate second-harmonic generation."""
import numpy as np

from shg import SHGCrystal, peak_intensity


def test_efficiency_increases_with_intensity():
    c = SHGCrystal()
    assert c.efficiency(5e13) > c.efficiency(1e12)


def test_efficiency_bounded_0_1():
    c = SHGCrystal()
    for I in (0.0, 1e12, 1e14, 1e16):
        e = c.efficiency(I)
        assert 0.0 <= e <= 1.0


def test_phase_mismatch_reduces_efficiency():
    c = SHGCrystal()
    matched = c.efficiency(1e13, dk=0.0)
    mismatched = c.efficiency(1e13, dk=500.0)
    assert mismatched < matched


def test_longer_crystal_more_conversion():
    short = SHGCrystal(length_mm=5.0)
    long = SHGCrystal(length_mm=20.0)
    assert long.efficiency(1e13) > short.efficiency(1e13)


def test_peak_intensity_positive():
    assert peak_intensity(1.28, 200e-12, 0.8) > 0
