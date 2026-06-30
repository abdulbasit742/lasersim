"""Validate timing-jitter / synchronization model."""
from jitter import SyncModel


def test_no_jitter_no_fluctuation():
    m = SyncModel()
    assert m.energy_rms(0.0) < 1e-9


def test_more_jitter_more_rms():
    m = SyncModel()
    assert m.energy_rms(40) > m.energy_rms(5)


def test_gain_peaks_at_zero_offset():
    m = SyncModel()
    assert m.gain_factor(0.0) == 1.0
    assert m.gain_factor(100.0) < 1.0


def test_max_jitter_within_spec():
    m = SyncModel()
    j = m.max_jitter_for_spec(0.011)
    assert m.energy_rms(j) <= 0.011 + 2e-3


def test_shorter_pump_more_jitter_sensitive():
    short = SyncModel(pump_fwhm_ps=50.0)
    long = SyncModel(pump_fwhm_ps=400.0)
    assert short.energy_rms(20) > long.energy_rms(20)
