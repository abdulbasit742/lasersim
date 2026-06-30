#!/usr/bin/env python3
"""
================================================================================
contrast.py  -  temporal pulse contrast: ASE pedestal & pre-pulses
================================================================================
For a high-energy ps pulse, the peak isn't the whole story. Sitting underneath
it is a low-level background: an ASE pedestal (nanosecond-scale amplified
spontaneous emission) and discrete pre-pulses (from leakage/reflections). The
CONTRAST is the ratio of main-pulse peak intensity to that background. Poor
contrast pre-ionizes or pre-damages a target before the main pulse arrives,
which ruins OPCPA seeding and material-processing results.

This module builds a synthetic temporal intensity profile (main ps pulse + ns
ASE pedestal + pre-pulses) and computes the contrast at chosen delays, plus how
much a fast Pockels-cell gate or saturable absorber would improve it.

Run:
    python contrast.py
    python contrast.py --pedestal 1e-6 --gate-contrast 1e3
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class PrePulse:
    delay_ps: float
    rel_intensity: float


@dataclass
class PulseContrast:
    main_fwhm_ps: float = 200.0
    pedestal_level: float = 1e-6
    pedestal_fwhm_ns: float = 5.0
    pre_pulses: List[PrePulse] = field(default_factory=list)
    window_ns: float = 20.0
    npts: int = 40000

    def time_axis_ns(self):
        return np.linspace(-self.window_ns / 2, self.window_ns / 2, self.npts)

    def profile(self, gate_contrast: float = 1.0):
        """Normalized temporal intensity (peak=1). gate_contrast>1 suppresses
        everything outside the main-pulse window (a fast gate / sat. absorber)."""
        t_ns = self.time_axis_ns()
        t_ps = t_ns * 1e3
        main = np.exp(-4 * np.log(2) * (t_ps / self.main_fwhm_ps) ** 2)
        pedestal = self.pedestal_level * np.exp(
            -4 * np.log(2) * (t_ns / self.pedestal_fwhm_ns) ** 2)
        prof = main + pedestal
        for pp in self.pre_pulses:
            prof += pp.rel_intensity * np.exp(
                -4 * np.log(2) * ((t_ps - pp.delay_ps) / self.main_fwhm_ps) ** 2)
        if gate_contrast > 1.0:
            gate = np.where(np.abs(t_ps) < 2 * self.main_fwhm_ps, 1.0, 1.0 / gate_contrast)
            prof = np.maximum(main, prof * gate)
        return t_ns, prof / prof.max()

    def contrast_at(self, delay_ns: float, gate_contrast: float = 1.0) -> float:
        t_ns, prof = self.profile(gate_contrast)
        i = int(np.argmin(np.abs(t_ns - delay_ns)))
        return 1.0 / prof[i] if prof[i] > 0 else float("inf")


def main():
    ap = argparse.ArgumentParser(description="Temporal pulse contrast")
    ap.add_argument("--pedestal", type=float, default=1e-6,
                    help="ASE pedestal level relative to peak")
    ap.add_argument("--gate-contrast", type=float, default=1.0,
                    help="contrast improvement from a fast gate (>1)")
    args = ap.parse_args()

    pc = PulseContrast(
        pedestal_level=args.pedestal,
        pre_pulses=[PrePulse(-2000, 1e-3), PrePulse(-5000, 1e-4)],
    )

    print("=" * 60)
    print(" Temporal pulse contrast")
    print("=" * 60)
    print(f"  ASE pedestal level   : {args.pedestal:.1e} of peak")
    for d in (-5.0, -2.0, -0.5):
        c0 = pc.contrast_at(d)
        cg = pc.contrast_at(d, args.gate_contrast)
        print(f"  contrast @ {d:>5.1f} ns : {c0:.1e}"
              + (f"  -> {cg:.1e} with gate" if args.gate_contrast > 1 else ""))
    print("=" * 60)

    if _HAVE_MPL:
        t, p0 = pc.profile()
        _, pg = pc.profile(args.gate_contrast)
        plt.figure(figsize=(8, 4.4))
        plt.semilogy(t, p0, lw=1.5, label="raw")
        if args.gate_contrast > 1:
            plt.semilogy(t, pg, lw=1.5, label="after gate")
        plt.xlabel("time [ns]"); plt.ylabel("normalized intensity (log)")
        plt.title("Pulse contrast: main pulse + ASE pedestal + pre-pulses")
        plt.ylim(1e-9, 2); plt.legend(); plt.tight_layout()
        plt.savefig("contrast.png", dpi=130)
        print("Saved -> contrast.png")
        plt.show()


if __name__ == "__main__":
    main()
