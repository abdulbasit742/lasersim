"""Validate thermal-lens + ABCD cavity behavior."""
import numpy as np
import pytest

from thermal_abcd import ThermalRod, TwoMirrorCavity, M_space, M_lens, chain


def test_no_pump_no_lens():
    rod = ThermalRod()
    assert np.isinf(rod.focal_length(0.0))
    assert rod.dioptric_power(0.0) == 0.0


def test_focal_length_decreases_with_power():
    rod = ThermalRod()
    f_low = rod.focal_length(50.0)
    f_high = rod.focal_length(200.0)
    assert f_high < f_low  # stronger lens at higher power


def test_dioptric_power_linear_in_heat():
    rod = ThermalRod()
    d1 = rod.dioptric_power(100.0)
    d2 = rod.dioptric_power(200.0)
    assert d2 == pytest.approx(2.0 * d1, rel=1e-6)


def test_abcd_space_lens_identity():
    # space(0) is identity; lens(inf) is identity
    assert np.allclose(M_space(0.0), np.eye(2))
    assert np.allclose(M_lens(np.inf), np.eye(2))


def test_abcd_determinant_unity():
    M = chain(M_space(0.2), M_lens(0.5), M_space(0.3))
    assert np.linalg.det(M) == pytest.approx(1.0, rel=1e-9)


def test_cavity_stability_is_bounded_when_stable():
    rod = ThermalRod()
    cav = TwoMirrorCavity(R1=np.inf, R2=5.0, d1=0.15, d2=0.15, rod=rod)
    P = 100.0
    if cav.is_stable(P):
        assert not np.isnan(cav.mode_radius(P))
        assert cav.mode_radius(P) > 0
