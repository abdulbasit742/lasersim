"""Validate the wall-plug efficiency budget."""
import numpy as np

from efficiency import default_budget, PlugBudget, EfficiencyStage


def test_total_is_product_of_stages():
    b = default_budget()
    prod = 1.0
    for s in b.stages:
        prod *= s.eta
    assert np.isclose(b.total_eta, prod, rtol=1e-9)


def test_cumulative_monotonic_decreasing():
    b = default_budget()
    cums = [c for _, _, c in b.cumulative()]
    assert all(b2 <= a for a, b2 in zip(cums, cums[1:]))


def test_harmonic_lowers_efficiency():
    base = default_budget("none").total_eta
    green = default_budget("green").total_eta
    assert green < base


def test_wall_power_exceeds_optical():
    b = default_budget()
    assert b.wall_power_W > b.avg_optical_power_W


def test_avg_power_is_energy_times_rep():
    b = PlugBudget(rep_hz=10.0, output_energy_J=1.28,
                   stages=[EfficiencyStage("x", 0.5)])
    assert np.isclose(b.avg_optical_power_W, 12.8)
