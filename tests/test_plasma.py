"""Validate the laser-plasma interaction model."""
import numpy as np

from plasma import LaserPlasma


def test_tighter_focus_higher_intensity():
    big = LaserPlasma(spot_radius_um=50)
    small = LaserPlasma(spot_radius_um=5)
    assert small.intensity_Wcm2() > big.intensity_Wcm2()


def test_a0_increases_with_intensity():
    lo = LaserPlasma(peak_power_W=1e8, spot_radius_um=20)
    hi = LaserPlasma(peak_power_W=1e11, spot_radius_um=20)
    assert hi.a0() > lo.a0()


def test_critical_density_positive():
    assert LaserPlasma().critical_density_m3() > 0


def test_ponderomotive_scales_with_intensity():
    lp = LaserPlasma()
    u1 = lp.ponderomotive_eV()
    lp2 = LaserPlasma(peak_power_W=lp.peak_power_W * 4, spot_radius_um=lp.spot_radius_um)
    assert np.isclose(lp2.ponderomotive_eV() / u1, 4.0, rtol=1e-6)


def test_xray_fraction_bounded():
    for p in (1e8, 1e10, 1e12):
        f = LaserPlasma(peak_power_W=p).soft_xray_fraction()
        assert 0.0 <= f <= 0.05
