"""Validate the FROG diagnostic."""
import numpy as np

from frog import FROG


def test_trace_is_normalized():
    f = FROG(npts=64)
    _, _, trace = f.trace()
    assert np.isclose(trace.max(), 1.0)


def test_transform_limited_no_tilt():
    f = FROG(chirp=0.0, npts=64)
    assert abs(f.trace_tilt()) < 0.1


def test_chirp_produces_tilt():
    clean = FROG(chirp=0.0, npts=64).trace_tilt()
    chirped = FROG(chirp=0.5, npts=64).trace_tilt()
    assert abs(chirped) > abs(clean)


def test_trace_shape():
    f = FROG(npts=48)
    _, _, trace = f.trace()
    assert trace.shape == (48, 48)
