"""Validate the air-breakdown / vacuum-relay model."""
from breakdown import FocusBreakdown, P_ATM_MBAR


def test_tighter_focus_higher_intensity():
    wide = FocusBreakdown(focus_radius_um=60)
    tight = FocusBreakdown(focus_radius_um=10)
    assert tight.focal_intensity_Wcm2() > wide.focal_intensity_Wcm2()


def test_threshold_rises_as_pressure_drops():
    fb = FocusBreakdown()
    assert fb.threshold_at_pressure(1e-3) > fb.threshold_at_pressure(P_ATM_MBAR)


def test_breaks_down_at_atm_for_high_power():
    fb = FocusBreakdown(peak_power_W=6.4e9, focus_radius_um=30)
    assert fb.breaks_down(P_ATM_MBAR)


def test_no_breakdown_in_good_vacuum():
    fb = FocusBreakdown(peak_power_W=6.4e9, focus_radius_um=30)
    assert not fb.breaks_down(6.5e-4)


def test_max_safe_pressure_consistent():
    fb = FocusBreakdown()
    p = fb.max_safe_pressure_mbar()
    # at the max safe pressure, intensity ~ threshold
    import numpy as np
    assert np.isclose(fb.focal_intensity_Wcm2(), fb.threshold_at_pressure(p), rtol=1e-6)
