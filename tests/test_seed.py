"""Validate the microchip seed oscillator."""
from seed import MicrochipSeed


def test_shorter_cavity_shorter_pulse():
    short = MicrochipSeed(cavity_mm=1.0)
    long = MicrochipSeed(cavity_mm=8.0)
    assert short.pulse_duration_s() < long.pulse_duration_s()


def test_pulse_energy_positive():
    assert MicrochipSeed().pulse_energy_J() > 0


def test_peak_power_consistent():
    s = MicrochipSeed()
    assert abs(s.peak_power_W() - s.pulse_energy_J() / s.pulse_duration_s()) < 1e-6


def test_higher_inversion_shorter_pulse():
    lo = MicrochipSeed(inversion_ratio=2.0)
    hi = MicrochipSeed(inversion_ratio=10.0)
    assert hi.pulse_duration_s() < lo.pulse_duration_s()


def test_round_trip_scales_with_length():
    import numpy as np
    a = MicrochipSeed(cavity_mm=2.0).round_trip_s
    b = MicrochipSeed(cavity_mm=4.0).round_trip_s
    assert np.isclose(b / a, 2.0, rtol=1e-9)
