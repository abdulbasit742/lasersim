#!/usr/bin/env python3
"""
================================================================================
cpa.py  -  grating stretcher / compressor for chirped-pulse amplification
================================================================================
Chirped-pulse amplification (CPA) is THE technique that made high-energy short
pulses possible (Strickland & Mourou, Nobel 2018, cited in the paper as ref
[23]). A short pulse is stretched in time with a grating pair (so its intensity
is low enough to amplify safely), amplified, then recompressed with a matched
grating pair. opcpa.py covered the parametric gain; this covers the DISPERSION
engineering that bookends it.

Model
-----
  Grating-pair group-delay dispersion (GDD):
      GDD = -(m^2 lambda^3 L) / (pi c^2 d^2 cos^3(theta))
  Stretched duration from GDD acting on bandwidth:
      tau_stretched ~ |GDD| * delta_omega
  Compressor is the conjugate (opposite-sign GDD). Residual (uncompensated)
  GDD after the pair leaves a finite recompressed duration above transform limit.

Reports stretch factor, the grating separation needed to reach a target stretch,
and the recompressed duration given a residual-dispersion error.

Run:
    python cpa.py
    python cpa.py --tl-fs 100 --target-ps 200
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
class GratingPair:
    lines_per_mm: float = 1740.0
    incidence_deg: float = 50.0
    lam_nm: float = 1064.0
    order: int = 1

    @property
    def d_m(self) -> float:
        return 1e-3 / self.lines_per_mm

    @property
    def theta(self) -> float:
        return np.radians(self.incidence_deg)

    def gdd_per_meter(self) -> float:
        """Group-delay dispersion per metre of grating separation [s^2/m]."""
        lam = self.lam_nm * 1e-9
        m = self.order
        num = -(m ** 2) * lam ** 3
        den = np.pi * C0 ** 2 * self.d_m ** 2 * np.cos(self.theta) ** 3
        return num / den

    def gdd(self, separation_m: float) -> float:
        return self.gdd_per_meter() * separation_m


def bandwidth_rad_s(tl_fs: float) -> float:
    """Angular bandwidth of a transform-limited Gaussian of duration tl_fs."""
    return 0.441 * 2.0 * np.pi / (tl_fs * 1e-15)


def stretched_duration_s(gdd_s2: float, tl_fs: float) -> float:
    t0 = (tl_fs * 1e-15) / 1.1774
    return (tl_fs * 1e-15) * np.sqrt(1.0 + (abs(gdd_s2) / t0 ** 2) ** 2)


def separation_for_target(grating: GratingPair, tl_fs: float, target_ps: float) -> float:
    """Grating separation [m] to stretch a TL pulse to the target duration."""
    t0 = (tl_fs * 1e-15) / 1.1774
    target_s = target_ps * 1e-12
    ratio = (target_s / (tl_fs * 1e-15)) ** 2 - 1.0
    gdd_needed = np.sqrt(max(ratio, 0.0)) * t0 ** 2
    return gdd_needed / abs(grating.gdd_per_meter())


def recompressed_duration_ps(tl_fs: float, residual_gdd_s2: float) -> float:
    """Duration after compression with leftover (residual) GDD."""
    return stretched_duration_s(residual_gdd_s2, tl_fs) * 1e12


def main():
    ap = argparse.ArgumentParser(description="CPA stretcher/compressor model")
    ap.add_argument("--tl-fs", type=float, default=100.0, help="transform-limited duration")
    ap.add_argument("--target-ps", type=float, default=200.0, help="stretch target")
    ap.add_argument("--residual-frac", type=float, default=0.01,
                    help="residual GDD as fraction of stretcher GDD")
    args = ap.parse_args()

    g = GratingPair()
    sep = separation_for_target(g, args.tl_fs, args.target_ps)
    gdd = g.gdd(sep)
    stretched = stretched_duration_s(gdd, args.tl_fs)
    residual = args.residual_frac * abs(gdd)
    recomp = recompressed_duration_ps(args.tl_fs, residual)

    print("=" * 62)
    print(" CPA grating stretcher / compressor")
    print("=" * 62)
    print(f"  transform-limited   : {args.tl_fs:.0f} fs")
    print(f"  grating             : {g.lines_per_mm:.0f} l/mm @ {g.incidence_deg:.0f} deg")
    print(f"  GDD per metre       : {g.gdd_per_meter():.3e} s^2/m")
    print(f"  separation needed   : {sep*100:.1f} cm")
    print(f"  stretched duration  : {stretched*1e12:.1f} ps (target {args.target_ps:.0f})")
    print(f"  stretch factor      : {stretched/(args.tl_fs*1e-15):.0f}x")
    print(f"  residual GDD        : {args.residual_frac*100:.1f}% of stretcher")
    print(f"  recompressed        : {recomp*1e3:.1f} fs (TL {args.tl_fs:.0f} fs)")
    print("=" * 62)

    if _HAVE_MPL:
        seps = np.linspace(0.01, sep * 2, 200)
        durs = [stretched_duration_s(g.gdd(s), args.tl_fs) * 1e12 for s in seps]
        plt.figure(figsize=(8, 4.2))
        plt.plot(seps * 100, durs, lw=2)
        plt.axhline(args.target_ps, color="r", ls="--", label="target")
        plt.axvline(sep * 100, color="tab:green", ls=":", label="separation")
        plt.xlabel("grating separation [cm]"); plt.ylabel("stretched duration [ps]")
        plt.title("CPA stretch vs grating separation")
        plt.legend(); plt.tight_layout(); plt.savefig("cpa.png", dpi=130)
        print("Saved -> cpa.png")
        plt.show()


if __name__ == "__main__":
    main()
