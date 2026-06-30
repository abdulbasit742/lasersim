"""Validate rep-rate thermal limits."""
import numpy as np

from reprate import RepRateThermal


def test_rise_increases_with_rep_rate():
    rod = RepRateThermal()
    assert rod.steady_rise(100) > rod.steady_rise(10)


def test_rise_linear_in_rep_rate():
    rod = RepRateThermal()
    assert np.isclose(rod.steady_rise(20) / rod.steady_rise(10), 2.0, rtol=1e-9)


def test_max_rep_rate_within_budget():
    rod = RepRateThermal(max_rise_K=60.0)
    f_max = rod.max_rep_rate()
    assert np.isclose(rod.steady_rise(f_max), 60.0, rtol=1e-6)


def test_paper_10hz_under_budget():
    rod = RepRateThermal()
    assert rod.steady_rise(10) <= rod.max_rise_K


def test_more_heat_lowers_max_rep():
    cool = RepRateThermal(q_shot_J=2.0)
    hot = RepRateThermal(q_shot_J=8.0)
    assert hot.max_rep_rate() < cool.max_rep_rate()
