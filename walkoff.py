#!/usr/bin/env python3
"""
================================================================================
walkoff.py  -  temporal & spatial walk-off in nonlinear crystals
================================================================================
phase_matching.py / dispersion.py set up the indices; this module captures a
consequence that LIMITS harmonic-crystal length: WALK-OFF.
  * TEMPORAL walk-off: fundamental and harmonic travel at different GROUP
    velocities, so they slide apart in time as they propagate. Once they no
    longer overlap, conversion stops, capping the useful crystal length for a
    given pulse duration.
  * SPATIAL walk-off: in a birefringent crystal the extraordinary beam's energy
    flow (Poynting vector) is tilted from the wavevector by the walk-off angle,
    so the beams separate transversely, also limiting effective length.
Both set the real upper bound on how long a crystal you can use in shg.py /
opcpa.py.

Model
-----
  Group-velocity mismatch: GVM = 1/vg(2w) - 1/vg(w)  [s/m]
  Temporal walk-off length: L_tw = pulse_duration / |GVM|
  Spatial walk-off: separation = rho * L (rho = walk-off angle)

Run:
    python walkoff.py
    python walkoff.py --pulse-ps 200 --crystal-mm 12
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
class WalkOff:
    gvm_fs_per_mm: float = 80.0       # group-velocity mismatch [fs/mm] (typical)
    walkoff_angle_mrad: float = 30.0  # spatial walk-off angle (birefringent)
    pulse_ps: float = 200.0
    crystal_mm: float = 12.0

    def temporal_walkoff_ps(self) -> float:
        """Accumulated temporal slip over the crystal [ps]."""
        return self.gvm_fs_per_mm * self.crystal_mm / 1000.0

    def temporal_walkoff_length_mm(self) -> float:
        """Crystal length at which the slip equals the pulse duration."""
        return (self.pulse_ps * 1000.0) / self.gvm_fs_per_mm

    def spatial_separation_um(self) -> float:
        return self.walkoff_angle_mrad * 1e-3 * (self.crystal_mm * 1e-3) * 1e6

    def overlap_fraction(self) -> float:
        """Fraction of the pulse still temporally overlapped at crystal exit."""
        slip = self.temporal_walkoff_ps()
        return float(max(1.0 - slip / self.pulse_ps, 0.0))


def main():
    ap = argparse.ArgumentParser(description="Nonlinear-crystal walk-off")
    ap.add_argument("--pulse-ps", type=float, default=200.0)
    ap.add_argument("--crystal-mm", type=float, default=12.0)
    ap.add_argument("--gvm", type=float, default=80.0, help="GVM [fs/mm]")
    args = ap.parse_args()

    w = WalkOff(gvm_fs_per_mm=args.gvm, pulse_ps=args.pulse_ps, crystal_mm=args.crystal_mm)

    print("=" * 60)
    print(" Nonlinear-crystal walk-off")
    print("=" * 60)
    print(f"  pulse duration      : {args.pulse_ps:.0f} ps")
    print(f"  crystal length      : {args.crystal_mm:.0f} mm")
    print(f"  group-vel mismatch  : {args.gvm:.0f} fs/mm")
    print(f"  temporal slip       : {w.temporal_walkoff_ps():.3f} ps")
    print(f"  temporal overlap    : {w.overlap_fraction()*100:.1f} %")
    print(f"  walk-off length     : {w.temporal_walkoff_length_mm():.0f} mm (max useful)")
    print(f"  spatial separation  : {w.spatial_separation_um():.1f} um")
    print(f"  -> {'crystal length OK' if args.crystal_mm < w.temporal_walkoff_length_mm() else 'TOO LONG: walk-off kills conversion'}")
    print("=" * 60)

    if _HAVE_MPL:
        lengths = np.linspace(1, 2 * w.temporal_walkoff_length_mm(), 200)
        overlaps = []
        for L in lengths:
            ww = WalkOff(gvm_fs_per_mm=args.gvm, pulse_ps=args.pulse_ps, crystal_mm=L)
            overlaps.append(ww.overlap_fraction() * 100)
        plt.figure(figsize=(8, 4.2))
        plt.plot(lengths, overlaps, lw=2)
        plt.axvline(args.crystal_mm, color="tab:green", ls=":", label="this crystal")
        plt.axvline(w.temporal_walkoff_length_mm(), color="r", ls="--", label="walk-off length")
        plt.xlabel("crystal length [mm]"); plt.ylabel("temporal overlap [%]")
        plt.title("Pulse overlap vs crystal length (walk-off)")
        plt.legend(); plt.tight_layout(); plt.savefig("walkoff.png", dpi=130)
        print("Saved -> walkoff.png")
        plt.show()


if __name__ == "__main__":
    main()
