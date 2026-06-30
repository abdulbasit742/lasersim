"""Validate nonlinear-crystal walk-off."""
import numpy as np

from walkoff import WalkOff


def test_slip_grows_with_length():
    short = WalkOff(crystal_mm=5)
    long = WalkOff(crystal_mm=20)
    assert long.temporal_walkoff_ps() > short.temporal_walkoff_ps()


def test_overlap_drops_with_length():
    short = WalkOff(crystal_mm=5)
    long = WalkOff(crystal_mm=50)
    assert long.overlap_fraction() < short.overlap_fraction()


def test_walkoff_length_matches_pulse():
    w = WalkOff(gvm_fs_per_mm=80, pulse_ps=200)
    L = w.temporal_walkoff_length_mm()
    wL = WalkOff(gvm_fs_per_mm=80, pulse_ps=200, crystal_mm=L)
    assert np.isclose(wL.temporal_walkoff_ps(), 200, rtol=1e-6)


def test_spatial_separation_grows():
    short = WalkOff(crystal_mm=5)
    long = WalkOff(crystal_mm=20)
    assert long.spatial_separation_um() > short.spatial_separation_um()


def test_overlap_bounded():
    for L in (1, 12, 100):
        f = WalkOff(crystal_mm=L).overlap_fraction()
        assert 0.0 <= f <= 1.0
