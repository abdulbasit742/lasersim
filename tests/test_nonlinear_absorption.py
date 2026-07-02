"""Validate two-photon / nonlinear absorption."""
import numpy as np

from nonlinear_absorption import NonlinearAbsorber


def test_transmission_drops_with_intensity():
    na = NonlinearAbsorber()
    L = 0.01
    assert na.transmission(1e14, L) < na.transmission(1e12, L)


def test_transmission_bounded():
    na = NonlinearAbsorber()
    for I in (1e11, 1e13, 1e15):
        T = na.transmission(I, 0.01)
        assert 0.0 < T <= 1.0


def test_longer_path_more_loss():
    na = NonlinearAbsorber()
    assert na.transmission(1e14, 0.05) < na.transmission(1e14, 0.005)


def test_crossover_intensity():
    na = NonlinearAbsorber()
    I = na.tpa_equals_linear_intensity()
    assert np.isclose(na.beta_m_per_W * I, na.alpha_per_m, rtol=1e-9)


def test_low_intensity_near_linear():
    na = NonlinearAbsorber()
    T = na.transmission(1e9, 0.01)
    assert np.isclose(T, np.exp(-na.alpha_per_m * 0.01), rtol=1e-3)
