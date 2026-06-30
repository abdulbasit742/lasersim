#!/usr/bin/env python3
"""
================================================================================
validate.py  -  cross-engine validation capstone
================================================================================
Runs EVERY major engine on the NILOP 1.28 J / 200 ps Nd:YAG system and checks
each result against a published number or a known physical bound, then prints
one pass/fail scorecard. Exit code 0 if all pass (CI-friendly).
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


def _energy():
    from amplifier import build_nilop_amplifier
    final = build_nilop_amplifier().run()[-1].e_out_mJ
    return Check("energy", 950 <= final <= 1600, f"final {final:.0f} mJ (paper 1280)")


def _b_integral():
    from amplifier import build_nilop_amplifier
    peak = max(r.b_integral for r in build_nilop_amplifier().run())
    return Check("B-integral", peak < 3.0, f"peak {peak:.2f} rad (<3.0)")


def _polarization():
    from polarization import qwp, H, n2_reduction
    ratio = n2_reduction(qwp(np.pi / 4) @ H) / n2_reduction(H)
    return Check("polarization", np.isclose(ratio, 2/3, rtol=2e-2), f"n2 ratio {ratio:.3f}")


def _thermal():
    from thermal_fem import RodThermal, solve_radial_T, thermal_focal_length
    rod = RodThermal()
    _, T1 = solve_radial_T(rod, 50.0)
    r2, T2 = solve_radial_T(rod, 200.0)
    ok = (T2.max() > T1.max()) and (thermal_focal_length(rod, r2, T2) > 0)
    return Check("thermal", ok, f"rise {T2.max()-rod.T_coolant:.0f} K @200W")


def _cooling():
    from cooling import CoolingChannel
    ch = CoolingChannel()
    return Check("cooling", ch.wall_rise(15, 200) < ch.wall_rise(3, 200),
                 "more flow -> cooler wall")


def _relay():
    from relay_imaging import q_from_w, w_from_q, propagate, build_nilop_relays
    q = q_from_w(3e-3)
    for relay in build_nilop_relays():
        q, _ = propagate(q, relay.elements())
    d = 2 * w_from_q(q)
    return Check("relay", d > 6e-3, f"booster {d*1e3:.0f} mm")


def _ase():
    from ase import ASERod
    return Check("ase", ASERod(diameter_m=25e-3).parasitic_margin(1.14) < 2.0,
                 "below parasitic ceiling")


def _damage():
    from damage import audit_chain, headroom
    return Check("damage", headroom(audit_chain()) > 0.0, "LIDT margin positive")


def _oscillator():
    from laser_platform import Cavity, FourLevelLaser
    cav = Cavity()
    N_ss, _ = FourLevelLaser(cav).steady_state()
    return Check("oscillator", np.isclose(N_ss, cav.N_threshold, rtol=1e-6),
                 "inversion clamps at threshold")


def _shg():
    from shg import SHGCrystal
    c = SHGCrystal()
    return Check("shg", c.efficiency(5e13) > c.efficiency(1e12), "532 nm rises w/ I")


def _regen():
    from regen import Regen
    _, e = Regen().optimum_dump()
    return Check("regen", e / Regen().seed_J > 1e3, "regen builds up >1e3x")


def _wavefront():
    from wavefront import Wavefront
    a = Wavefront({"defocus": 0.2})
    b = Wavefront({"defocus": 0.05})
    return Check("wavefront", b.strehl() > a.strehl(), "less aberration -> higher Strehl")


def _safety():
    from safety import BeamHazard
    return Check("safety", BeamHazard(energy_J=1.28).nohd_m() > 0, "NOHD computed")


def _materials():
    from materials import get
    return Check("materials", get("Yb:YAG").quantum_defect < get("Nd:YAG").quantum_defect,
                 "Yb:YAG lower defect")


CHECKS: List[Callable[[], Check]] = [
    _energy, _b_integral, _polarization, _thermal, _cooling, _relay, _ase,
    _damage, _oscillator, _shg, _regen, _wavefront, _safety, _materials,
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
        print(f"  [{'PASS' if c.passed else 'FAIL'}]  {c.name:<14} {c.detail}")
    print("-" * 66)
    n = sum(r.passed for r in results)
    print(f"  {n}/{len(results)} checks passed")
    print("=" * 66)
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
