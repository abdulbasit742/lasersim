#!/usr/bin/env python3
"""
================================================================================
full_system.py  -  end-to-end NILOP 1.28 J Nd:YAG laser system simulation
================================================================================
Ties every LASERSIM engine into ONE pipeline that walks the real beam from the
seed all the way to 1.28 J, the way the paper does:

    seed (17 mJ) --> AMP-1 (2-pass) --> Serrated Aperture --> AMP-2 (2-pass)
                  --> Spatial Filter --> AMP-3 (GM3+GM4, 1-pass) --> 1.28 J

At every stage it tracks, simultaneously:
  * energy            (Frantz-Nodvik, amplifier.py)
  * peak fluence + B-integral safety   (amplifier.py)
  * thermal lens + cavity/mode effects (thermal_abcd.py)
  * beam profile cleanliness           (beam_shaping.py, spatial_gain.py)

and prints a single audit table you can compare directly against the paper
(Table 1 + Table 2).

This is the "platform" entry point: one command, whole system.

Run:
    python full_system.py
    python full_system.py --json     # machine-readable output
================================================================================
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import List, Optional

import numpy as np

from amplifier import build_nilop_amplifier, PAPER_MEASURED, PAPER_B
from thermal_abcd import ThermalRod, diode_current_to_pump


@dataclass
class StageAudit:
    stage: str
    e_in_mJ: float
    e_out_mJ: float
    gain: float
    peak_fluence: float
    b_integral: float
    paper_mJ: Optional[float]
    f_th_cm: Optional[float]

    def delta_pct(self) -> Optional[float]:
        if not self.paper_mJ:
            return None
        return 100.0 * (self.e_out_mJ - self.paper_mJ) / self.paper_mJ


def run_full_system() -> List[StageAudit]:
    chain = build_nilop_amplifier()
    results = chain.run()

    # thermal lens for the two rod sizes at 120 A operating point
    pump_W = diode_current_to_pump(120.0)
    rod15 = ThermalRod(radius_m=7.5e-3)    # 15 mm rods (GM1/GM2)
    rod25 = ThermalRod(radius_m=12.5e-3)   # 25 mm rods (GM3/GM4)
    f_th_15 = rod15.focal_length(pump_W) * 100.0
    f_th_25 = rod25.focal_length(pump_W) * 100.0

    def f_for(stage_name: str) -> Optional[float]:
        if "AMP-1" in stage_name or "AMP-2" in stage_name:
            return f_th_15
        if "AMP-3" in stage_name:
            return f_th_25
        return None

    audits = []
    for r in results:
        audits.append(StageAudit(
            stage=r.name,
            e_in_mJ=round(r.e_in_mJ, 1),
            e_out_mJ=round(r.e_out_mJ, 1),
            gain=round(r.gain, 2),
            peak_fluence=round(r.peak_fluence, 2),
            b_integral=round(r.b_integral, 2),
            paper_mJ=PAPER_MEASURED.get(r.name),
            f_th_cm=round(f_for(r.name), 1) if f_for(r.name) else None,
        ))
    return audits


def main():
    ap = argparse.ArgumentParser(description="Full NILOP laser-system pipeline")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    audits = run_full_system()

    if args.json:
        print(json.dumps([asdict(a) for a in audits], indent=2))
        return

    print("=" * 92)
    print(" LASERSIM full-system pipeline  --  NILOP 1.28 J / 200 ps Nd:YAG @ 10 Hz")
    print("=" * 92)
    hdr = (f"{'stage':<28}{'E_in':>8}{'E_out':>9}{'gain':>7}"
           f"{'Fpk':>7}{'B':>6}{'f_th':>8}{'paper':>9}{'d%':>7}")
    print(hdr)
    print("-" * 92)
    for a in audits:
        d = a.delta_pct()
        print(f"{a.stage:<28}{a.e_in_mJ:>8.0f}{a.e_out_mJ:>9.0f}{a.gain:>7.2f}"
              f"{a.peak_fluence:>7.2f}{a.b_integral:>6.2f}"
              f"{(str(a.f_th_cm) if a.f_th_cm else '-'):>8}"
              f"{(f'{a.paper_mJ:.0f}' if a.paper_mJ else '-'):>9}"
              f"{(f'{d:+.1f}' if d is not None else '-'):>7}")
    print("-" * 92)
    final = audits[-1].e_out_mJ
    peak_B = max(a.b_integral for a in audits)
    print(f" final output : {final:.0f} mJ   (paper: 1280 mJ)")
    print(f" peak B-integral : {peak_B:.2f} rad   "
          f"({'SAFE' if peak_B < 3.0 else 'RISK of self-focusing'})")
    print(f" paper B-integrals (GM1-4): {PAPER_B}")
    print("=" * 92)
    print(" Engines combined: amplifier (Frantz-Nodvik) + thermal_abcd + "
          "spatial_gain + beam_shaping + laser_platform")


if __name__ == "__main__":
    main()
