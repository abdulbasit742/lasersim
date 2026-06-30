#!/usr/bin/env python3
"""
================================================================================
shg.py  -  second-harmonic generation: 1064 nm -> 532 nm
================================================================================
The 1.28 J / 200 ps Nd:YAG fundamental can be frequency-doubled to green (532 nm)
in a nonlinear crystal (KDP/KTP/LBO). The paper's own reference [21] reports both
1064 and 532 nm output. Green high-energy ps light is prized for material
processing, ranging, and as an OPCPA pump. No other module covered the harmonic
stage, so this adds it.

Physics (plane-wave, type-I SHG)
--------------------------------
  Conversion efficiency vs. drive (non-depleted -> depleted):
      eta = tanh^2( L * sqrt( 2 * omega^2 * deff^2 * I_w / (n^2 * eps0 * c^3) ) )
  with a phase-mismatch sinc^2(dk L / 2) reduction when not perfectly matched.

Reports the green conversion efficiency, output energy, and how mismatch /
intensity / crystal length trade off.

Run:
    python shg.py                       # double the 1.28 J fundamental
    python shg.py --energy-J 1.28 --tau-ps 200 --crystal-mm 12
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

C0 = 2.99792458e8
EPS0 = 8.8541878128e-12


@dataclass
class SHGCrystal:
    name: str = "KDP"
    length_mm: float = 12.0
    deff_pm_V: float = 0.39      # effective nonlinearity [pm/V] (KDP type-I)
    n: float = 1.50              # refractive index near 1 um
    lam_fund_nm: float = 1064.0
    beam_radius_cm: float = 0.8

    @property
    def omega(self) -> float:
        return 2.0 * np.pi * C0 / (self.lam_fund_nm * 1e-9)

    def kappa(self) -> float:
        """SHG drive coefficient: eta = tanh^2(kappa * sqrt(I) * L)."""
        deff = self.deff_pm_V * 1e-12
        num = 2.0 * self.omega ** 2 * deff ** 2
        den = self.n ** 3 * EPS0 * C0 ** 3
        return np.sqrt(num / den)

    def efficiency(self, intensity_W_m2: float, dk: float = 0.0) -> float:
        L = self.length_mm * 1e-3
        drive = self.kappa() * np.sqrt(max(intensity_W_m2, 0.0)) * L
        eta = np.tanh(drive) ** 2
        if dk != 0.0:
            eta *= np.sinc(dk * L / (2.0 * np.pi)) ** 2   # numpy sinc = sin(pi x)/(pi x)
        return float(min(eta, 1.0))


def peak_intensity(energy_J, tau_s, radius_cm):
    area_m2 = np.pi * (radius_cm * 1e-2) ** 2
    peak_power = 0.94 * energy_J / tau_s     # Gaussian-pulse peak power
    return peak_power / area_m2


def main():
    ap = argparse.ArgumentParser(description="Second-harmonic generation 1064->532")
    ap.add_argument("--energy-J", type=float, default=1.28)
    ap.add_argument("--tau-ps", type=float, default=200.0)
    ap.add_argument("--crystal-mm", type=float, default=12.0)
    ap.add_argument("--radius-cm", type=float, default=0.8)
    args = ap.parse_args()

    crystal = SHGCrystal(length_mm=args.crystal_mm, beam_radius_cm=args.radius_cm)
    I = peak_intensity(args.energy_J, args.tau_ps * 1e-12, args.radius_cm)
    eta = crystal.efficiency(I)
    e_green = eta * args.energy_J

    print("=" * 62)
    print(" Second-harmonic generation: 1064 nm -> 532 nm")
    print("=" * 62)
    print(f"  fundamental energy  : {args.energy_J*1e3:.0f} mJ @ {args.tau_ps:.0f} ps")
    print(f"  peak intensity      : {I/1e13:.2f} x10^13 W/m^2 "
          f"({I/1e9/1e4:.2f} GW/cm^2)")
    print(f"  crystal             : {crystal.name}, {args.crystal_mm:.0f} mm")
    print(f"  conversion efficiency: {eta*100:.1f} %")
    print(f"  green output (532 nm): {e_green*1e3:.0f} mJ")
    print("=" * 62)

    if _HAVE_MPL:
        Is = np.linspace(1e12, 5e13, 200)
        eta_curve = [crystal.efficiency(i) for i in Is]
        plt.figure(figsize=(8, 4.2))
        plt.plot(Is / 1e13, np.array(eta_curve) * 100, lw=2)
        plt.axvline(I / 1e13, color="tab:green", ls="--",
                    label=f"this system ({eta*100:.0f}%)")
        plt.xlabel("peak intensity [x10^13 W/m^2]")
        plt.ylabel("SHG efficiency [%]")
        plt.title(f"1064->532 nm conversion ({crystal.name}, {args.crystal_mm:.0f} mm)")
        plt.legend(); plt.tight_layout(); plt.savefig("shg.png", dpi=130)
        print("Saved -> shg.png")
        plt.show()


if __name__ == "__main__":
    main()
