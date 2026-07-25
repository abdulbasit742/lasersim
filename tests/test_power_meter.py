"""Power-meter head response, wavelength correction and uncertainty budget."""
import math

import pytest

import power_meter as pm


def test_thermopile_step_response_is_monotonic_and_converges():
    head = pm.ThermopileHead()
    steady = head.signal_V(10.0)
    assert head.signal_V(10.0, 0.0) == 0.0
    # one time constant -> 63.2 % of final
    assert head.signal_V(10.0, head.time_constant_s) == pytest.approx(steady * (1 - 1 / math.e), rel=1e-9)
    # long after, essentially the true reading
    assert head.signal_V(10.0, 20 * head.time_constant_s) == pytest.approx(steady, rel=1e-6)


def test_settling_time_scales_with_time_constant():
    head = pm.ThermopileHead(time_constant_s=1.0)
    assert head.settling_time_s(0.99) == pytest.approx(math.log(100.0), rel=1e-9)
    assert head.settling_time_s(0.999) > head.settling_time_s(0.99)
    with pytest.raises(ValueError):
        head.settling_time_s(1.0)


def test_power_density_and_damage_flag():
    head = pm.ThermopileHead(max_density_W_per_cm2=12.0)
    # 1 W into a 1 cm diameter spot -> 4/pi W/cm^2
    assert head.power_density_W_per_cm2(1.0, 10.0) == pytest.approx(4.0 / math.pi, rel=1e-9)
    assert head.is_density_safe(1.0, 10.0)
    # same power squeezed into 0.5 mm is not safe
    assert not head.is_density_safe(1.0, 0.5)
    assert head.is_within_range(5.0)
    assert not head.is_within_range(1e6)


def test_photodiode_responsivity_and_wavelength_correction():
    head = pm.PhotodiodeHead(calibration_lam_nm=1064.0)
    r1064 = head.responsivity_A_per_W(1064.0)
    r532 = head.responsivity_A_per_W(532.0)
    assert r1064 > r532 > 0.0
    # responsivity is linear in wavelength, so halving lambda doubles the correction
    assert head.wavelength_correction(1064.0) == pytest.approx(1.0, rel=1e-12)
    assert head.wavelength_correction(532.0) == pytest.approx(2.0, rel=1e-9)


def test_photodiode_saturation_clamps_current():
    head = pm.PhotodiodeHead(max_power_W=50e-3)
    assert not head.is_saturated(1e-3)
    assert head.is_saturated(1.0)
    # beyond the ceiling the head cannot report more current
    assert head.current_A(10.0, 1064.0) == pytest.approx(head.current_A(50e-3, 1064.0), rel=1e-12)


def test_pulse_energy_round_trip():
    # 1.28 J at 10 Hz reads as 12.8 W average
    assert pm.average_power_W(1.28, 10.0) == pytest.approx(12.8, rel=1e-12)
    assert pm.pulse_energy_J(12.8, 10.0) == pytest.approx(1.28, rel=1e-12)
    with pytest.raises(ValueError):
        pm.pulse_energy_J(1.0, 0.0)


def test_uncertainty_combines_in_quadrature():
    ub = pm.UncertaintyBudget(components={"a": 0.03, "b": 0.04})
    assert ub.combined_relative() == pytest.approx(0.05, rel=1e-12)
    assert ub.expanded_relative() == pytest.approx(0.10, rel=1e-12)
    assert ub.dominant() == "b"
    lo, hi = ub.interval_W(10.0)
    assert lo == pytest.approx(9.0, rel=1e-12)
    assert hi == pytest.approx(11.0, rel=1e-12)


def test_default_budget_is_dominated_by_calibration_and_bounded():
    ub = pm.UncertaintyBudget()
    combined = ub.combined_relative()
    assert combined >= max(ub.components.values())      # quadrature never shrinks
    assert combined <= sum(ub.components.values())      # and never exceeds the linear sum
    assert ub.dominant() == "calibration transfer"


def test_cli_entry_point_runs():
    import sys

    argv = sys.argv
    try:
        sys.argv = ["power_meter", "--power-W", "12.8", "--lam-nm", "1064", "--rep-rate-Hz", "10"]
        pm.main()
    finally:
        sys.argv = argv
