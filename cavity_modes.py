#!/usr/bin/env python3
"""
================================================================================
cavity_modes.py  -  longitudinal cavity modes & free spectral range
================================================================================
A laser cavity only supports discrete longitudinal modes spaced by the FREE
SPECTRAL RANGE (FSR = c/2L). How many of these fall under the gain bandwidth
decides whether the laser runs SINGLE-longitudinal-mode (clean, narrow, long
coherence, good for seeding) or MULTI-mode (mode beating, temporal structure).
A short microchip seed cavity has a huge FSR so only one mode fits -> clean
single-mode seed, which is exactly what feeds the amplifier. This module ties
cavity length and gain bandwidth to the mode count and coherence length.

Model
-----
  FSR (frequency):   dnu = c / (2 n L)
  Modes under gain:  N = gain_bandwidth / FSR
  Coherence length:  L_coh ~ c / (pi * linewidth)

Run:
    python cavity_modes.py
    python cavity_modes.py --length-mm 2 --bandwidth-ghz 120
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
class CavityModes:
    length_mm: float = 2.0
    n0: float = 1.82
    gain_bandwidth_GHz: float = 120.0   # Nd:YAG ~120 GHz (~0.45 nm at 1064)

    def fsr_GHz(self) -> float:
        return C0 / (2.0 * self.n0 * (self.length_mm * 1e-3)) / 1e9

    def mode_count(self) -> int:
        return max(int(self.gain_bandwidth_GHz / self.fsr_GHz()), 1)

    def is_single_mode(self) -> bool:
        return self.mode_count() <= 1

    def coherence_length_m(self) -> float:
        # linewidth ~ FSR for single mode, gain bandwidth for multimode
        lw_Hz = (self.fsr_GHz() if self.is_single_mode()
                 else self.gain_bandwidth_GHz) * 1e9
        return C0 / (np.pi * lw_Hz)


def main():
    ap = argparse.ArgumentParser(description="Longitudinal cavity modes")
    ap.add_argument("--length-mm", type=float, default=2.0)
    ap.add_argument("--bandwidth-ghz", type=float, default=120.0)
    args = ap.parse_args()

    cm = CavityModes(length_mm=args.length_mm, gain_bandwidth_GHz=args.bandwidth_ghz)

    print("=" * 60)
    print(" Longitudinal cavity modes")
    print("=" * 60)
    print(f"  cavity length       : {args.length_mm:.1f} mm")
    print(f"  free spectral range : {cm.fsr_GHz():.1f} GHz")
    print(f"  gain bandwidth      : {args.bandwidth_ghz:.0f} GHz")
    print(f"  modes under gain    : {cm.mode_count()}")
    print(f"  operation           : {'SINGLE longitudinal mode' if cm.is_single_mode() else 'MULTI-mode (beating)'}")
    print(f"  coherence length    : {cm.coherence_length_m():.3f} m")
    print("=" * 60)

    if _HAVE_MPL:
        lengths = np.linspace(0.5, 200, 300)
        counts = [CavityModes(length_mm=L, gain_bandwidth_GHz=args.bandwidth_ghz).mode_count()
                  for L in lengths]
        plt.figure(figsize=(8, 4.2))
        plt.semilogy(lengths, counts, lw=2)
        plt.axhline(1, color="r", ls="--", label="single mode")
        plt.axvline(args.length_mm, color="tab:green", ls=":", label="this cavity")
        plt.xlabel("cavity length [mm]"); plt.ylabel("# longitudinal modes")
        plt.title("Mode count vs cavity length")
        plt.legend(); plt.tight_layout(); plt.savefig("cavity_modes.png", dpi=130)
        print("Saved -> cavity_modes.png")
        plt.show()


if __name__ == "__main__":
    main()
