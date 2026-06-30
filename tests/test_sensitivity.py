"""Validate Monte Carlo tolerancing + sensitivity."""
import numpy as np

from sensitivity import (
    default_params, nominal_dict, chain_output_mJ, monte_carlo,
    sensitivity_ranking,
)


def test_nominal_near_target():
    out = chain_output_mJ(nominal_dict(default_params()))
    assert 950.0 <= out <= 1600.0


def test_monte_carlo_spread_positive_and_small():
    outs = monte_carlo(default_params(), n=400, seed=3)
    mean, std = outs.mean(), outs.std()
    assert std > 0
    # with ~1% component tolerances, output RMS should be a few percent at most
    assert 100.0 * std / mean < 10.0


def test_sensitivity_shares_sum_to_one():
    _, shares = sensitivity_ranking(default_params(), n=300, seed=4)
    assert np.isclose(sum(shares.values()), 1.0, atol=1e-6)


def test_zero_tolerance_zero_spread():
    params = default_params()
    for p in params:
        p.rel_sigma = 0.0
    outs = monte_carlo(params, n=100)
    assert np.isclose(outs.std(), 0.0, atol=1e-6)
