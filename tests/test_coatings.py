"""Validate thin-film coating reflectivity."""
import numpy as np

from coatings import reflectivity, ar_single, hr_stack


def test_ar_reduces_reflection():
    n_sub = 1.52
    bare = ((1 - n_sub) / (1 + n_sub)) ** 2
    ar = ar_single(1064.0, np.sqrt(n_sub), n_sub)
    R = reflectivity(ar, 1064.0, n_substrate=n_sub)
    assert R < bare


def test_ideal_ar_near_zero():
    n_sub = 1.52
    ar = ar_single(1064.0, np.sqrt(n_sub), n_sub)
    R = reflectivity(ar, 1064.0, n_substrate=n_sub)
    assert R < 1e-3


def test_hr_stack_high_reflectivity():
    hr = hr_stack(1064.0, 2.30, 1.45, pairs=15)
    R = reflectivity(hr, 1064.0, n_substrate=1.52)
    assert R > 0.99


def test_more_pairs_higher_reflectivity():
    few = reflectivity(hr_stack(1064.0, 2.3, 1.45, 4), 1064.0, n_substrate=1.52)
    many = reflectivity(hr_stack(1064.0, 2.3, 1.45, 20), 1064.0, n_substrate=1.52)
    assert many > few


def test_reflectivity_bounded():
    hr = hr_stack(1064.0, 2.3, 1.45, 10)
    for lam in (900, 1064, 1300):
        R = reflectivity(hr, lam, n_substrate=1.52)
        assert 0.0 <= R <= 1.0
