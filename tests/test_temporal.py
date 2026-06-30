"""Validate time-resolved pulse amplification."""
import numpy as np

from temporal import PulseGrid, frantz_nodvik_temporal, pulse_metrics


def test_energy_gain_above_one():
    grid = PulseGrid()
    t = grid.time_axis()
    phi = grid.input_shape()
    _, egain = frantz_nodvik_temporal(phi, t, G0=3.0, U_sat=1.0, E_in_J=0.2)
    assert egain > 1.0


def test_leading_edge_advantage_shifts_center_forward():
    """Gain saturation should pull the pulse center-of-mass earlier in time."""
    grid = PulseGrid()
    t = grid.time_axis()
    phi = grid.input_shape()
    flux_out, _ = frantz_nodvik_temporal(phi, t, G0=5.0, U_sat=1.0, E_in_J=0.5)
    flux_in = phi / np.trapz(phi, t) * 0.5
    com_in, _ = pulse_metrics(t, flux_in)
    com_out, _ = pulse_metrics(t, flux_out)
    assert com_out <= com_in + 1e-9   # advances (or at worst unchanged)


def test_higher_gain_more_energy():
    grid = PulseGrid()
    t = grid.time_axis()
    phi = grid.input_shape()
    _, g_low = frantz_nodvik_temporal(phi, t, G0=2.0, U_sat=1.0, E_in_J=0.2)
    _, g_high = frantz_nodvik_temporal(phi, t, G0=6.0, U_sat=1.0, E_in_J=0.2)
    assert g_high > g_low
