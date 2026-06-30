#!/usr/bin/env python3
"""
================================================================================
validate.py  -  cross-engine validation capstone
================================================================================
The single source of truth for "does LASERSIM still reproduce the paper?" It
runs EVERY engine on the NILOP 1.28 J / 200 ps Nd:YAG system and checks each
result against a published number or a known physical bound, then prints one
pass/fail scorecard.

Exit code is 0 if all checks pass, 1 otherwise (CI-friendly).

Run:
    python validate.py
================================================================================
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, List

import numpy as np


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _energy() -> Check:
    from amplifier import build_nilop_amplifier
    final = build_nilop_amplifier().run()[-1].e_out_mJ
    ok = 950.0 <= final <= 1600.0
    return Check("energy", ok, f"final {final:.0f} mJ (paper 1280)")


def _b_integral() -> Check:
    from amplifier import build_nilop_amplifier
    peak = max(r.b_integral for r in build_nilop_amplifier().run())
    return Check("B-integral", peak < 3.0, f"peak {peak:.2f} rad (limit 3.0)")


def _polarization() -> Check:
    from polarization import qwp, H, n2_reduction
    circ = qwp(np.pi / 4) @ H
    ratio = n2_reduction(circ) / n2_reduction(H)
    ok = np.isclose(ratio, 2.0 / 3.0, rtol=2e-2)
    return Check("polarization", ok, f"n2 ratio {ratio:.3f} (expect 0.667)")


def _thermal() -> Check:
    from thermal_fem import RodThermal, solve_radial_T, thermal_focal_length
    rod = RodThermal()
    _, T1 = solve_radial_T(rod, 50.0)
    r2, T2 = solve_radial_T(rod, 200.0)
    ok = (T2.max() > T1.max()) and (thermal_focal_length(rod, r2, T2) > 0)
    return Check("thermal", ok, f"center rise {T2.max()-rod.T_coolant:.1f} K @200W")


def _relay() -> Check:
    from relay_imaging import q_from_w, w_from_q, propagate, build_nilop_relays
    q = q_from_w(3e-3)
    diam0 = 6e-3
    for relay in build_nilop_relays():
        q, _ = propagate(q, relay.elements())
    final_d = 2 * w_from_q(q)
    return Check("relay", final_d > diam0, f"booster diameter {final_d*1e3:.1f} mm")


def _ase() -> Check:
    from ase import ASERod
    rod = ASERod(diameter_m=25e-3)
    margin = rod.parasitic_margin(1.14)
    return Check("ase", margin < 2.0, f"parasitic loop gain {margin:.2f} @1.14 J")


def _damage() -> Check:
    from damage import audit_chain, headroom
    hr = headroom(audit_chain())
    return Check("damage", hr > 0.0, f"tightest LIDT margin {hr:.2f}x")


def _oscillator() -> Check:
    from laser_platform import Cavity, FourLevelLaser
    cav = Cavity()
    N_ss, _ = FourLevelLaser(cav).steady_state()
    ok = np.isclose(N_ss, cav.N_threshold, rtol=1e-6)
    return Check("oscillator", ok, "inversion clamps at threshold")


def _shg() -> Check:
    from shg import SHGCrystal
    c = SHGCrystal()
    ok = c.efficiency(5e13) > c.efficiency(1e12)
    return Check("shg", ok, "532 nm conversion rises with intensity")


CHECKS: List[Callable[[], Check]] = [
    _energy, _b_integral, _polarization, _thermal,
    _relay, _ase, _damage, _oscillator, _shg,
]


def main() -> int:
    print("=" * 66)
    print(" LASERSIM cross-engine validation  (vs NILOP 1.28 J Nd:YAG paper)")
    print("=" * 66)
    results = []
    for fn in CHECKS:
        try:
            c = fn()
        except Exception as e:
            c = Check(fn.__name__.strip('_'), False, f"ERROR: {e}")
        results.append(c)
        mark = "PASS" if c.passed else "FAIL"
        print(f"  [{mark}]  {c.name:<12} {c.detail}")
    print("-" * 66)
    n_pass = sum(r.passed for r in results)
    print(f"  {n_pass}/{len(results)} checks passed")
    print("=" * 66)
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
