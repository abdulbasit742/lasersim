"""Validate Sellmeier dispersion."""
import numpy as np

from dispersion import MATERIALS


def test_fused_silica_index_near_known():
    # fused silica n ~ 1.45 at 1064 nm
    n = MATERIALS["fused_silica"].n(1064.0)
    assert 1.44 < n < 1.46


def test_yag_index_reasonable():
    n = MATERIALS["YAG"].n(1064.0)
    assert 1.80 < n < 1.84


def test_group_index_exceeds_phase_index():
    s = MATERIALS["fused_silica"]
    assert s.group_index(1064.0) > s.n(1064.0)


def test_index_decreases_with_wavelength_normal():
    # normal dispersion: n drops as wavelength rises (visible-NIR)
    s = MATERIALS["fused_silica"]
    assert s.n(1500.0) < s.n(500.0)


def test_gvd_is_finite():
    for s in MATERIALS.values():
        assert np.isfinite(s.gvd_ps_nm_km(1064.0))
