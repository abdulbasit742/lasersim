"""Validate longitudinal pump absorption."""
import numpy as np

from pump_absorption import PumpAbsorption


def test_more_doping_more_absorption():
    lo = PumpAbsorption(doping_pct=0.3)
    hi = PumpAbsorption(doping_pct=1.5)
    assert hi.absorbed_fraction() > lo.absorbed_fraction()


def test_longer_rod_more_absorption():
    short = PumpAbsorption(length_mm=50)
    long = PumpAbsorption(length_mm=200)
    assert long.absorbed_fraction() > short.absorbed_fraction()


def test_absorbed_fraction_bounded():
    for d in (0.1, 0.7, 2.0):
        f = PumpAbsorption(doping_pct=d).absorbed_fraction()
        assert 0.0 <= f <= 1.0


def test_more_doping_worse_uniformity():
    lo = PumpAbsorption(doping_pct=0.3)
    hi = PumpAbsorption(doping_pct=1.5)
    assert hi.uniformity() < lo.uniformity()


def test_uniformity_and_absorption_complementary():
    pa = PumpAbsorption(doping_pct=0.7)
    # back/front = 1 - absorbed (since front-face deposition normalized)
    assert np.isclose(pa.uniformity(), 1 - pa.absorbed_fraction(), rtol=1e-6)
