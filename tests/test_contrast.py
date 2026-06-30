"""Validate temporal pulse-contrast modeling."""
import numpy as np

from contrast import PulseContrast, PrePulse


def test_peak_normalized_to_one():
    pc = PulseContrast()
    _, prof = pc.profile()
    assert np.isclose(prof.max(), 1.0)


def test_contrast_better_than_pedestal():
    pc = PulseContrast(pedestal_level=1e-6)
    c = pc.contrast_at(-8.0)
    assert c > 1e4


def test_gate_improves_contrast():
    pc = PulseContrast(pedestal_level=1e-4)
    raw = pc.contrast_at(-6.0)
    gated = pc.contrast_at(-6.0, gate_contrast=1e3)
    assert gated >= raw


def test_prepulse_lowers_contrast_at_its_delay():
    pc = PulseContrast(pedestal_level=1e-9,
                       pre_pulses=[PrePulse(-2000, 1e-3)])
    c = pc.contrast_at(-2.0)
    assert c < 1e4
