"""Validate the autocorrelation diagnostic."""
import numpy as np

from autocorrelation import Autocorrelator, DECONV


def test_ac_wider_than_pulse():
    ac = Autocorrelator(pulse_fwhm_ps=200.0, shape="gaussian")
    t, trace = ac.trace()
    assert ac.fwhm(t, trace) > 200.0


def test_recovers_pulse_duration_gaussian():
    ac = Autocorrelator(pulse_fwhm_ps=200.0, shape="gaussian")
    assert np.isclose(ac.measured_duration(), 200.0, rtol=0.05)


def test_recovers_pulse_duration_sech2():
    ac = Autocorrelator(pulse_fwhm_ps=150.0, shape="sech2")
    assert np.isclose(ac.measured_duration(), 150.0, rtol=0.08)


def test_deconvolution_factor_ordering():
    assert DECONV["gaussian"] < DECONV["sech2"] < DECONV["lorentzian"]


def test_longer_pulse_wider_ac():
    short = Autocorrelator(pulse_fwhm_ps=100.0)
    long = Autocorrelator(pulse_fwhm_ps=300.0)
    ts, acs = short.trace(); tl, acl = long.trace()
    assert short.fwhm(tl, acl) > short.fwhm(ts, acs)
