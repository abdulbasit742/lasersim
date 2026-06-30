#!/usr/bin/env python3
"""
================================================================================
landscape.py  -  where this system sits among published ps Nd:YAG DPSSL lasers
================================================================================
The paper's introduction surveys the prior art in high-energy picosecond
diode-pumped Nd:YAG systems. This module encodes those published systems as data
and places the NILOP 1.28 J result in context: it computes peak power and a
brightness-like figure of merit (energy / duration) for each, ranks them, and
shows by how much the NILOP system advances the energy record.

This is the 'related work' engine: useful for a thesis intro, a grant, or just
knowing how good your number really is.

Data are taken from the references cited in:
  K. Raza et al., Opt. Commun. 577 (2025) 131413 (refs [16-22]).

Run:
    python landscape.py
    python landscape.py --sort brightness
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class System:
    label: str
    energy_mJ: float
    duration_ps: float
    rep_hz: float
    ref: str
    is_this_work: bool = False

    @property
    def peak_power_GW(self) -> float:
        # peak power ~ energy / duration (approximate, ignores pulse shape factor)
        return (self.energy_mJ * 1e-3) / (self.duration_ps * 1e-12) / 1e9

    @property
    def avg_power_W(self) -> float:
        return self.energy_mJ * 1e-3 * self.rep_hz


def published_systems() -> List[System]:
    return [
        System("Noom 2013", 130, 60, 300, "[16] Opt. Lett. 38, 3021"),
        System("Kawasaki 2019", 190, 100, 100, "[17] Opt. Express 27, 19555"),
        System("Yahia 2018", 235, 600, 10, "[18] Opt. Express 26, 8609"),
        System("Huang 2020", 363, 63, 100, "[19] IEEE JQE 56, 1"),
        System("Kornev 2018", 430, 100, 200, "[20] Opt. Lett. 43, 4394"),
        System("Balmashnov 2016", 360, 100, 200, "[22] ICLO 2016"),
        System("Kornev 2020", 920, 76, 200, "[21] Electron. Lett. 56, 339"),
        System("NILOP 2025 (this)", 1280, 200, 10,
               "Raza 2025, Opt. Commun. 577", is_this_work=True),
    ]


def main():
    ap = argparse.ArgumentParser(description="Published ps Nd:YAG DPSSL landscape")
    ap.add_argument("--sort", choices=["energy", "peak", "brightness"],
                    default="energy")
    args = ap.parse_args()

    systems = published_systems()
    keyfn = {
        "energy": lambda s: s.energy_mJ,
        "peak": lambda s: s.peak_power_GW,
        "brightness": lambda s: s.peak_power_GW * s.rep_hz,
    }[args.sort]
    systems.sort(key=keyfn, reverse=True)

    print("=" * 78)
    print(" Published high-energy picosecond Nd:YAG DPSSL systems")
    print("=" * 78)
    print(f"{'system':<22}{'E (mJ)':>8}{'tau (ps)':>10}{'rep (Hz)':>10}"
          f"{'Ppk (GW)':>10}{'Pavg (W)':>10}")
    print("-" * 78)
    for s in systems:
        star = " *" if s.is_this_work else ""
        print(f"{s.label:<22}{s.energy_mJ:>8.0f}{s.duration_ps:>10.0f}"
              f"{s.rep_hz:>10.0f}{s.peak_power_GW:>10.2f}{s.avg_power_W:>10.2f}{star}")
    print("-" * 78)

    this = next(s for s in systems if s.is_this_work)
    others = [s for s in systems if not s.is_this_work]
    prev_record = max(others, key=lambda s: s.energy_mJ)
    print(f" energy record advance: {this.energy_mJ:.0f} mJ vs previous best "
          f"{prev_record.energy_mJ:.0f} mJ ({prev_record.label}) "
          f"= {this.energy_mJ/prev_record.energy_mJ:.2f}x")
    print(f" this work peak power : {this.peak_power_GW:.2f} GW")
    print("=" * 78)

    if _HAVE_MPL:
        labels = [s.label for s in systems]
        E = [s.energy_mJ for s in systems]
        colors = ["tab:red" if s.is_this_work else "tab:blue" for s in systems]
        plt.figure(figsize=(10, 4.6))
        plt.barh(labels, E, color=colors)
        plt.xlabel("pulse energy [mJ]")
        plt.title("High-energy ps Nd:YAG DPSSL systems (red = this work)")
        plt.gca().invert_yaxis()
        plt.tight_layout(); plt.savefig("landscape.png", dpi=130)
        print("Saved -> landscape.png")
        plt.show()


if __name__ == "__main__":
    main()
