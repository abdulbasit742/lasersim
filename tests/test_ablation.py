"""Validate the ablation / micromachining model."""
import numpy as np

from ablation import Ablator, MATERIALS


def test_no_ablation_below_threshold():
    ab = Ablator(MATERIALS["steel"])
    assert ab.depth_per_pulse_nm(MATERIALS["steel"].f_threshold_Jcm2 * 0.5) == 0.0


def test_depth_grows_with_fluence():
    ab = Ablator(MATERIALS["steel"])
    assert ab.depth_per_pulse_nm(2.0) > ab.depth_per_pulse_nm(0.5)


def test_log_law_at_e_times_threshold():
    m = MATERIALS["steel"]
    ab = Ablator(m)
    # at F = e * F_th, ln = 1 -> depth = penetration
    d = ab.depth_per_pulse_nm(np.e * m.f_threshold_Jcm2)
    assert np.isclose(d, m.penetration_nm, rtol=1e-6)


def test_removal_rate_scales_with_rep():
    slow = Ablator(MATERIALS["steel"], rep_hz=10)
    fast = Ablator(MATERIALS["steel"], rep_hz=100)
    assert fast.removal_rate_mm3_per_s(2.0) > slow.removal_rate_mm3_per_s(2.0)


def test_silica_higher_threshold_than_metal():
    assert MATERIALS["fused_silica"].f_threshold_Jcm2 > MATERIALS["steel"].f_threshold_Jcm2
