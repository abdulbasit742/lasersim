#!/usr/bin/env python3
"""
================================================================================
prism_compressor.py  -  prism-pair dispersion compressor
================================================================================
cpa.py used a GRATING pair for the big stretch/compress. For FINE dispersion
tuning (and low loss), a PRISM pair is the classic alternative: it provides
tunable negative group-delay dispersion with much lower insertion loss than
gratings (no diffraction efficiency penalty), at the cost of weaker dispersion
per unit length. Prism compressors are common for trimming residual chirp after
a grating compressor or inside an oscillator. This module models the prism-pair
GDD and the tuning knobs (prism separation, insertion).

Model (Fork/Martinez prism-pair)
--------------------------------
  GDD ~ (lambda^3 / (2 pi c^2)) * [ L * (d2P/dlambda2 terms) ]
  Practically: GDD_total = -k * L_sep * (dn/dlambda)^2 + insertion material GDD
  Net GDD is tuned between negative (separation-dominated) and positive
  (material-insertion-dominated).

Reports the net GDD vs prism separation and the separation needed to null a
given residual chirp.

Run:
    python prism_compressor.py
    python prism_compressor.py --separation-cm 50
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


@dataclass
class PrismCompressor:
    lam_nm: float = 1064.0
    dn_dlam_per_um: float = -0.013      # material dispersion dn/dlambda [1/um]
    insertion_gdd_fs2_per_mm: float = 36.0   # +GDD from glass path per mm
    insertion_mm: float = 4.0

    def separation_gdd_fs2(self, separation_cm: float) -> float:
        """Negative GDD from prism separation (angular dispersion)."""
        lam = self.lam_nm * 1e-9
        L = separation_cm * 1e-2
        # GDD = -(lambda^3 / (2 pi c^2)) * L * (4 (dn/dlam)^2), in s^2
        dn_dlam = self.dn_dlam_per_um * 1e6   # per metre
        gdd = -(lam ** 3 / (2 * np.pi * C0 ** 2)) * L * 4 * dn_dlam ** 2
        return gdd * 1e30   # s^2 -> fs^2

    def insertion_gdd_fs2(self) -> float:
        return self.insertion_gdd_fs2_per_mm * self.insertion_mm

    def net_gdd_fs2(self, separation_cm: float) -> float:
        return self.separation_gdd_fs2(separation_cm) + self.insertion_gdd_fs2()

    def separation_to_null(self, residual_gdd_fs2: float) -> float:
        """Prism separation [cm] to cancel a residual +GDD."""
        # solve separation_gdd + insertion_gdd + residual = 0
        target = -(residual_gdd_fs2 + self.insertion_gdd_fs2())
        per_cm = self.separation_gdd_fs2(1.0)   # negative
        return target / per_cm if per_cm != 0 else 0.0


def main():
    ap = argparse.ArgumentParser(description="Prism-pair compressor")
    ap.add_argument("--separation-cm", type=float, default=50.0)
    ap.add_argument("--residual-gdd", type=float, default=5000.0,
                    help="residual GDD to cancel [fs^2]")
    args = ap.parse_args()

    pc = PrismCompressor()
    net = pc.net_gdd_fs2(args.separation_cm)
    sep_null = pc.separation_to_null(args.residual_gdd)

    print("=" * 60)
    print(" Prism-pair dispersion compressor")
    print("=" * 60)
    print(f"  wavelength          : {pc.lam_nm:.0f} nm")
    print(f"  prism separation    : {args.separation_cm:.0f} cm")
    print(f"  separation GDD      : {pc.separation_gdd_fs2(args.separation_cm):.0f} fs^2")
    print(f"  insertion GDD       : {pc.insertion_gdd_fs2():+.0f} fs^2")
    print(f"  net GDD             : {net:.0f} fs^2 ({'negative' if net < 0 else 'positive'})")
    print(f"  separation to null {args.residual_gdd:.0f} fs^2: {sep_null:.1f} cm")
    print("=" * 60)

    if _HAVE_MPL:
        seps = np.linspace(5, 150, 200)
        gdds = [pc.net_gdd_fs2(s) for s in seps]
        plt.figure(figsize=(8, 4.2))
        plt.plot(seps, gdds, lw=2)
        plt.axhline(0, color="gray", ls="-", lw=0.8)
        plt.axvline(args.separation_cm, color="tab:green", ls=":", label="operating")
        plt.xlabel("prism separation [cm]"); plt.ylabel("net GDD [fs^2]")
        plt.title("Prism-pair net GDD vs separation")
        plt.legend(); plt.tight_layout(); plt.savefig("prism_compressor.png", dpi=130)
        print("Saved -> prism_compressor.png")
        plt.show()


if __name__ == "__main__":
    main()
