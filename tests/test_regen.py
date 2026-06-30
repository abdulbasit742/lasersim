"""Validate the regenerative amplifier model."""
import numpy as np

from regen import Regen


def test_buildup_grows_then_saturates():
    r = Regen()
    hist = r.buildup()
    # early growth
    assert hist[5] > hist[0]
    # eventually saturates (late steps barely change)
    assert hist[-1] >= hist[-2] * 0.9


def test_optimum_dump_is_max():
    r = Regen()
    n, e = r.optimum_dump()
    hist = r.buildup()
    assert np.isclose(e, hist.max())
    assert 0 <= n < len(hist)


def test_higher_gain_faster_buildup():
    slow = Regen(g0=1.4)
    fast = Regen(g0=2.2)
    assert fast.buildup()[10] > slow.buildup()[10]


def test_more_loss_lowers_output():
    lo = Regen(loss=0.02)
    hi = Regen(loss=0.15)
    assert lo.optimum_dump()[1] > hi.optimum_dump()[1]


def test_total_gain_large():
    r = Regen()
    _, e = r.optimum_dump()
    assert e / r.seed_J > 1e3
