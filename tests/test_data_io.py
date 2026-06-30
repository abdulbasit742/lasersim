"""Validate data import + super-Gaussian fitting."""
import numpy as np

from data_io import make_synthetic_beam, fit_beam, compare_to_model


def test_fit_recovers_super_gaussian_order():
    img = make_synthetic_beam(order=4, wx=60, wy=60, noise=0.0)
    fit = fit_beam(img)
    # should recover order near 4 and near-round beam
    assert 3.0 <= fit.order <= 5.5
    assert fit.ellipticity > 0.9


def test_fit_radii_positive():
    img = make_synthetic_beam(noise=0.02)
    fit = fit_beam(img)
    assert fit.wx > 0 and fit.wy > 0
    assert 0.0 <= fit.flatness <= 1.0


def test_compare_to_model_runs():
    ins = np.array([720.0])
    meas = np.array([1280.0])
    modeled, agree = compare_to_model(ins, meas, stored_energy_J=1.14,
                                      rod_diameter_cm=2.5)
    assert modeled[0] > ins[0]          # it amplified
    assert agree.shape == (1,)
