#!/usr/bin/env python3
"""
================================================================================
regen.py  -  regenerative amplifier (regen) round-trip buildup
================================================================================
A regenerative amplifier traps a low-energy seed pulse in a cavity with a
Pockels cell and lets it make many round trips through the gain medium, building
up energy by orders of magnitude, then switches it out at peak. Regens are the
standard front-end booster between an oscillator and a multipass/power amplifier
chain (a natural pre-stage to the paper's AMP-1). No module covered the
round-trip buildup dynamics, so here it is.

Model (per round trip)
----------------------
  E_{n+1} = E_n * G(E_n) * (1 - loss)
  G(E_n)  = 1 + (g0 - 1) / (1 + E_n / E_sat)     # saturating gain per pass
The pulse grows exponentially while small, then saturation flattens it. The
optimum number of round trips is just before saturation rolls the gain off; dump
there for maximum energy and best stability.

Reports the buildup curve, the optimum dump round-trip, the output energy, and
the total gain from seed to dump.

Run:
    python regen.py
    python regen.py --seed-nJ 1 --g0 1.8 --loss 0.05
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class Regen:
    seed_J: float = 1e-9          # 1 nJ seed
    g0: float = 1.8               # small-signal single-pass gain
    e_sat_J: float = 2e-3         # saturation energy [J]
    loss: float = 0.05            # per-round-trip loss fraction
    max_round_trips: int = 60

    def gain(self, E: float) -> float:
        return 1.0 + (self.g0 - 1.0) / (1.0 + E / self.e_sat_J)

    def buildup(self) -> np.ndarray:
        E = self.seed_J
        hist = [E]
        for _ in range(self.max_round_trips):
            E = E * self.gain(E) * (1.0 - self.loss)
            hist.append(E)
        return np.array(hist)

    def optimum_dump(self) -> Tuple[int, float]:
        """Round trip with maximum energy (dump point)."""
        hist = self.buildup()
        n = int(np.argmax(hist))
        return n, hist[n]


def main():
    ap = argparse.ArgumentParser(description="Regenerative amplifier buildup")
    ap.add_argument("--seed-nJ", type=float, default=1.0)
    ap.add_argument("--g0", type=float, default=1.8)
    ap.add_argument("--loss", type=float, default=0.05)
    ap.add_argument("--e-sat-mJ", type=float, default=2.0)
    args = ap.parse_args()

    regen = Regen(seed_J=args.seed_nJ * 1e-9, g0=args.g0, loss=args.loss,
                  e_sat_J=args.e_sat_mJ * 1e-3)
    hist = regen.buildup()
    n_opt, e_opt = regen.optimum_dump()

    print("=" * 60)
    print(" Regenerative amplifier buildup")
    print("=" * 60)
    print(f"  seed energy        : {args.seed_nJ:.1f} nJ")
    print(f"  single-pass gain g0: {args.g0:.2f}")
    print(f"  round-trip loss    : {args.loss*100:.1f} %")
    print(f"  optimum dump       : round trip #{n_opt}")
    print(f"  output energy      : {e_opt*1e3:.3f} mJ")
    print(f"  total gain         : {e_opt/regen.seed_J:.2e}x")
    print("=" * 60)

    if _HAVE_MPL:
        plt.figure(figsize=(8, 4.4))
        plt.semilogy(range(len(hist)), hist * 1e3, "o-", lw=1.5, ms=3)
        plt.axvline(n_opt, color="r", ls="--", label=f"dump @ RT {n_opt}")
        plt.xlabel("round trip"); plt.ylabel("pulse energy [mJ] (log)")
        plt.title("Regen buildup: exponential growth then saturation")
        plt.legend(); plt.tight_layout(); plt.savefig("regen.png", dpi=130)
        print("Saved -> regen.png")
        plt.show()


if __name__ == "__main__":
    main()
