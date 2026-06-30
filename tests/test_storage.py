"""Validate energy-storage efficiency."""
import numpy as np

from storage import Storage


def test_short_pump_high_efficiency():
    s = Storage(tau_us=230)
    assert s.efficiency(20) > s.efficiency(400)


def test_efficiency_bounded():
    s = Storage()
    for p in (10, 200, 1000):
        e = s.efficiency(p)
        assert 0.0 < e <= 1.0


def test_inversion_saturates():
    s = Storage(tau_us=230)
    assert s.inversion_fraction(2000) > 0.99


def test_efficiency_limit_short_pump():
    s = Storage(tau_us=230)
    # as pump -> 0, efficiency -> 1
    assert np.isclose(s.efficiency(0.01), 1.0, rtol=1e-3)


def test_paper_point_reasonable():
    s = Storage(tau_us=230)
    eta = s.efficiency(200)
    assert 0.7 < eta < 0.95
