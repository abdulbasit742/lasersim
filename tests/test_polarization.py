"""Validate Jones-calculus polarization optics."""
import numpy as np

from polarization import (
    H, V, qwp, hwp, polarizer, faraday_rotator, apply,
    ellipticity, n2_reduction, classify,
)


def test_qwp_makes_circular():
    out = qwp(np.pi / 4) @ H
    assert ellipticity(out) > 0.99
    assert classify(out) == "circular"


def test_hwp_rotates_linear():
    # HWP at 45 deg flips H -> V
    out = hwp(np.pi / 4) @ H
    assert abs(abs(out[1]) - 1.0) < 1e-9
    assert abs(out[0]) < 1e-9


def test_polarizer_blocks_crossed():
    out = polarizer(np.pi / 2) @ H   # vertical polarizer, horizontal input
    assert np.allclose(out, [0, 0], atol=1e-9)


def test_circular_reduces_n2():
    lin = H.copy()
    circ = qwp(np.pi / 4) @ H
    assert n2_reduction(circ) < n2_reduction(lin)
    assert np.isclose(n2_reduction(circ) / n2_reduction(lin), 2.0 / 3.0, rtol=1e-2)


def test_two_qwps_make_hwp_like():
    # Two QWPs at the same angle = one HWP
    out = apply([qwp(0.0), qwp(0.0)], H)
    ref = hwp(0.0) @ H
    # same polarization up to global phase
    assert np.isclose(abs(np.vdot(out, ref)), 1.0, atol=1e-6)


def test_faraday_rotates_45():
    out = faraday_rotator(np.pi / 4) @ H
    # should have rotated toward +45
    assert abs(out[0]) > 0 and abs(out[1]) > 0
