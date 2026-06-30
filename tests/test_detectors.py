"""Validate detector response."""
import numpy as np

from detectors import Photodiode, EnergyMeter


def test_responsivity_increases_with_wavelength():
    pd = Photodiode()
    assert pd.responsivity(1064) > pd.responsivity(532)


def test_low_power_linear():
    pd = Photodiode()
    assert pd.is_linear(1e-4)


def test_high_power_saturates():
    pd = Photodiode()
    assert not pd.is_linear(1.0)


def test_current_saturates_below_ideal():
    pd = Photodiode()
    ideal = pd.responsivity(1064) * 1.0
    assert pd.current_A(1.0, 1064) < ideal


def test_energy_meter_damage_flag():
    em = EnergyMeter(damage_threshold_J=2.0)
    assert em.is_safe(1.28)
    assert not em.is_safe(3.0)


def test_energy_meter_linear_signal():
    em = EnergyMeter(calibration_V_per_J=1e4)
    assert np.isclose(em.signal_V(1.0), 1e4)
