"""Validate the radial thermal-diffusion solver."""
import numpy as np

from thermal_fem import RodThermal, solve_radial_T, thermal_focal_length, peak_stress_MPa


def test_center_hotter_than_edge():
    rod = RodThermal()
    r, T = solve_radial_T(rod, power_W=100.0, profile="uniform")
    assert T[0] > T[-1]                      # center hotter than cooled barrel
    assert np.isclose(T[-1], rod.T_coolant, atol=1e-6)


def test_parabolic_profile_matches_analytic():
    """Uniform heating -> parabolic T(r). Check center rise vs Q R^2 / 4k."""
    rod = RodThermal(n_nodes=400)
    P = 100.0
    r, T = solve_radial_T(rod, P, "uniform")
    R = rod.radius_m
    Q = P / (np.pi * R ** 2 * rod.length_m)        # uniform volumetric density
    analytic_rise = Q * R ** 2 / (4.0 * rod.K_th)
    assert np.isclose(T[0] - rod.T_coolant, analytic_rise, rtol=0.05)


def test_focal_length_shrinks_with_power():
    rod = RodThermal()
    r1, T1 = solve_radial_T(rod, 50.0)
    r2, T2 = solve_radial_T(rod, 200.0)
    assert thermal_focal_length(rod, r2, T2) < thermal_focal_length(rod, r1, T1)


def test_stress_increases_with_power():
    rod = RodThermal()
    _, T1 = solve_radial_T(rod, 50.0)
    _, T2 = solve_radial_T(rod, 200.0)
    assert peak_stress_MPa(rod, None, T2) > peak_stress_MPa(rod, None, T1)
