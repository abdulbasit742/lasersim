"""Validate the dermatology model."""
import numpy as np

from dermatology import DermaTreatment


def test_relaxation_grows_with_particle_size():
    small = DermaTreatment(particle_diameter_nm=100)
    big = DermaTreatment(particle_diameter_nm=1000)
    assert big.thermal_relaxation_s() > small.thermal_relaxation_s()


def test_relaxation_quadratic_in_size():
    a = DermaTreatment(particle_diameter_nm=100).thermal_relaxation_s()
    b = DermaTreatment(particle_diameter_nm=200).thermal_relaxation_s()
    assert np.isclose(b / a, 4.0, rtol=1e-6)


def test_ps_pulse_is_photoacoustic():
    t = DermaTreatment(particle_diameter_nm=200, pulse_ps=200)
    assert t.is_photoacoustic()


def test_long_pulse_not_confined():
    t = DermaTreatment(particle_diameter_nm=200, pulse_ps=1e6)  # 1 us
    assert not t.is_photoacoustic()


def test_safe_window_ordered():
    lo, hi = DermaTreatment().safe_window()
    assert lo < hi
