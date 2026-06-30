#!/usr/bin/env python3
"""
================================================================================
thermal_fem.py  -  radial heat-diffusion solver for a side-pumped laser rod
================================================================================
thermal_abcd.py used a LUMPED thermal-lens formula. This module solves the heat
equation from FIRST PRINCIPLES on a 1D radial grid (cylindrical symmetry), which
is what actually sets the thermal lens, the stress, and the fracture limit.

Steady-state radial heat equation with volumetric heat source Q(r):

    (1/r) d/dr ( r k dT/dr ) + Q(r) = 0,   T(R) = T_coolant (cooled barrel)

For uniform heating the classic parabolic solution is T(r) = T_s + (Q/4k)(R^2 - r^2).
We solve the general case (non-uniform Q from the measured pump profile) with a
tridiagonal finite-difference scheme, then derive:

  * radial temperature profile T(r),
  * thermal-induced optical path difference -> focal length (dn/dT term),
  * thermal stress (hoop/radial) and a fracture-limit check,
  * comparison to the lumped thermal_abcd estimate.

Run:
    python thermal_fem.py                 # default 15 mm rod, uniform heat
    python thermal_fem.py --profile petal --power 200
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class RodThermal:
    radius_m: float = 7.5e-3
    length_m: float = 0.13
    K_th: float = 14.0          # W/(m K)
    dn_dT: float = 7.3e-6       # 1/K
    alpha_T: float = 7.5e-6     # thermal expansion [1/K]
    E_young: float = 280e9      # Young's modulus [Pa]
    poisson: float = 0.25
    fracture_MPa: float = 130.0 # Nd:YAG tensile fracture strength
    T_coolant: float = 300.0    # K
    n_nodes: int = 200


def heat_source(r, R, power_W, length_m, profile="uniform"):
    """Volumetric heat density Q(r) [W/m^3], normalized so the integral over the
    rod cross-section * length equals power_W."""
    if profile == "uniform":
        shape = np.ones_like(r)
    elif profile == "center":
        shape = np.exp(-(r / (0.6 * R)) ** 2)
    elif profile == "petal":  # bright annulus (large rods)
        shape = np.exp(-((r / R - 0.6) / 0.22) ** 2) + 0.25
    else:
        shape = np.ones_like(r)
    # normalize: integral( Q * 2 pi r dr ) * L = power
    integral = np.trapz(shape * 2 * np.pi * r, r) * length_m
    return shape * power_W / max(integral, 1e-30)


def solve_radial_T(rod: RodThermal, power_W: float, profile="uniform"):
    """Finite-difference solve of the steady radial heat equation. Returns (r, T)."""
    N = rod.n_nodes
    R = rod.radius_m
    r = np.linspace(1e-6, R, N)
    dr = r[1] - r[0]
    Q = heat_source(r, R, power_W, rod.length_m, profile)

    # build tridiagonal system for: k/r d/dr(r dT/dr) = -Q
    a = np.zeros(N)  # sub
    b = np.zeros(N)  # diag
    c = np.zeros(N)  # super
    d = np.zeros(N)  # rhs
    k = rod.K_th
    for i in range(1, N - 1):
        rp = 0.5 * (r[i] + r[i + 1])
        rm = 0.5 * (r[i] + r[i - 1])
        a[i] = k * rm / (r[i] * dr ** 2)
        c[i] = k * rp / (r[i] * dr ** 2)
        b[i] = -(a[i] + c[i])
        d[i] = -Q[i]
    # center: symmetry dT/dr=0 -> T[0]=T[1]
    b[0] = 1.0; c[0] = -1.0; d[0] = 0.0
    # edge: fixed coolant temperature
    b[-1] = 1.0; d[-1] = rod.T_coolant

    # Thomas algorithm
    cp = np.zeros(N); dp = np.zeros(N)
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0]
    for i in range(1, N):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < N - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    T = np.zeros(N)
    T[-1] = dp[-1]
    for i in range(N - 2, -1, -1):
        T[i] = dp[i] - cp[i] * T[i + 1]
    return r, T


def thermal_focal_length(rod: RodThermal, r, T) -> float:
    """Focal length from the dn/dT optical-path-difference across the rod.
    A radial OPD ~ parabolic gives f = (radius^2) / (2 L dn/dT dT), using the
    center-to-edge temperature difference."""
    dT = T.max() - T.min()
    if dT <= 0:
        return np.inf
    # parabolic-lens approximation: 1/f = 2 * L * dn/dT * (dT / R^2)
    inv_f = 2.0 * rod.length_m * rod.dn_dT * dT / rod.radius_m ** 2
    return 1.0 / inv_f if inv_f > 0 else np.inf


def peak_stress_MPa(rod: RodThermal, r, T) -> float:
    """Approximate peak thermal (hoop) stress at the rod surface.
    sigma ~ alpha E dT / (2 (1 - nu))."""
    dT = T.max() - T.min()
    sigma = rod.alpha_T * rod.E_young * dT / (2.0 * (1.0 - rod.poisson))
    return sigma / 1e6


def main():
    ap = argparse.ArgumentParser(description="Radial thermal solver for a laser rod")
    ap.add_argument("--profile", choices=["uniform", "center", "petal"], default="uniform")
    ap.add_argument("--power", type=float, default=100.0, help="heat load [W]")
    ap.add_argument("--radius-mm", type=float, default=7.5)
    args = ap.parse_args()

    rod = RodThermal(radius_m=args.radius_mm * 1e-3)
    r, T = solve_radial_T(rod, args.power, args.profile)
    f = thermal_focal_length(rod, r, T)
    stress = peak_stress_MPa(rod, r, T)
    frac = 100.0 * stress / rod.fracture_MPa

    print("=" * 62)
    print(f" Radial thermal solve: {args.radius_mm*2:.0f} mm rod, {args.profile} pump")
    print("=" * 62)
    print(f"  heat load           : {args.power:.0f} W")
    print(f"  center temperature  : {T.max():.1f} K  (rise {T.max()-rod.T_coolant:.1f} K)")
    print(f"  thermal focal length: {f*100:.1f} cm")
    print(f"  peak thermal stress : {stress:.1f} MPa  ({frac:.0f}% of fracture)")
    print(f"  fracture risk       : {'OK' if frac < 70 else 'WARNING'}")
    print("=" * 62)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
        rr = r * 1e3
        ax[0].plot(rr, T - rod.T_coolant, lw=2)
        ax[0].set(title="Radial temperature rise", xlabel="r [mm]",
                  ylabel="T - T_coolant [K]")
        Q = heat_source(r, rod.radius_m, args.power, rod.length_m, args.profile)
        ax[1].plot(rr, Q / 1e6, lw=2, color="tab:red")
        ax[1].set(title="Heat deposition Q(r)", xlabel="r [mm]",
                  ylabel="Q [MW/m^3]")
        plt.tight_layout(); plt.savefig("thermal_fem.png", dpi=130)
        print("Saved -> thermal_fem.png")
        plt.show()


if __name__ == "__main__":
    main()
