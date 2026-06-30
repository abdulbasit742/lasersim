#!/usr/bin/env python3
"""
================================================================================
damage.py  -  optical damage-threshold safety auditor
================================================================================
Every surface and crystal in the chain has a Laser-Induced Damage Threshold
(LIDT). The paper keeps peak fluence in the range ~0.7-1.35 J/cm^2 (Table 1)
because few-100 ps Nd:YAG optics damage around ~1 J/cm^2. Go above and you crack
glass, pit coatings, and burn pin-holes. This module is the safety auditor:

  * Scales a reference LIDT to your pulse duration using the standard
    tau^0.5 scaling law (LIDT(tau) = LIDT_ref * sqrt(tau / tau_ref)).
  * Computes the safety margin (LIDT / peak_fluence) for every stage of the
    NILOP chain and flags anything under a chosen safety factor.
  * Reports the headroom you have to push energy before the nearest optic fails.

Run:
    python damage.py                  # audit the full NILOP chain
    python damage.py --lidt 1.0 --tau-ps 200 --safety 1.5
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

from amplifier import build_nilop_amplifier


LIDT_REF_JCM2 = 1.0
TAU_REF_PS = 200.0


@dataclass
class DamageReport:
    stage: str
    peak_fluence: float
    lidt: float
    margin: float
    safe: bool


def scaled_lidt(lidt_ref: float, tau_ps: float, tau_ref_ps: float = TAU_REF_PS) -> float:
    """Pulse-duration scaling of LIDT (tau^0.5 law, valid ~ps to ~ns)."""
    return lidt_ref * np.sqrt(tau_ps / tau_ref_ps)


def audit_chain(lidt_ref=LIDT_REF_JCM2, tau_ps=TAU_REF_PS, safety=1.2) -> List[DamageReport]:
    lidt = scaled_lidt(lidt_ref, tau_ps)
    results = build_nilop_amplifier().run()
    reports = []
    for r in results:
        if r.peak_fluence <= 0:
            continue
        margin = lidt / r.peak_fluence
        reports.append(DamageReport(r.name, r.peak_fluence, lidt, margin,
                                    margin >= safety))
    return reports


def headroom(reports: List[DamageReport]) -> float:
    """How much more energy (multiplicative) before the worst optic hits LIDT."""
    if not reports:
        return 0.0
    return min(r.margin for r in reports)


def main():
    ap = argparse.ArgumentParser(description="Optical damage-threshold auditor")
    ap.add_argument("--lidt", type=float, default=LIDT_REF_JCM2,
                    help="reference LIDT [J/cm^2] at 200 ps")
    ap.add_argument("--tau-ps", type=float, default=TAU_REF_PS)
    ap.add_argument("--safety", type=float, default=1.2,
                    help="required safety factor (LIDT/fluence)")
    args = ap.parse_args()

    reports = audit_chain(args.lidt, args.tau_ps, args.safety)
    lidt = scaled_lidt(args.lidt, args.tau_ps)

    print("=" * 70)
    print(f" Damage-threshold audit  (LIDT = {lidt:.2f} J/cm^2 @ {args.tau_ps:.0f} ps)")
    print("=" * 70)
    print(f"{'stage':<30}{'Fpk':>8}{'LIDT':>8}{'margin':>9}{'status':>10}")
    print("-" * 70)
    for r in reports:
        print(f"{r.stage:<30}{r.peak_fluence:>8.2f}{r.lidt:>8.2f}"
              f"{r.margin:>9.2f}{('OK' if r.safe else 'AT RISK'):>10}")
    print("-" * 70)
    hr = headroom(reports)
    worst = min(reports, key=lambda r: r.margin) if reports else None
    print(f" tightest margin : {hr:.2f}x at '{worst.stage if worst else '-'}'")
    print(f" energy headroom : can scale ~{hr:.2f}x before nearest optic hits LIDT")
    print("=" * 70)

    if _HAVE_MPL and reports:
        names = [r.stage.split(' (')[0] for r in reports]
        F = [r.peak_fluence for r in reports]
        plt.figure(figsize=(9, 4.2))
        plt.bar(names, F, color=["tab:green" if r.safe else "tab:red" for r in reports])
        plt.axhline(lidt, color="r", ls="--", label=f"LIDT {lidt:.2f} J/cm^2")
        plt.ylabel("peak fluence [J/cm^2]"); plt.xticks(rotation=20, ha="right")
        plt.title("Per-stage peak fluence vs damage threshold")
        plt.legend(); plt.tight_layout(); plt.savefig("damage.png", dpi=130)
        print("Saved -> damage.png")
        plt.show()


if __name__ == "__main__":
    main()
