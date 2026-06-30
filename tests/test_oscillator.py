"""Validate the rate-equation oscillator models."""
import numpy as np
import pytest

from laser_platform import (
    Cavity, FourLevelLaser, ThreeLevelLaser, QSwitchActive, MultiModeLaser,
    li_curve, MODEL_REGISTRY,
)


def test_threshold_positive():
    cav = Cavity()
    assert cav.N_threshold > 0
    assert cav.Rp_threshold > 0


def test_below_threshold_no_lasing():
    # Pump below threshold -> steady-state photon density ~ 0.
    cav = Cavity(Rp=1.0)  # essentially unpumped
    _, S_ss = FourLevelLaser(cav).steady_state()
    assert S_ss == pytest.approx(0.0, abs=1e-6)


def test_above_threshold_lases():
    cav = Cavity()  # default Rp is well above threshold
    assert cav.r > 1.0
    _, S_ss = FourLevelLaser(cav).steady_state()
    assert S_ss > 0.0


def test_inversion_clamps_at_threshold():
    """CW steady-state inversion should equal threshold inversion."""
    cav = Cavity()
    N_ss, _ = FourLevelLaser(cav).steady_state()
    assert N_ss == pytest.approx(cav.N_threshold, rel=1e-9)


def test_li_curve_monotonic_above_threshold():
    cav = Cavity()
    rs, P = li_curve(cav)
    above = P[rs > 1.0]
    assert all(b >= a - 1e-9 for a, b in zip(above, above[1:]))


def test_relaxation_freq_zero_below_threshold():
    cav = Cavity(Rp=1.0)
    assert cav.relaxation_freq_hz() == 0.0


@pytest.mark.parametrize("name", sorted(MODEL_REGISTRY))
def test_every_model_integrates(name):
    """Every registered model should integrate without error and stay finite."""
    model = MODEL_REGISTRY[name]()
    # keep CI fast: shorten the long runs
    model.n_pts = min(model.n_pts, 3000)
    res = model.simulate()
    assert np.all(np.isfinite(res.y))
    assert res.y.shape[1] > 0


def test_qswitch_produces_pulse():
    res = QSwitchActive().simulate()
    assert res.extra["peak_power_W"] > 0
    assert res.extra["fwhm_ns"] >= 0


def test_multimode_picks_center_winner():
    """With a symmetric gain profile the center mode should win."""
    res = MultiModeLaser(n_modes=5).simulate()
    assert res.extra["winning_mode"] == 2
