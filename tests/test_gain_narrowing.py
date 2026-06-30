"""Validate spectral gain narrowing."""
import numpy as np

from gain_narrowing import (
    GainLine, amplify_spectrum, spectral_fwhm, transform_limited_ps,
)


def _grid(line):
    span = 5.0 * line.delta_nu
    return np.linspace(line.nu0 - span, line.nu0 + span, 4000)


def test_spectrum_narrows_with_passes():
    line = GainLine()
    nu = _grid(line)
    sigma = (3.0 * line.delta_nu) / 2.3548
    S_in = np.exp(-0.5 * ((nu - line.nu0) / sigma) ** 2)
    S_out = amplify_spectrum(line, S_in, nu, n_passes=6, g0=5.0)
    assert spectral_fwhm(nu, S_out) < spectral_fwhm(nu, S_in)


def test_more_passes_narrower():
    line = GainLine()
    nu = _grid(line)
    sigma = (3.0 * line.delta_nu) / 2.3548
    S_in = np.exp(-0.5 * ((nu - line.nu0) / sigma) ** 2)
    s2 = amplify_spectrum(line, S_in, nu, 2, 5.0)
    s8 = amplify_spectrum(line, S_in, nu, 8, 5.0)
    assert spectral_fwhm(nu, s8) < spectral_fwhm(nu, s2)


def test_transform_limit_inverse_bandwidth():
    # narrower spectrum -> longer TL pulse
    assert transform_limited_ps(1e11) > transform_limited_ps(1e12)


def test_bandwidth_conversion_positive():
    line = GainLine()
    assert line.delta_nu > 0
