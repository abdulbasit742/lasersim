"""Validate stimulated Raman scattering model."""
import numpy as np

from raman import SRS, MEDIA, stokes_wavelength_nm, G_THRESHOLD


def test_stokes_is_redshifted():
    s = stokes_wavelength_nm(1064.0, 440.0)
    assert s > 1064.0    # Stokes is longer wavelength


def test_gain_scales_with_intensity_and_length():
    srs = SRS(MEDIA["air"])
    assert srs.gain_exponent(1e14, 2) > srs.gain_exponent(1e13, 2)
    assert srs.gain_exponent(1e13, 4) > srs.gain_exponent(1e13, 2)


def test_threshold_crossing():
    srs = SRS(MEDIA["methane"])
    I_th = srs.threshold_intensity(2.0)
    assert srs.above_threshold(I_th * 1.1, 2.0)
    assert not srs.above_threshold(I_th * 0.5, 2.0)


def test_threshold_intensity_gives_threshold_gain():
    srs = SRS(MEDIA["water"])
    I_th = srs.threshold_intensity(3.0)
    assert np.isclose(srs.gain_exponent(I_th, 3.0), G_THRESHOLD, rtol=1e-6)


def test_methane_higher_gain_than_air():
    assert MEDIA["methane"].g_raman_m_per_W > MEDIA["air"].g_raman_m_per_W
