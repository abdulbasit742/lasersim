#!/usr/bin/env python3
"""
================================================================================
efficiency.py  -  end-to-end wall-plug (electrical-to-optical) efficiency budget
================================================================================
A high-energy laser is also an energy-conversion machine. This module tracks
every efficiency stage from the wall socket to the delivered photons, so you can
see where the power actually goes and what the real "plug efficiency" is:

    mains AC
      x driver efficiency        (power supply -> diode electrical)
      x diode efficiency         (electrical -> 808 nm optical)
      x transfer/absorption      (pump light absorbed in the rod)
      x quantum defect           (808 -> 1064 nm photon energy ratio)
      x storage efficiency       (upper-state lifetime vs pump pulse)
      x extraction efficiency    (stored -> extracted in the pulse)
      [x harmonic efficiency]    (optional 1064 -> 532 / 355)

Reports each stage, the cumulative efficiency, and the average optical power
delivered at 10 Hz, plus the electrical wall draw.

Run:
    python efficiency.py
    python efficiency.py --harmonic green
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import List, Tuple

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class EfficiencyStage:
    name: str
    eta: float
    note: str = ""


@dataclass
class PlugBudget:
    rep_hz: float = 10.0
    output_energy_J: float = 1.28
    stages: List[EfficiencyStage] = field(default_factory=list)

    def cumulative(self) -> List[Tuple[str, float, float]]:
        out = []
        cum = 1.0
        for s in self.stages:
            cum *= s.eta
            out.append((s.name, s.eta, cum))
        return out

    @property
    def total_eta(self) -> float:
        cum = 1.0
        for s in self.stages:
            cum *= s.eta
        return cum

    @property
    def avg_optical_power_W(self) -> float:
        return self.output_energy_J * self.rep_hz

    @property
    def wall_power_W(self) -> float:
        return self.avg_optical_power_W / self.total_eta if self.total_eta > 0 else float("inf")


def default_budget(harmonic: str = "none") -> PlugBudget:
    stages = [
        EfficiencyStage("driver (AC->diode elec)", 0.85, "switching power supply"),
        EfficiencyStage("diode (elec->808nm)", 0.50, "QCW laser diode bars"),
        EfficiencyStage("pump transfer/absorption", 0.85, "coupling + absorption in rod"),
        EfficiencyStage("quantum defect (808->1064)", 808.0 / 1064.0, "photon energy ratio"),
        EfficiencyStage("storage (lifetime vs pump)", 0.80, "200 us pump vs 230 us tau"),
        EfficiencyStage("extraction (stored->pulse)", 0.50, "Frantz-Nodvik extraction"),
    ]
    if harmonic == "green":
        stages.append(EfficiencyStage("SHG (1064->532)", 0.55, "second harmonic"))
    elif harmonic == "uv":
        stages.append(EfficiencyStage("THG (1064->355)", 0.30, "third harmonic"))
    return PlugBudget(stages=stages)


def main():
    ap = argparse.ArgumentParser(description="Wall-plug efficiency budget")
    ap.add_argument("--harmonic", choices=["none", "green", "uv"], default="none")
    args = ap.parse_args()

    budget = default_budget(args.harmonic)

    print("=" * 68)
    print(" Wall-plug efficiency budget (mains -> delivered photons)")
    print("=" * 68)
    print(f"{'stage':<34}{'eta':>8}{'cumulative':>14}")
    print("-" * 68)
    for name, eta, cum in budget.cumulative():
        print(f"{name:<34}{eta:>8.3f}{cum*100:>13.2f}%")
    print("-" * 68)
    print(f"  total wall-plug efficiency : {budget.total_eta*100:.2f} %")
    print(f"  avg optical power @ {budget.rep_hz:.0f} Hz : {budget.avg_optical_power_W:.1f} W")
    print(f"  electrical wall draw       : {budget.wall_power_W:.0f} W")
    print("=" * 68)

    if _HAVE_MPL:
        rows = budget.cumulative()
        names = [r[0] for r in rows]
        cum = [r[2] * 100 for r in rows]
        plt.figure(figsize=(9, 4.4))
        plt.plot(range(len(cum)), cum, "o-", lw=2)
        plt.xticks(range(len(names)), [n.split(' (')[0] for n in names],
                   rotation=25, ha="right", fontsize=8)
        plt.ylabel("cumulative efficiency [%]")
        plt.title("Power flow: wall socket to delivered photons")
        plt.tight_layout(); plt.savefig("efficiency.png", dpi=130)
        print("Saved -> efficiency.png")
        plt.show()


if __name__ == "__main__":
    main()
