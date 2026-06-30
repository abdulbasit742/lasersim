"""Validate phase-matching acceptance bandwidths."""
import numpy as np

from phase_matching import PhaseMatch, sinc2


def test_perfect_match_full_conversion():
    pm = PhaseMatch()
    assert np.isclose(pm.efficiency_vs_dk(0.0), 1.0)


def test_conversion_drops_with_mismatch():
    pm = PhaseMatch()
    assert pm.efficiency_vs_dk(300) < pm.efficiency_vs_dk(0)


def test_longer_crystal_tighter_acceptance():
    short = PhaseMatch(length_mm=5)
    long = PhaseMatch(length_mm=20)
    assert long.angular_acceptance_mrad() < short.angular_acceptance_mrad()


def test_acceptance_is_half_max_width():
    pm = PhaseMatch(length_mm=12)
    # at half the angular acceptance from center, efficiency ~ 0.5
    dtheta = pm.angular_acceptance_mrad() / 2
    dk = pm.dkd_angle_per_mrad * dtheta
    assert np.isclose(pm.efficiency_vs_dk(dk), 0.5, rtol=0.05)


def test_all_acceptances_positive():
    pm = PhaseMatch()
    assert pm.angular_acceptance_mrad() > 0
    assert pm.thermal_acceptance_K() > 0
    assert pm.spectral_acceptance_nm() > 0
