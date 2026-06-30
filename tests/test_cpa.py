"""Validate the CPA stretcher/compressor model."""
import numpy as np

from cpa import (
    GratingPair, stretched_duration_s, separation_for_target,
    recompressed_duration_ps,
)


def test_gdd_negative_for_grating_pair():
    g = GratingPair()
    assert g.gdd_per_meter() < 0      # grating pairs give negative GDD


def test_more_separation_more_stretch():
    g = GratingPair()
    d1 = stretched_duration_s(g.gdd(0.1), 100.0)
    d2 = stretched_duration_s(g.gdd(0.5), 100.0)
    assert d2 > d1


def test_separation_reaches_target():
    g = GratingPair()
    sep = separation_for_target(g, tl_fs=100.0, target_ps=200.0)
    got = stretched_duration_s(g.gdd(sep), 100.0)
    assert np.isclose(got * 1e12, 200.0, rtol=0.05)


def test_zero_residual_recompresses_to_tl():
    assert np.isclose(recompressed_duration_ps(100.0, 0.0) * 1e3, 100.0, rtol=1e-6)


def test_residual_lengthens_recompressed():
    clean = recompressed_duration_ps(100.0, 0.0)
    dirty = recompressed_duration_ps(100.0, 1e-25)
    assert dirty > clean
