"""Validate the 808 nm pump diode-bar model."""
import numpy as np

from pump_diode import DiodeBar


def test_no_output_below_threshold():
    d = DiodeBar()
    assert d.optical_power(d.i_threshold_A - 1) == 0.0


def test_power_increases_with_current():
    d = DiodeBar()
    assert d.optical_power(120) > d.optical_power(60)


def test_peak_power_near_paper_value():
    d = DiodeBar()
    # ~16.22 kW at 120 A
    assert abs(d.optical_power(120) / 1e3 - 16.22) < 1.0


def test_wavelength_drifts_up_with_current():
    d = DiodeBar()
    assert d.wavelength(120) >= d.wavelength(20)


def test_absorption_max_at_peak():
    d = DiodeBar()
    assert np.isclose(d.absorption(808.0), 1.0)
    assert d.absorption(812.0) < 1.0
