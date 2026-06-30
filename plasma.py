#!/usr/bin/env python3
"""
================================================================================
plasma.py  -  laser-plasma interaction & soft X-ray generation
================================================================================
The paper lists soft X-ray generation and plasma diagnostics as applications.
When the 6.4 GW beam is focused tightly enough, the intensity ionizes the target
and creates a plasma; that plasma radiates (including soft X-rays) and its
behaviour is set by a few key intensity-derived numbers. This module computes
them: the focused intensity, the normalized vector potential a0, the
ponderomotive (quiver) energy, the critical plasma density for 1064 nm, and a
rough soft-X-ray conversion estimate.

Key relations
-------------
  Focused intensity I = P / (pi w0^2).
  Normalized a0 = 0.85e-9 * sqrt(I[W/cm^2]) * lambda[um]   (relativistic when ~1)
  Ponderomotive energy U_p[eV] = 9.33e-14 * I[W/cm^2] * lambda[um]^2
  Critical density n_c = eps0 m_e omega^2 / e^2.

Run:
    python plasma.py
    python plasma.py --power 6.4e9 --spot-um 20
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

EPS0 = 8.8541878128e-12
M_E = 9.1093837015e-31
Q_E = 1.602176634e-19
C0 = 2.99792458e8


@dataclass
class LaserPlasma:
    peak_power_W: float = 6.4e9
    spot_radius_um: float = 20.0
    lam_nm: float = 1064.0

    @property
    def lam_um(self):
        return self.lam_nm / 1000.0

    def intensity_Wcm2(self) -> float:
        area_cm2 = np.pi * (self.spot_radius_um * 1e-4) ** 2
        return self.peak_power_W / area_cm2

    def a0(self) -> float:
        return 0.85e-9 * np.sqrt(self.intensity_Wcm2()) * self.lam_um

    def ponderomotive_eV(self) -> float:
        return 9.33e-14 * self.intensity_Wcm2() * self.lam_um ** 2

    def critical_density_m3(self) -> float:
        omega = 2.0 * np.pi * C0 / (self.lam_nm * 1e-9)
        return EPS0 * M_E * omega ** 2 / Q_E ** 2

    def regime(self) -> str:
        a = self.a0()
        if a >= 1.0:
            return "relativistic"
        if self.intensity_Wcm2() >= 1e12:
            return "strong-field (ionizing, X-ray emitting)"
        return "sub-ionization"

    def soft_xray_fraction(self) -> float:
        """Very rough laser->soft-X-ray conversion: rises with intensity, a few
        percent in the 1e13-1e15 W/cm^2 range, saturating."""
        I = self.intensity_Wcm2()
        return float(0.05 * (1.0 - np.exp(-I / 1e14)))


def main():
    ap = argparse.ArgumentParser(description="Laser-plasma / X-ray generation")
    ap.add_argument("--power", type=float, default=6.4e9, help="peak power [W]")
    ap.add_argument("--spot-um", type=float, default=20.0)
    args = ap.parse_args()

    lp = LaserPlasma(peak_power_W=args.power, spot_radius_um=args.spot_um)
    print("=" * 60)
    print(" Laser-plasma interaction (1064 nm)")
    print("=" * 60)
    print(f"  peak power          : {args.power/1e9:.2f} GW")
    print(f"  focal spot radius   : {args.spot_um:.0f} um")
    print(f"  focused intensity   : {lp.intensity_Wcm2():.2e} W/cm^2")
    print(f"  normalized a0       : {lp.a0():.3f}")
    print(f"  ponderomotive energy: {lp.ponderomotive_eV():.1f} eV")
    print(f"  critical density    : {lp.critical_density_m3():.2e} 1/m^3")
    print(f"  regime              : {lp.regime()}")
    print(f"  soft-X-ray fraction : {lp.soft_xray_fraction()*100:.2f} %")
    print("=" * 60)

    if _HAVE_MPL:
        spots = np.linspace(2, 100, 200)
        Is = [LaserPlasma(args.power, s).intensity_Wcm2() for s in spots]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(spots, Is, lw=2)
        plt.axhline(1e12, color="r", ls="--", label="ionization ~1e12")
        plt.axvline(args.spot_um, color="tab:green", ls=":", label="operating spot")
        plt.xlabel("focal spot radius [um]"); plt.ylabel("intensity [W/cm^2]")
        plt.title("Focused intensity vs spot size")
        plt.legend(); plt.tight_layout(); plt.savefig("plasma.png", dpi=130)
        print("Saved -> plasma.png")
        plt.show()


if __name__ == "__main__":
    main()
