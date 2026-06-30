"""Validate M^2 beam-quality analysis."""
import numpy as np

from beam_quality import BeamQuality


def test_ideal_beam_m2_one_min_divergence():
    ideal = BeamQuality(m2=1.0, w0_m=8e-3)
    worse = BeamQuality(m2=2.0, w0_m=8e-3)
    assert worse.divergence > ideal.divergence


def test_bpp_scales_with_m2():
    b1 = BeamQuality(m2=1.0, w0_m=5e-3)
    b2 = BeamQuality(m2=2.0, w0_m=5e-3)
    assert np.isclose(b2.bpp / b1.bpp, 2.0, rtol=1e-6)


def test_width_at_waist_is_w0():
    b = BeamQuality(m2=1.5, w0_m=4e-3)
    assert np.isclose(b.width(0.0), b.w0_m, rtol=1e-9)


def test_higher_m2_bigger_focal_spot():
    good = BeamQuality(m2=1.0, w0_m=8e-3)
    bad = BeamQuality(m2=2.5, w0_m=8e-3)
    assert bad.focal_spot(0.2, 8e-3) > good.focal_spot(0.2, 8e-3)


def test_brightness_drops_with_m2():
    good = BeamQuality(m2=1.0, w0_m=8e-3)
    bad = BeamQuality(m2=2.0, w0_m=8e-3)
    assert good.brightness(1e9) > bad.brightness(1e9)
