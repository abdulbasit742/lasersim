"""Validate wavefront / Strehl-ratio modeling."""
import numpy as np

from wavefront import Wavefront, zernike, ZERNIKES


def test_flat_wavefront_strehl_one():
    wf = Wavefront({})
    assert np.isclose(wf.rms_error(), 0.0)
    assert np.isclose(wf.strehl(), 1.0)


def test_more_aberration_lower_strehl():
    small = Wavefront({"defocus": 0.05})
    big = Wavefront({"defocus": 0.20})
    assert big.strehl() < small.strehl()


def test_rms_quadrature_sum():
    wf = Wavefront({"defocus": 0.03, "astig": 0.04})
    assert np.isclose(wf.rms_error(), 0.05, rtol=1e-9)   # 3-4-5


def test_strehl_between_0_and_1():
    wf = Wavefront({"coma": 0.1, "spherical": 0.1})
    assert 0.0 < wf.strehl() <= 1.0


def test_zernike_unknown_raises():
    R = np.array([0.5]); PHI = np.array([0.0])
    try:
        zernike("bogus", R, PHI)
        assert False
    except ValueError:
        pass
