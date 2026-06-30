#!/usr/bin/env python3
"""
================================================================================
reprate.py  -  repetition-rate / average-power thermal limit
================================================================================
The paper runs at 10 Hz. Why not 100 Hz or 1 kHz? Because between shots the rod
has to shed the heat each pump pulse dumps in. Push the rep rate too high and
heat accumulates faster than the coolant removes it: the steady-state rod
temperature (and thermal lens, and stress) climbs until the beam degrades or the
rod fractures. This module models the inter-shot thermal balance.

Model (lumped thermal mass + Newton cooling)
--------------------------------------------
  Each shot deposits Q_shot of heat.
  Between shots the rod cools: dT/dt = -(T - T_cool) / tau_thermal.
  Steady-state per-cycle temperature rise builds until heat-in == heat-out.
  Average heat load = Q_shot * rep_rate, balanced by coolant: P = (T-Tc)/R_th.

Reports the steady-state center temperature vs rep rate, the max safe rep rate
for a temperature/stress budget, and where 10 Hz sits.

Run:
    python reprate.py
    python reprate.py --q-shot 5.0 --max-rise 60
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
class RepRateThermal:
    q_shot_J: float = 5.0          # heat deposited per shot [J]
    R_th: float = 12.0             # thermal resistance to coolant [K/W]
    tau_thermal_s: float = 0.5     # rod thermal time constant [s]
    max_rise_K: float = 60.0       # allowed center-temperature rise budget

    def steady_rise(self, rep_hz: float) -> float:
        """Steady-state center temperature rise at a given rep rate.
        Average power = Q_shot * rep; rise = P_avg * R_th."""
        p_avg = self.q_shot_J * rep_hz
        return p_avg * self.R_th

    def max_rep_rate(self) -> float:
        """Highest rep rate that keeps the rise within budget."""
        p_max = self.max_rise_K / self.R_th
        return p_max / self.q_shot_J

    def per_pulse_transient(self, rep_hz: float, n_shots: int = 50):
        """Simulate shot-by-shot temperature build-up to steady state."""
        period = 1.0 / rep_hz
        T = 0.0
        peaks = []
        for _ in range(n_shots):
            T += self.q_shot_J * self.R_th / self.tau_thermal_s * period  # heat in (approx)
            T *= np.exp(-period / self.tau_thermal_s)                     # cooling
            peaks.append(T)
        return np.array(peaks)


def main():
    ap = argparse.ArgumentParser(description="Rep-rate thermal limit")
    ap.add_argument("--q-shot", type=float, default=5.0, help="heat per shot [J]")
    ap.add_argument("--max-rise", type=float, default=60.0, help="temp budget [K]")
    args = ap.parse_args()

    rod = RepRateThermal(q_shot_J=args.q_shot, max_rise_K=args.max_rise)
    f_max = rod.max_rep_rate()

    print("=" * 60)
    print(" Repetition-rate thermal limit")
    print("=" * 60)
    print(f"  heat per shot       : {args.q_shot:.1f} J")
    print(f"  temperature budget  : {args.max_rise:.0f} K rise")
    print(f"  max safe rep rate   : {f_max:.1f} Hz")
    for f in (10, 50, 100, 200):
        rise = rod.steady_rise(f)
        flag = "OK" if rise <= args.max_rise else "OVER BUDGET"
        print(f"  @ {f:>4} Hz: center rise {rise:6.1f} K  ({flag})")
    print(f"  -> paper's 10 Hz uses {100*rod.steady_rise(10)/args.max_rise:.0f}% of budget")
    print("=" * 60)

    if _HAVE_MPL:
        reps = np.linspace(1, max(f_max * 1.5, 200), 200)
        rises = [rod.steady_rise(f) for f in reps]
        plt.figure(figsize=(8, 4.2))
        plt.plot(reps, rises, lw=2)
        plt.axhline(args.max_rise, color="r", ls="--", label="budget")
        plt.axvline(10, color="tab:green", ls=":", label="paper 10 Hz")
        plt.axvline(f_max, color="tab:orange", ls=":", label=f"max {f_max:.0f} Hz")
        plt.xlabel("repetition rate [Hz]"); plt.ylabel("center temp rise [K]")
        plt.title("Steady-state rod heating vs rep rate")
        plt.legend(); plt.tight_layout(); plt.savefig("reprate.png", dpi=130)
        print("Saved -> reprate.png")
        plt.show()


if __name__ == "__main__":
    main()
