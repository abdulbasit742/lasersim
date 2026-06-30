#!/usr/bin/env python3
"""
================================================================================
jitter.py  -  timing jitter & pump-seed synchronization
================================================================================
The paper lists timing jitter as a key stability parameter, and for OPCPA it is
critical: the parametric gain only happens while the ps signal overlaps the ps
pump in time. If they jitter relative to each other, the signal sometimes lands
on the pump peak (full gain) and sometimes on its edge (low gain), so the OUTPUT
ENERGY fluctuates shot-to-shot. This module connects timing jitter (in ps RMS)
to output-energy stability.

Model
-----
  Pump temporal gain window ~ Gaussian of width = pump duration.
  Effective gain on shot i = G0 * exp(-(dt_i / tau_pump)^2), dt_i ~ N(0, jitter).
  Monte Carlo the jitter -> distribution of shot energies -> RMS stability.

Reports output-energy RMS vs jitter, and the max tolerable jitter to stay within
an energy-stability spec (the paper quotes 1.1% RMS).

Run:
    python jitter.py
    python jitter.py --jitter-ps 20 --pump-ps 200
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
class SyncModel:
    pump_fwhm_ps: float = 200.0
    seed_fwhm_ps: float = 200.0

    @property
    def overlap_tau_ps(self) -> float:
        """Combined temporal gain-window width (RMS-style add)."""
        return np.hypot(self.pump_fwhm_ps, self.seed_fwhm_ps) / 1.6651

    def gain_factor(self, dt_ps):
        """Relative gain when seed is offset by dt from pump peak."""
        return np.exp(-(dt_ps / self.overlap_tau_ps) ** 2)

    def energy_rms(self, jitter_ps: float, n: int = 20000, seed: int = 0) -> float:
        rng = np.random.default_rng(seed)
        dt = rng.normal(0.0, jitter_ps, n)
        g = self.gain_factor(dt)
        return float(np.std(g) / np.mean(g))

    def max_jitter_for_spec(self, rms_spec: float) -> float:
        for j in np.linspace(0.1, self.pump_fwhm_ps, 600):
            if self.energy_rms(j) > rms_spec:
                return max(j - self.pump_fwhm_ps / 600, 0.0)
        return self.pump_fwhm_ps


def main():
    ap = argparse.ArgumentParser(description="Timing jitter -> energy stability")
    ap.add_argument("--jitter-ps", type=float, default=20.0)
    ap.add_argument("--pump-ps", type=float, default=200.0)
    ap.add_argument("--spec", type=float, default=0.011, help="RMS energy spec (1.1%)")
    args = ap.parse_args()

    m = SyncModel(pump_fwhm_ps=args.pump_ps)
    rms = m.energy_rms(args.jitter_ps)
    j_max = m.max_jitter_for_spec(args.spec)

    print("=" * 60)
    print(" Timing jitter -> output-energy stability")
    print("=" * 60)
    print(f"  pump duration       : {args.pump_ps:.0f} ps")
    print(f"  timing jitter (RMS) : {args.jitter_ps:.1f} ps")
    print(f"  output energy RMS   : {rms*100:.2f} %")
    print(f"  spec               : {args.spec*100:.1f} %")
    print(f"  -> {'WITHIN spec' if rms <= args.spec else 'EXCEEDS spec'}")
    print(f"  max tolerable jitter: {j_max:.1f} ps RMS for {args.spec*100:.1f}% stability")
    print("=" * 60)

    if _HAVE_MPL:
        js = np.linspace(1, args.pump_ps, 120)
        rmss = [m.energy_rms(j) * 100 for j in js]
        plt.figure(figsize=(8, 4.2))
        plt.plot(js, rmss, lw=2)
        plt.axhline(args.spec * 100, color="r", ls="--", label=f"{args.spec*100:.1f}% spec")
        plt.axvline(j_max, color="tab:green", ls=":", label=f"max {j_max:.0f} ps")
        plt.xlabel("timing jitter [ps RMS]"); plt.ylabel("energy RMS [%]")
        plt.title("Energy stability vs pump-seed timing jitter")
        plt.legend(); plt.tight_layout(); plt.savefig("jitter.png", dpi=130)
        print("Saved -> jitter.png")
        plt.show()


if __name__ == "__main__":
    main()
