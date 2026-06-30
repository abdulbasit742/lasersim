#!/usr/bin/env python3
"""
================================================================================
phase_matching.py  -  nonlinear-crystal phase matching & acceptance bandwidths
================================================================================
shg.py / thg.py / opcpa.py all ASSUMED perfect phase matching. In reality you
have to TUNE the crystal (angle or temperature) so the fundamental and harmonic
travel with matched phase velocities, and even then the matching only holds over
a finite ANGULAR, SPECTRAL, and THERMAL acceptance bandwidth. Exceed those and
conversion collapses via the sinc^2(dk L/2) factor. This module is the engine
that tells you how tightly you must control the crystal.

Model
-----
  Phase mismatch:   dk = k_2w - 2 k_w  (type-I SHG)
  Conversion:       eta ~ sinc^2(dk L / 2)
  Acceptance (FWHM) in any parameter p: where sinc^2 falls to 0.5, i.e.
      dk * L / 2 ~ 1.39, so the half-width in p is 2.78 / (L * |d(dk)/dp|).
We model angular, spectral, and thermal detuning with representative
sensitivity coefficients and report each acceptance bandwidth.

Run:
    python phase_matching.py
    python phase_matching.py --crystal-mm 12
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


def sinc2(x):
    """Normalized sinc^2 with sinc(0)=1; x is dk*L/2."""
    return np.sinc(x / np.pi) ** 2


@dataclass
class PhaseMatch:
    length_mm: float = 12.0
    # representative sensitivities of dk to each parameter (1/m per unit)
    dkd_angle_per_mrad: float = 250.0     # angular sensitivity [1/m per mrad]
    dkd_temp_per_K: float = 60.0          # thermal sensitivity [1/m per K]
    dkd_lambda_per_nm: float = 400.0      # spectral sensitivity [1/m per nm]

    @property
    def L(self):
        return self.length_mm * 1e-3

    def efficiency_vs_dk(self, dk):
        return sinc2(dk * self.L / 2.0)

    def acceptance(self, sensitivity_per_unit: float) -> float:
        """FWHM acceptance in the parameter whose dk-sensitivity is given.
        sinc^2 = 0.5 at dk L/2 = 1.3916 -> full width = 2*1.3916/(L*sens)."""
        return 2.0 * 1.3916 / (self.L * sensitivity_per_unit)

    def angular_acceptance_mrad(self):
        return self.acceptance(self.dkd_angle_per_mrad)

    def thermal_acceptance_K(self):
        return self.acceptance(self.dkd_temp_per_K)

    def spectral_acceptance_nm(self):
        return self.acceptance(self.dkd_lambda_per_nm)


def main():
    ap = argparse.ArgumentParser(description="Nonlinear crystal phase matching")
    ap.add_argument("--crystal-mm", type=float, default=12.0)
    args = ap.parse_args()

    pm = PhaseMatch(length_mm=args.crystal_mm)

    print("=" * 60)
    print(" Phase matching & acceptance bandwidths")
    print("=" * 60)
    print(f"  crystal length      : {args.crystal_mm:.0f} mm")
    print(f"  angular acceptance  : {pm.angular_acceptance_mrad():.3f} mrad (FWHM)")
    print(f"  thermal acceptance  : {pm.thermal_acceptance_K():.2f} K (FWHM)")
    print(f"  spectral acceptance : {pm.spectral_acceptance_nm():.3f} nm (FWHM)")
    print("-" * 60)
    print("  longer crystal -> higher conversion but TIGHTER acceptance.")
    print("=" * 60)

    if _HAVE_MPL:
        dks = np.linspace(-600, 600, 400)
        eta = [pm.efficiency_vs_dk(dk) for dk in dks]
        plt.figure(figsize=(8, 4.2))
        plt.plot(dks, eta, lw=2)
        plt.axhline(0.5, color="r", ls="--", label="half-max (acceptance edge)")
        plt.xlabel("phase mismatch dk [1/m]"); plt.ylabel("relative conversion")
        plt.title(f"sinc^2 phase-matching curve ({args.crystal_mm:.0f} mm)")
        plt.legend(); plt.tight_layout(); plt.savefig("phase_matching.png", dpi=130)
        print("Saved -> phase_matching.png")
        plt.show()


if __name__ == "__main__":
    main()
