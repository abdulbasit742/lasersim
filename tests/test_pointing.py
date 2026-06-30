"""Validate beam pointing stability."""
import numpy as np

from pointing import Pointing


def test_wander_grows_with_range():
    p = Pointing(jitter_urad=5)
    assert p.spot_wander_m(2000) > p.spot_wander_m(500)


def test_hit_prob_higher_for_bigger_target():
    p = Pointing(jitter_urad=5)
    assert p.hit_probability(1000, 0.2) > p.hit_probability(1000, 0.02)


def test_less_jitter_better_hit():
    good = Pointing(jitter_urad=1)
    bad = Pointing(jitter_urad=20)
    assert good.hit_probability(1000, 0.1) > bad.hit_probability(1000, 0.1)


def test_budget_achieves_target_probability():
    p = Pointing(jitter_urad=5)
    budget = p.max_jitter_for(1000, 0.1, 0.95)
    p2 = Pointing(jitter_urad=budget)
    assert np.isclose(p2.hit_probability(1000, 0.1), 0.95, rtol=0.02)


def test_zero_jitter_certain_hit():
    p = Pointing(jitter_urad=0.0)
    assert p.hit_probability(1000, 0.1) == 1.0
