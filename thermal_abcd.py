#!/usr/bin/env python3
"""
================================================================================
thermal_abcd.py  -  thermal lensing + ABCD ray-matrix cavity solver
================================================================================
Diode-pumped rods heat up. The deposited heat sets up a radial temperature
gradient, and through dn/dT the rod acts like a positive lens (thermal lens).
That lens changes the cavity stability and the TEM00 mode size, and it shifts
as pump power changes (which is why the NILOP paper had to re-optimize spatial
filter positions at full pump).

This module:
  1. Computes the thermal-lens focal length f_th of a side-pumped rod from
     deposited heat, thermal conductivity, dn/dT, and stress-optic terms.
  2. Builds ABCD ray-transfer matrices for free space, thin lenses, the thermal
     lens, and curved mirrors.
  3. Solves a two-mirror cavity for stability (|(A+D)/2| <= 1) and the Gaussian
     mode (1/e^2) spot size at any reference plane.

Run directly:
    python thermal_abcd.py                 # sweep pump power -> f_th, mode size
    python thermal_abcd.py --P 200         # single heat load in watts
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

LAMBDA = 1064e-9   # m


# ==============================================================================
# THERMAL LENS
# ==============================================================================
@dataclass
class ThermalRod:
    """Defaults ~ Nd:YAG rod."""
    radius_m: float = 7.5e-3      # rod radius (15 mm dia)
    length_m: float = 0.13        # rod length
    K_th: float = 14.0            # thermal conductivity [W/(m K)]
    dn_dT: float = 7.3e-6         # thermo-optic coefficient [1/K]
    n0: float = 1.82
    eta_heat: float = 0.30        # fraction of pump power -> heat
    Cr_phi: float = 0.017         # stress-optic contribution factor (lumped)

    def focal_length(self, P_pump_W: float) -> float:
        """Thermal-lens focal length [m] for absorbed pump power P_pump_W.
        Classic Koechner result:
            1/f_th = (P_heat / (2*pi*K*A)) * ( dn/dT + (n0^3 a_T C) + ... )
        We lump the dn/dT term (dominant) plus a stress-optic correction.
        """
        P_heat = self.eta_heat * P_pump_W
        A = np.pi * self.radius_m ** 2
        inv_f = (P_heat / (2.0 * self.K_th * A)) * (self.dn_dT + self.Cr_phi)
        if inv_f <= 0:
            return np.inf
        return 1.0 / inv_f

    def dioptric_power(self, P_pump_W: float) -> float:
        f = self.focal_length(P_pump_W)
        return 0.0 if np.isinf(f) else 1.0 / f


# ==============================================================================
# ABCD RAY MATRICES
# ==============================================================================
def M_space(d: float) -> np.ndarray:
    return np.array([[1.0, d], [0.0, 1.0]])


def M_lens(f: float) -> np.ndarray:
    if np.isinf(f):
        return np.eye(2)
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def M_mirror(Rcurv: float) -> np.ndarray:
    """Curved mirror, radius of curvature R (concave R>0). Acts as f = R/2."""
    if np.isinf(Rcurv):
        return np.eye(2)
    return M_lens(Rcurv / 2.0)


def chain(*mats: np.ndarray) -> np.ndarray:
    """Multiply ABCD matrices in beam-propagation order (last applied = leftmost)."""
    out = np.eye(2)
    for m in mats:
        out = m @ out
    return out


# ==============================================================================
# CAVITY
# ==============================================================================
@dataclass
class TwoMirrorCavity:
    """Linear cavity: M1 - space d1 - thermal lens (rod) - space d2 - M2."""
    R1: float           # mirror 1 radius of curvature [m] (inf = flat)
    R2: float           # mirror 2 radius of curvature [m]
    d1: float           # M1 -> rod distance [m]
    d2: float           # rod -> M2 distance [m]
    rod: ThermalRod

    def round_trip(self, P_pump_W: float) -> np.ndarray:
        f = self.rod.focal_length(P_pump_W)
        # start at M1, go to M2 and back
        return chain(
            M_mirror(self.R1),
            M_space(self.d1), M_lens(f), M_space(self.d2),
            M_mirror(self.R2),
            M_space(self.d2), M_lens(f), M_space(self.d1),
        )

    def stability(self, P_pump_W: float) -> float:
        """Stability parameter m = (A+D)/2. |m| <= 1 -> stable."""
        M = self.round_trip(P_pump_W)
        return 0.5 * (M[0, 0] + M[1, 1])

    def is_stable(self, P_pump_W: float) -> bool:
        return abs(self.stability(P_pump_W)) <= 1.0

    def mode_radius(self, P_pump_W: float) -> float:
        """TEM00 1/e^2 mode radius [m] at M1 from the round-trip ABCD matrix.
        Returns nan if cavity is unstable."""
        M = self.round_trip(P_pump_W)
        A, B, D = M[0, 0], M[0, 1], M[1, 1]
        m = 0.5 * (A + D)
        if abs(m) > 1.0:
            return float("nan")
        sin2 = 1.0 - m * m
        if sin2 <= 0 or B == 0:
            return float("nan")
        w2 = (LAMBDA / np.pi) * abs(B) / np.sqrt(sin2)
        return np.sqrt(w2)


def diode_current_to_pump(I_A: float, peak_kW_at_120A: float = 16.22) -> float:
    """Crude linear map from diode current to deposited pump power proxy [W].
    Scales the paper's 16.22 kW peak diode power at 120 A by duty cycle.
    200 us pulse at 10 Hz -> duty ~2e-3 -> avg ~ peak * duty."""
    duty = 200e-6 * 10.0
    peak_W = peak_kW_at_120A * 1e3 * (I_A / 120.0)
    return peak_W * duty


def main():
    ap = argparse.ArgumentParser(description="Thermal lens + ABCD cavity solver")
    ap.add_argument("--P", type=float, default=None,
                    help="absorbed pump power [W] for a single point")
    args = ap.parse_args()

    rod = ThermalRod()
    cav = TwoMirrorCavity(R1=np.inf, R2=5.0, d1=0.15, d2=0.15, rod=rod)

    if args.P is not None:
        f = rod.focal_length(args.P)
        print(f"P_pump = {args.P:.1f} W -> f_th = {f*100:.1f} cm, "
              f"stability m = {cav.stability(args.P):+.3f}, "
              f"mode radius = {cav.mode_radius(args.P)*1e3:.3f} mm "
              f"({'stable' if cav.is_stable(args.P) else 'UNSTABLE'})")
        return

    Ps = np.linspace(20, 400, 60)
    f_th = np.array([rod.focal_length(P) for P in Ps])
    m = np.array([cav.stability(P) for P in Ps])
    w = np.array([cav.mode_radius(P) for P in Ps])

    print("=" * 60)
    print(" Thermal lens + cavity stability sweep (Nd:YAG, 15 mm rod)")
    print("=" * 60)
    for P in (50, 100, 200, 300):
        print(f"  P={P:>4} W  f_th={rod.focal_length(P)*100:6.1f} cm  "
              f"m={cav.stability(P):+.3f}  "
              f"{'stable' if cav.is_stable(P) else 'UNSTABLE'}")
    print("=" * 60)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
        ax[0].plot(Ps, f_th * 100, lw=2)
        ax[0].set(title="Thermal lens focal length", xlabel="P_pump [W]",
                  ylabel="f_th [cm]")
        ax[1].plot(Ps, m, lw=2)
        ax[1].axhspan(-1, 1, color="tab:green", alpha=0.15, label="stable")
        ax[1].axhline(1, color="r", ls="--"); ax[1].axhline(-1, color="r", ls="--")
        ax[1].set(title="Cavity stability (A+D)/2", xlabel="P_pump [W]",
                  ylabel="m"); ax[1].legend()
        ax[2].plot(Ps, w * 1e3, lw=2, color="tab:purple")
        ax[2].set(title="TEM00 mode radius at M1", xlabel="P_pump [W]",
                  ylabel="w [mm]")
        plt.tight_layout()
        plt.savefig("thermal_abcd.png", dpi=130)
        print("Saved -> thermal_abcd.png")
        plt.show()


if __name__ == "__main__":
    main()
