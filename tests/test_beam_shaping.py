"""Validate serrated-aperture + spatial-filter beam shaping."""
import pytest

from beam_shaping import run_pipeline


def test_transmissions_in_expected_range():
    _, _, _, _, _, m = run_pipeline(pinhole_um=110.0)
    # SA clips ~20% -> ~80% pass; SF passes most of the energy
    assert 0.6 <= m["SA_transmission"] <= 0.95
    assert 0.5 <= m["SF_transmission"] <= 1.0


def test_spatial_filter_reduces_ripple():
    """Core modulation depth should drop after spatial filtering."""
    _, _, _, _, _, m = run_pipeline(pinhole_um=110.0)
    assert m["ripple_out"] <= m["ripple_in"] + 1e-6


def test_smaller_pinhole_passes_less_energy():
    _, _, _, _, _, m_small = run_pipeline(pinhole_um=60.0)
    _, _, _, _, _, m_big = run_pipeline(pinhole_um=160.0)
    assert m_small["SF_transmission"] <= m_big["SF_transmission"] + 1e-6
