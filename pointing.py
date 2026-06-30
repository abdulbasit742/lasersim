#!/usr/bin/env python3
"""
================================================================================
pointing.py  -  beam pointing stability & far-field spot wander
================================================================================
For ranging, targeting, and OPCPA seeding, the beam has to land where you aim
it. But mirror mounts drift thermally, the floor vibrates, and air turbulence
bends the beam. A small angular wobble theta turns into a far-field position
error theta * distance that can miss the target entirely. This module connects
pointing jitter (in microradians) to on-target hit statistics.

Model
-----
  Angular jitter ~ Gaussian, sigma_theta [urad] (mount + vibration + air).
  Far-field displacement at range L: sigma_x = sigma_theta * L.
  Hit probability within a target of radius r: Rayleigh CDF
      P = 1 - exp(-r^2 / (2 sigma_x^2)).

Reports the far-field spot wander vs range and the angular-stability budget to
hit a target with a chosen probability.

Run:
    python pointing.py
    python pointing.py --jitter-urad 5 --range-m 1000 --target-cm 10
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
class Pointing:
    jitter_urad: float = 5.0       # RMS angular jitter [microrad]

    def spot_wander_m(self, range_m: float) -> float:
        return self.jitter_urad * 1e-6 * range_m

    def hit_probability(self, range_m: float, target_radius_m: float) -> float:
        sx = self.spot_wander_m(range_m)
        if sx <= 0:
            return 1.0
        return float(1.0 - np.exp(-target_radius_m ** 2 / (2.0 * sx ** 2)))

    def max_jitter_for(self, range_m: float, target_radius_m: float,
                       prob: float = 0.95) -> float:
        """Angular-jitter budget [urad] to hit with the given probability."""
        # invert Rayleigh CDF: sigma_x = r / sqrt(-2 ln(1-P))
        sx = target_radius_m / np.sqrt(-2.0 * np.log(1.0 - prob))
        return sx / range_m / 1e-6


def main():
    ap = argparse.ArgumentParser(description="Beam pointing stability")
    ap.add_argument("--jitter-urad", type=float, default=5.0)
    ap.add_argument("--range-m", type=float, default=1000.0)
    ap.add_argument("--target-cm", type=float, default=10.0)
    args = ap.parse_args()

    p = Pointing(jitter_urad=args.jitter_urad)
    r = args.target_cm / 100.0
    wander = p.spot_wander_m(args.range_m)
    hit = p.hit_probability(args.range_m, r)
    budget = p.max_jitter_for(args.range_m, r, 0.95)

    print("=" * 60)
    print(" Beam pointing stability")
    print("=" * 60)
    print(f"  angular jitter (RMS): {args.jitter_urad:.1f} urad")
    print(f"  range               : {args.range_m:.0f} m")
    print(f"  target radius       : {args.target_cm:.1f} cm")
    print(f"  far-field wander    : {wander*100:.1f} cm RMS")
    print(f"  hit probability     : {hit*100:.1f} %")
    print(f"  jitter for 95% hit  : {budget:.2f} urad")
    print("=" * 60)

    if _HAVE_MPL:
        ranges = np.linspace(10, args.range_m * 1.5, 200)
        hits = [p.hit_probability(R, r) * 100 for R in ranges]
        plt.figure(figsize=(8, 4.2))
        plt.plot(ranges, hits, lw=2)
        plt.axvline(args.range_m, color="tab:green", ls=":", label="range")
        plt.axhline(95, color="r", ls="--", label="95%")
        plt.xlabel("range [m]"); plt.ylabel("hit probability [%]")
        plt.title(f"On-target hit vs range ({args.jitter_urad:.0f} urad jitter)")
        plt.legend(); plt.tight_layout(); plt.savefig("pointing.png", dpi=130)
        print("Saved -> pointing.png")
        plt.show()


if __name__ == "__main__":
    main()
