#!/usr/bin/env python3
"""
================================================================================
dispersion.py  -  Sellmeier refractive index & group-velocity dispersion
================================================================================
phase_matching.py and cpa.py both depend on how the refractive index varies with
wavelength, n(lambda). The standard description is the SELLMEIER equation, an
empirical fit whose derivatives give the group index and the group-velocity
dispersion (GVD), which sets how a pulse spreads in a material and where you must
match phase velocities for harmonic generation. This module is the dispersion
foundation the nonlinear modules sit on.

Model
-----
  Sellmeier:  n^2(lambda) = 1 + sum_i  B_i lambda^2 / (lambda^2 - C_i)
  Group index: n_g = n - lambda dn/dlambda
  GVD: D = -(lambda/c) d^2 n / dlambda^2   [s/m^2], often quoted ps/(nm km)

Includes Sellmeier coefficients for fused silica, YAG, BBO, and KDP.

Run:
    python dispersion.py
    python dispersion.py --material YAG --lam-nm 1064
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

C0 = 2.99792458e8


@dataclass
class Sellmeier:
    name: str
    B: List[float]
    C_um2: List[float]    # in micron^2

    def n(self, lam_nm: float) -> float:
        lam_um2 = (lam_nm / 1000.0) ** 2
        n2 = 1.0
        for b, c in zip(self.B, self.C_um2):
            n2 += b * lam_um2 / (lam_um2 - c)
        return float(np.sqrt(n2))

    def dn_dlam(self, lam_nm: float, h_nm: float = 0.1) -> float:
        return (self.n(lam_nm + h_nm) - self.n(lam_nm - h_nm)) / (2 * h_nm)

    def d2n_dlam2(self, lam_nm: float, h_nm: float = 0.5) -> float:
        return (self.n(lam_nm + h_nm) - 2 * self.n(lam_nm)
                + self.n(lam_nm - h_nm)) / h_nm ** 2

    def group_index(self, lam_nm: float) -> float:
        return self.n(lam_nm) - lam_nm * self.dn_dlam(lam_nm)

    def gvd_ps_nm_km(self, lam_nm: float) -> float:
        """Dispersion parameter D in ps/(nm km)."""
        d2n = self.d2n_dlam2(lam_nm)            # per nm^2
        lam_m = lam_nm * 1e-9
        # D = -(lambda/c) d2n/dlambda^2 ; convert nm^-2 -> m^-2
        D = -(lam_m / C0) * d2n * 1e18          # s/m^2
        return D * 1e6 * 1e3 * 1e9 / 1e12       # -> ps/(nm km)


MATERIALS: Dict[str, Sellmeier] = {
    "fused_silica": Sellmeier("fused silica",
        [0.6961663, 0.4079426, 0.8974794],
        [0.0684043 ** 2, 0.1162414 ** 2, 9.896161 ** 2]),
    "YAG": Sellmeier("YAG",
        [2.28200, 3.27644], [0.01185, 282.734]),
    "BBO": Sellmeier("BBO (o)",
        [0.90291, 0.83155, 0.76536],
        [0.003926, 0.018786, 60.01]),
    "KDP": Sellmeier("KDP (o)",
        [1.256618, 33.89909], [0.0084888, 1113.6]),
}


def main():
    ap = argparse.ArgumentParser(description="Sellmeier dispersion")
    ap.add_argument("--material", choices=list(MATERIALS), default="YAG")
    ap.add_argument("--lam-nm", type=float, default=1064.0)
    args = ap.parse_args()

    s = MATERIALS[args.material]
    lam = args.lam_nm

    print("=" * 60)
    print(f" Sellmeier dispersion: {s.name}")
    print("=" * 60)
    print(f"  wavelength          : {lam:.0f} nm")
    print(f"  refractive index n  : {s.n(lam):.5f}")
    print(f"  group index n_g     : {s.group_index(lam):.5f}")
    print(f"  GVD D               : {s.gvd_ps_nm_km(lam):.1f} ps/(nm km)")
    print(f"  regime              : {'normal' if s.gvd_ps_nm_km(lam) < 0 else 'anomalous'} dispersion")
    print("=" * 60)

    if _HAVE_MPL:
        lams = np.linspace(400, 2000, 400)
        ns = [s.n(l) for l in lams]
        plt.figure(figsize=(8, 4.2))
        plt.plot(lams, ns, lw=2)
        plt.axvline(lam, color="tab:green", ls=":", label=f"{lam:.0f} nm")
        plt.xlabel("wavelength [nm]"); plt.ylabel("refractive index n")
        plt.title(f"Sellmeier dispersion: {s.name}")
        plt.legend(); plt.tight_layout(); plt.savefig("dispersion.png", dpi=130)
        print("Saved -> dispersion.png")
        plt.show()


if __name__ == "__main__":
    main()
