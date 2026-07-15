#!/usr/bin/env python3
"""Cross-engine verification with explicit evidence grades and provenance."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Callable, List, Sequence

import numpy as np

from validation_evidence import EVIDENCE, build_report, validate_registry


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
    return Check("polarization", np.isclose(ratio, 2 / 3, rtol=2e-2), f"n2 ratio {ratio:.3f}")


def _thermal():
    from thermal_fem import RodThermal, solve_radial_T, thermal_focal_length
    rod = RodThermal()
    _, T1 = solve_radial_T(rod, 50.0)
    r2, T2 = solve_radial_T(rod, 200.0)
    return Check(
        "thermal",
        (T2.max() > T1.max()) and thermal_focal_length(rod, r2, T2) > 0,
        f"rise {T2.max() - rod.T_coolant:.0f} K @200W",
    )


def _cooling():
    from cooling import CoolingChannel
    ch = CoolingChannel()
    return Check("cooling", ch.wall_rise(15, 200) < ch.wall_rise(3, 200), "flow cools wall")


def _relay():
    from relay_imaging import q_from_w, w_from_q, propagate, build_nilop_relays
    q = q_from_w(3e-3)
    for relay in build_nilop_relays():
        q, _ = propagate(q, relay.elements())
    return Check("relay", 2 * w_from_q(q) > 6e-3, f"booster {2 * w_from_q(q) * 1e3:.0f} mm")


def _ase():
    from ase import ASERod
    return Check("ase", ASERod(diameter_m=25e-3).parasitic_margin(1.14) < 2.0, "below ceiling")


def _damage():
    from damage import audit_chain, headroom
    return Check("damage", headroom(audit_chain()) > 0.0, "LIDT margin positive")


def _oscillator():
    from laser_platform import Cavity, FourLevelLaser
    cav = Cavity()
    N_ss, _ = FourLevelLaser(cav).steady_state()
    return Check("oscillator", np.isclose(N_ss, cav.N_threshold, rtol=1e-6), "clamps at threshold")


def _shg():
    from shg import SHGCrystal
    crystal = SHGCrystal()
    return Check("shg", crystal.efficiency(5e13) > crystal.efficiency(1e12), "532 rises w/ I")


def _regen():
    from regen import Regen
    _, energy = Regen().optimum_dump()
    return Check("regen", energy / Regen().seed_J > 1e3, "builds up >1e3x")


def _wavefront():
    from wavefront import Wavefront
    return Check(
        "wavefront",
        Wavefront({"defocus": 0.05}).strehl() > Wavefront({"defocus": 0.2}).strehl(),
        "less aberration -> higher Strehl",
    )


def _safety():
    from safety import BeamHazard
    return Check("safety", BeamHazard(energy_J=1.28).nohd_m() > 0, "NOHD computed")


def _materials():
    from materials import get
    return Check(
        "materials",
        get("Yb:YAG").quantum_defect < get("Nd:YAG").quantum_defect,
        "Yb:YAG lower defect",
    )


def _dispersion():
    from dispersion import MATERIALS
    refractive_index = MATERIALS["fused_silica"].n(1064.0)
    return Check("dispersion", 1.44 < refractive_index < 1.46, f"silica n={refractive_index:.3f}")


def _storage():
    from storage import Storage
    return Check("storage", Storage().efficiency(20) > Storage().efficiency(400), "short pump stores better")


def _coatings():
    from coatings import reflectivity, hr_stack
    reflectance = reflectivity(hr_stack(1064, 2.3, 1.45, 15), 1064, n_substrate=1.52)
    return Check("coatings", reflectance > 0.99, f"HR R={reflectance * 100:.2f}%")


def _harmonics_chain():
    from chain_e2e import run
    _, ultraviolet_energy, wavelength = run("uv", "none")
    return Check("chain_e2e", wavelength == 355 and ultraviolet_energy > 0, f"UV {ultraviolet_energy:.0f} mJ @355nm")


def _ranging():
    from ranging import RangingLink
    return Check("ranging", RangingLink().photons_returned(1000e3) > 0, "returns photons")


def _walkoff():
    from walkoff import WalkOff
    return Check(
        "walkoff",
        WalkOff(crystal_mm=5).overlap_fraction() > WalkOff(crystal_mm=50).overlap_fraction(),
        "longer crystal less overlap",
    )


CHECKS: List[Callable[[], Check]] = [
    _energy, _b_integral, _polarization, _thermal, _cooling, _relay, _ase,
    _damage, _oscillator, _shg, _regen, _wavefront, _safety, _materials,
    _dispersion, _storage, _coatings, _harmonics_chain, _ranging, _walkoff,
]
EXPECTED_CHECK_NAMES = tuple(EVIDENCE)


def run_checks(checks: Sequence[Callable[[], Check]] = CHECKS) -> list[Check]:
    results = []
    for function in checks:
        try:
            result = function()
        except Exception as error:  # verification should report every subsystem
            result = Check(function.__name__.strip("_"), False, f"ERROR: {error}")
        results.append(result)
    return results


def render_text(results: Sequence[Check]) -> str:
    lines = [
        "=" * 96,
        " LASERSIM cross-engine verification (evidence grades are not interchangeable)",
        "=" * 96,
    ]
    for result in results:
        evidence = EVIDENCE[result.name]
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"  [{status}] [{evidence.level.upper():14}] {result.name:<14} {result.detail}")
        lines.append(f"         quantity={evidence.quantity}; unit={evidence.unit}; criterion={evidence.criterion}")
        lines.append(f"         reference={evidence.reference}")
    passed = sum(result.passed for result in results)
    by_level = {}
    for result in results:
        level = EVIDENCE[result.name].level
        by_level.setdefault(level, [0, 0])
        by_level[level][1] += 1
        by_level[level][0] += int(result.passed)
    lines.extend(["-" * 96, f"  {passed}/{len(results)} checks passed"])
    lines.append("  " + " | ".join(f"{level}: {counts[0]}/{counts[1]}" for level, counts in by_level.items()))
    lines.append("  Note: invariant and smoke checks are not experimental validation.")
    lines.append("=" * 96)
    return "\n".join(lines)


def _write_output(path: Path, payload: str, overwrite: bool) -> None:
    path = path.expanduser().resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + ("" if payload.endswith("\n") else "\n"), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path, help="write the report to this path")
    parser.add_argument("--overwrite", action="store_true", help="allow replacing an existing report")
    args = parser.parse_args(argv)

    validate_registry(EXPECTED_CHECK_NAMES)
    results = run_checks()
    report = build_report(results)
    payload = json.dumps(report, indent=2, sort_keys=True) if args.format == "json" else render_text(results)

    try:
        if args.output:
            _write_output(args.output, payload, args.overwrite)
        else:
            print(payload)
    except OSError as error:
        print(f"validation report error: {error}", file=sys.stderr)
        return 2

    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
