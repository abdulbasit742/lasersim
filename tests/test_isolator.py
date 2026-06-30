"""Validate the Faraday isolator model."""
import numpy as np

from isolator import FaradayIsolator


def test_rotation_scales_with_field():
    iso = FaradayIsolator()
    iso.field_T = 1.0
    r1 = iso.rotation_deg()
    iso.field_T = 2.0
    assert np.isclose(iso.rotation_deg() / r1, 2.0, rtol=1e-9)


def test_field_for_45_gives_45():
    iso = FaradayIsolator()
    iso.field_T = iso.field_for_45deg()
    assert np.isclose(iso.rotation_deg(), 45.0, rtol=1e-6)


def test_isolation_max_at_45():
    iso = FaradayIsolator()
    iso.field_T = iso.field_for_45deg()
    best = iso.isolation_dB()
    iso.field_T *= 1.2
    worse = iso.isolation_dB()
    assert best > worse


def test_isolation_positive():
    iso = FaradayIsolator()
    iso.field_T = iso.field_for_45deg()
    assert iso.isolation_dB() > 0


def test_longer_crystal_less_field():
    short = FaradayIsolator(length_mm=10)
    long = FaradayIsolator(length_mm=30)
    assert long.field_for_45deg() < short.field_for_45deg()
