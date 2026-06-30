#!/usr/bin/env python3
"""
================================================================================
storage.py  -  energy-storage efficiency vs pump duration & lifetime
================================================================================
A quasi-CW pumped amplifier doesn't store all the pump energy: while you're
pumping (the paper uses a 200 us pump pulse) the upper level is also decaying
with its finite lifetime (tau = 230 us for Nd:YAG). If you pump much longer than
tau, the early-deposited inversion has already fluoresced away by the time the
seed arrives. This module quantifies the STORAGE EFFICIENCY: the fraction of
deposited pump energy that actually survives in the inversion at the moment of
extraction.

Model
-----
  Inversion build-up under constant pump for duration t_p:
      N(t_p) = R tau (1 - exp(-t_p / tau))
  Pump energy delivered ~ R t_p. Storage efficiency:
      eta_store = N(t_p) / (R t_p) = tau/t_p (1 - exp(-t_p/tau))
Maximum efficiency for t_p << tau; falls as t_p approaches/exceeds tau.

Reports storage efficiency for a given pump duration, and the optimum pump
duration for an energy target vs efficiency.

Run:
    python storage.py
    python storage.py --pump-us 200 --tau-us 230
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
class Storage:
    tau_us: float = 230.0      # upper-state lifetime (Nd:YAG)

    def efficiency(self, pump_us: float) -> float:
        x = pump_us / self.tau_us
        if x <= 0:
            return 1.0
        return float(self.tau_us / pump_us * (1.0 - np.exp(-x)))

    def inversion_fraction(self, pump_us: float) -> float:
        """Inversion relative to the steady-state (fully-pumped) value."""
        return float(1.0 - np.exp(-pump_us / self.tau_us))


def main():
    ap = argparse.ArgumentParser(description="Energy-storage efficiency")
    ap.add_argument("--pump-us", type=float, default=200.0)
    ap.add_argument("--tau-us", type=float, default=230.0)
    args = ap.parse_args()

    s = Storage(tau_us=args.tau_us)
    eta = s.efficiency(args.pump_us)
    inv = s.inversion_fraction(args.pump_us)

    print("=" * 60)
    print(" Energy-storage efficiency")
    print("=" * 60)
    print(f"  upper-state lifetime: {args.tau_us:.0f} us")
    print(f"  pump duration       : {args.pump_us:.0f} us ({args.pump_us/args.tau_us:.2f} tau)")
    print(f"  storage efficiency  : {eta*100:.1f} %")
    print(f"  inversion vs steady : {inv*100:.1f} %")
    print(f"  -> {'good: short pump' if eta > 0.85 else 'losing energy to fluorescence'}")
    print(f"  (paper: 200 us pump, 230 us lifetime)")
    print("=" * 60)

    if _HAVE_MPL:
        pumps = np.linspace(10, 3 * args.tau_us, 200)
        etas = [s.efficiency(p) * 100 for p in pumps]
        invs = [s.inversion_fraction(p) * 100 for p in pumps]
        plt.figure(figsize=(8, 4.2))
        plt.plot(pumps, etas, lw=2, label="storage efficiency")
        plt.plot(pumps, invs, lw=2, label="inversion vs steady")
        plt.axvline(args.pump_us, color="tab:green", ls=":", label="this pump")
        plt.axvline(args.tau_us, color="r", ls="--", label="lifetime tau")
        plt.xlabel("pump duration [us]"); plt.ylabel("%")
        plt.title("Storage efficiency vs pump duration")
        plt.legend(); plt.tight_layout(); plt.savefig("storage.png", dpi=130)
        print("Saved -> storage.png")
        plt.show()


if __name__ == "__main__":
    main()
