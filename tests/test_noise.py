"""Validate the RIN / noise model."""
import numpy as np

from noise import NoiseModel


def test_more_photons_lower_shot_noise():
    lo = NoiseModel(photons_per_pulse=1e15)
    hi = NoiseModel(photons_per_pulse=1e18)
    assert hi.shot_noise_rin() < lo.shot_noise_rin()


def test_transfer_peaks_at_relaxation():
    nm = NoiseModel(f_relax_khz=50, damping=0.1)
    f0 = 50e3
    assert nm.transfer(f0) > nm.transfer(f0 * 10)
    assert nm.transfer(f0) > nm.transfer(f0 / 10)


def test_resonant_amplification_positive():
    nm = NoiseModel(damping=0.1)
    assert nm.peak_amplification_dB() > 0


def test_output_rin_above_shot_floor():
    nm = NoiseModel()
    assert nm.output_rin(1e3) >= nm.shot_noise_rin()


def test_more_damping_less_peak():
    light = NoiseModel(damping=0.05)
    heavy = NoiseModel(damping=0.5)
    assert light.peak_amplification_dB() > heavy.peak_amplification_dB()
