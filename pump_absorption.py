#!/usr/bin/env python3
"""
================================================================================
pump_absorption.py  -  pump absorption vs doping & rod length (Beer-Lambert)
================================================================================
pump_diode.py gave the 808 nm light arriving at the rod; spatial_gain.py gave
the 2D transverse pump pattern. This module covers the LONGITUDINAL absorption:
as pump light travels through the doped rod it's absorbed exponentially
(Beer-Lambert), so the front of the rod sees more pump than the back. Doping and
length trade off: high doping / long rod absorbs nearly all the pump (efficient)
but concentrates heat at the entry face (non-uniform, worse thermal lens). This
is the design knob that sets both efficiency AND thermal uniformity.

Model
-----
  Absorbed fraction over length L:  eta_abs = 1 - exp(-alpha L)
  alpha = sigma_abs * N_dopant  (absorption coefficient).
  Local deposition:  dP/dz = -alpha P(z),  P(z) = P0 exp(-alpha z).
  Uniformity metric: ratio of back-face to front-face deposition.

Reports absorbed fraction, the longitudinal deposition profile, and the
efficiency/uniformity trade-off vs doping.

Run:
    python pump_absorption.py
    python pump_absorption.py --doping-pct 0.7 --length-mm 130
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

# Nd:YAG: 1 at.% doping ~ 1.38e20 Nd ions / cm^3
ND_PER_CM3_PER_PCT = 1.38e20
SIGMA_ABS_CM2 = 7.7e-20      # 808 nm absorption cross section (Nd:YAG)


@dataclass
class PumpAbsorption:
    doping_pct: float = 0.7
    length_mm: float = 130.0

    @property
    def alpha_per_cm(self) -> float:
        N = self.doping_pct * ND_PER_CM3_PER_PCT
        return SIGMA_ABS_CM2 * N

    def absorbed_fraction(self) -> float:
        return 1.0 - np.exp(-self.alpha_per_cm * (self.length_mm / 10.0))

    def deposition_profile(self, n=200):
        z_cm = np.linspace(0, self.length_mm / 10.0, n)
        dep = self.alpha_per_cm * np.exp(-self.alpha_per_cm * z_cm)
        return z_cm, dep / dep.max()

    def uniformity(self) -> float:
        """Back-face / front-face deposition (1.0 = perfectly uniform)."""
        L_cm = self.length_mm / 10.0
        return float(np.exp(-self.alpha_per_cm * L_cm))


def main():
    ap = argparse.ArgumentParser(description="Pump absorption vs doping/length")
    ap.add_argument("--doping-pct", type=float, default=0.7)
    ap.add_argument("--length-mm", type=float, default=130.0)
    args = ap.parse_args()

    pa = PumpAbsorption(doping_pct=args.doping_pct, length_mm=args.length_mm)

    print("=" * 60)
    print(" Longitudinal pump absorption (Beer-Lambert)")
    print("=" * 60)
    print(f"  doping              : {args.doping_pct:.2f} at.%")
    print(f"  rod length          : {args.length_mm:.0f} mm")
    print(f"  absorption coeff    : {pa.alpha_per_cm:.3f} /cm")
    print(f"  absorbed fraction   : {pa.absorbed_fraction()*100:.1f} %")
    print(f"  uniformity (back/front): {pa.uniformity():.3f}")
    print(f"  -> {'efficient but front-loaded heat' if pa.absorbed_fraction() > 0.9 else 'uniform but leaks pump'}")
    print(f"  (paper: 0.6-0.8% doped, 130 mm rods)")
    print("=" * 60)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
        z, dep = pa.deposition_profile()
        ax[0].plot(z * 10, dep, lw=2)
        ax[0].set(title="Heat deposition along rod", xlabel="z [mm]",
                  ylabel="relative deposition")
        dopings = np.linspace(0.1, 2.0, 100)
        abss = [PumpAbsorption(d, args.length_mm).absorbed_fraction()*100 for d in dopings]
        unis = [PumpAbsorption(d, args.length_mm).uniformity()*100 for d in dopings]
        ax[1].plot(dopings, abss, lw=2, label="absorbed %")
        ax[1].plot(dopings, unis, lw=2, label="uniformity %")
        ax[1].axvline(args.doping_pct, color="tab:green", ls=":", label="this doping")
        ax[1].set(title="Efficiency vs uniformity trade-off",
                  xlabel="doping [at.%]", ylabel="%"); ax[1].legend()
        plt.tight_layout(); plt.savefig("pump_absorption.png", dpi=130)
        print("Saved -> pump_absorption.png")
        plt.show()


if __name__ == "__main__":
    main()
