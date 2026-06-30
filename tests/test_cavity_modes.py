"""Validate longitudinal cavity-mode model."""
import numpy as np

from cavity_modes import CavityModes


def test_short_cavity_larger_fsr():
    short = CavityModes(length_mm=1)
    long = CavityModes(length_mm=100)
    assert short.fsr_GHz() > long.fsr_GHz()


def test_fsr_inverse_length():
    a = CavityModes(length_mm=2).fsr_GHz()
    b = CavityModes(length_mm=4).fsr_GHz()
    assert np.isclose(a / b, 2.0, rtol=1e-9)


def test_microchip_single_mode():
    # very short cavity -> single longitudinal mode
    cm = CavityModes(length_mm=1.0, gain_bandwidth_GHz=120)
    assert cm.is_single_mode()


def test_long_cavity_multimode():
    cm = CavityModes(length_mm=100, gain_bandwidth_GHz=120)
    assert cm.mode_count() > 1


def test_coherence_length_positive():
    assert CavityModes().coherence_length_m() > 0
