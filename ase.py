#!/usr/bin/env python3
"""
================================================================================
ase.py  -  amplified spontaneous emission (ASE) & parasitic-oscillation limit
================================================================================
Large-aperture, high-gain amplifiers (the 25 mm GM3/GM4 booster rods in the
paper) can't store unlimited energy: amplified spontaneous emission and
TRANSVERSE parasitic oscillation clamp the achievable single-pass gain. Photons
spontaneously emitted in the rod get amplified across the largest dimension; if
the transverse gain-length product gets too high, the rod self-lases sideways
and dumps the stored inversion before your real pulse arrives.

This module models:
  * ASE depopulation: effective upper-state lifetime shortens as gain rises
        1/tau_eff = 1/tau * (1 + ASE_factor(G))
  * the transverse gain-length product G_t = exp(sigma * N * d) across the rod
    diameter, and the classic parasitic threshold G_t * R_eff ~ 1,
  * the maximum storable inversion / gain before parasitics clamp it,
  * how much the paper's GM3/GM4 stored energy sits below that ceiling.

Run:
    python ase.py                  # GM3/GM4 booster rods
    python ase.py --diameter-mm 25 --gain 5
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class ASERod:
    diameter_m: float = 25e-3
    length_m: float = 0.13
    sigma: float = 2.8e-23        # stim. emission cross section [m^2]
    tau: float = 230e-6           # upper-state lifetime [s]
    n0: float = 1.82
    edge_reflectivity: float = 0.04   # residual Fresnel reflection at barrel
    f_sat: float = 0.3            # J/cm^2

    @property
    def radius_m(self):
        return self.diameter_m / 2.0

    def stored_fluence(self, stored_energy_J):
        area_cm2 = np.pi * (self.radius_m * 100) ** 2
        return stored_energy_J / area_cm2

    def longitudinal_gain(self, stored_energy_J):
        """Small-signal single-pass gain along the rod axis."""
        return np.exp(self.stored_fluence(stored_energy_J) / self.f_sat)

    def transverse_gain(self, stored_energy_J):
        """Gain across the DIAMETER (the parasitic path). Uses the same gain
        coefficient g0 = ln(G_axial)/L applied over the diameter."""
        g0 = np.log(self.longitudinal_gain(stored_energy_J)) / self.length_m
        return np.exp(g0 * self.diameter_m)

    def parasitic_margin(self, stored_energy_J):
        """Parasitic oscillation when transverse_gain * edge_reflectivity >= 1.
        Returns the loop gain; >=1 means the rod self-lases sideways."""
        return self.transverse_gain(stored_energy_J) * self.edge_reflectivity

    def ase_lifetime_factor(self, stored_energy_J):
        """Effective lifetime shortening from ASE. Grows with transverse gain."""
        Gt = self.transverse_gain(stored_energy_J)
        return 1.0 + 0.5 * (Gt - 1.0) / (Gt + 1.0)

    def max_storable_energy(self):
        """Stored energy at which parasitic loop gain hits 1 (the ceiling)."""
        Es = np.linspace(0.1, 10.0, 4000)
        margins = np.array([self.parasitic_margin(E) for E in Es])
        below = Es[margins < 1.0]
        return below.max() if below.size else 0.0


def main():
    ap = argparse.ArgumentParser(description="ASE & parasitic-oscillation limit")
    ap.add_argument("--diameter-mm", type=float, default=25.0)
    ap.add_argument("--stored", type=float, default=1.14,
                    help="stored energy [J] (paper GM3/GM4 = 1.14 J)")
    args = ap.parse_args()

    rod = ASERod(diameter_m=args.diameter_mm * 1e-3)
    E = args.stored
    G_ax = rod.longitudinal_gain(E)
    G_tr = rod.transverse_gain(E)
    margin = rod.parasitic_margin(E)
    E_max = rod.max_storable_energy()

    print("=" * 64)
    print(f" ASE / parasitic limit: {args.diameter_mm:.0f} mm rod")
    print("=" * 64)
    print(f"  stored energy        : {E:.2f} J")
    print(f"  axial single-pass gain: {G_ax:.2f}x")
    print(f"  transverse gain      : {G_tr:.2f}x (across diameter)")
    print(f"  parasitic loop gain  : {margin:.3f}  "
          f"({'SAFE' if margin < 1 else 'SELF-LASING'})")
    print(f"  ASE lifetime factor  : {rod.ase_lifetime_factor(E):.2f}x shorter")
    print(f"  max storable energy  : {E_max:.2f} J  "
          f"(paper runs at {100*E/E_max:.0f}% of ceiling)")
    print("=" * 64)

    if _HAVE_MPL:
        Es = np.linspace(0.2, max(E_max * 1.3, 3.0), 200)
        margins = [rod.parasitic_margin(e) for e in Es]
        plt.plot(Es, margins, lw=2)
        plt.axhline(1.0, color="r", ls="--", label="parasitic threshold")
        plt.axvline(E, color="tab:green", ls=":", label=f"paper ({E} J)")
        plt.xlabel("stored energy [J]"); plt.ylabel("parasitic loop gain")
        plt.title(f"Parasitic oscillation limit, {args.diameter_mm:.0f} mm rod")
        plt.legend(); plt.tight_layout(); plt.savefig("ase.png", dpi=130)
        print("Saved -> ase.png")
        plt.show()


if __name__ == "__main__":
    main()
