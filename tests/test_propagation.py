"""Validate split-step self-focusing propagation."""
import numpy as np

from propagation import (
    Medium, Window, initial_field, split_step, bespalov_talanov_kmax,
)


def test_energy_conserved_low_power():
    """At negligible intensity the medium is ~linear; total power conserved."""
    med = Medium()
    win = Window(npix=128)
    E0 = initial_field(win, I0=1.0, ripple_amp=0.0)
    E_out, B, _ = split_step(E0, med, win, n_steps=50)
    p_in = np.sum(np.abs(E0) ** 2)
    p_out = np.sum(np.abs(E_out) ** 2)
    assert np.isclose(p_in, p_out, rtol=1e-3)
    assert B >= 0.0


def test_b_integral_scales_with_intensity():
    med = Medium()
    win = Window(npix=128)
    _, B1, _ = split_step(initial_field(win, I0=1e12), med, win, n_steps=60)
    _, B2, _ = split_step(initial_field(win, I0=2e12), med, win, n_steps=60)
    assert B2 > B1


def test_bespalov_talanov_positive():
    med = Medium()
    assert bespalov_talanov_kmax(med, 1e13) > 0
    assert bespalov_talanov_kmax(med, 0.0) == 0.0


def test_self_focusing_grows_peak():
    """High intensity + seeded ripple -> peak intensity should grow."""
    med = Medium()
    win = Window(npix=128)
    E0 = initial_field(win, I0=5e13, ripple_amp=0.1)
    _, _, peaks = split_step(E0, med, win, n_steps=120)
    assert peaks[-1] >= peaks[0]
