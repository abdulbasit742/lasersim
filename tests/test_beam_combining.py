"""Validate beam combining."""
import numpy as np

from beam_combining import BeamCombiner


def test_perfect_phase_full_efficiency():
    bc = BeamCombiner(mode="coherent", phase_err_rad=0.0)
    assert np.isclose(bc.efficiency(), 1.0)


def test_phase_error_lowers_efficiency():
    good = BeamCombiner(phase_err_rad=0.1)
    bad = BeamCombiner(phase_err_rad=0.8)
    assert bad.efficiency() < good.efficiency()


def test_more_channels_more_energy():
    bc = BeamCombiner()
    assert bc.combined_energy_J(8) > bc.combined_energy_J(2)


def test_channels_for_target_scales():
    bc = BeamCombiner()
    assert bc.channels_for_target(20) > bc.channels_for_target(5)


def test_spectral_mode_uses_grating_eff():
    bc = BeamCombiner(mode="spectral", spectral_eff=0.95)
    assert np.isclose(bc.efficiency(), 0.95)
