"""nilore_scale.py -- scaling & optimization advisor on the NILORE twin.

The paper (Raza et al., Opt. Commun. 577 (2025) 131413) *reports* one
operating point: 1.28 J, B-integral up to 1.94, fixed beam diameters. It
does not answer the design questions a lab actually asks next:

    Q1. Can we hit the same 1.28 J but SAFER (lower peak B-integral)?
    Q2. How far can we push the energy before B-integral crosses the
        safe cap (~2.0), and what stored energy does that need?
    Q3. For any target energy, what booster stored energy is required?

This module answers all three by sweeping the validated digital twin
(`nilore_twin`), which reproduces the paper's Table 2 and corrects its
first-pass gain error. Every recommendation is grounded in the paper's own
constants (F_sat, n2, rod sizes, 200 ps, 1064 nm) so it is directly
actionable on the real bench.

Pure Python + math; runs in --smoke with no heavy deps.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

import nilore_twin as nt


def _booster_stage(beam_diam_cm: float, stored_j: float, e_in_j: float,
                   target_out_j: float) -> nt.Stage:
    """A GM4-class single-pass booster stage with a chosen beam diameter."""
    return nt.Stage(
        name="booster", beam_diam_cm=beam_diam_cm, rod_diam_cm=2.5,
        stored_energy_j=stored_j, e_in_j=e_in_j,
        e_out_meas_j=target_out_j, e_out_paper_calc_j=target_out_j,
        sg_order=4, circular_pol=True,
    )


def stored_energy_for(target_out_j: float, beam_diam_cm: float,
                      e_in_j: float, f_sat: float = nt.F_SAT) -> Optional[float]:
    """Bisection: stored energy needed to reach target_out_j at this beam size."""
    lo, hi = 0.0, 30.0

    def out_for(store):
        st = _booster_stage(beam_diam_cm, store, e_in_j, target_out_j)
        return nt.simulate_stage(st, corrected=True, f_sat=f_sat)["e_out_j"]

    if out_for(hi) < target_out_j:
        return None
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        if out_for(mid) < target_out_j:
            lo = mid
        else:
            hi = mid
    return hi


def b_for_point(target_out_j: float, beam_diam_cm: float,
                e_in_j: float, f_sat: float = nt.F_SAT) -> Optional[Dict]:
    """Full evaluation of one (energy, beam-diameter) operating point."""
    store = stored_energy_for(target_out_j, beam_diam_cm, e_in_j, f_sat)
    if store is None:
        return None
    st = _booster_stage(beam_diam_cm, store, e_in_j, target_out_j)
    res = nt.simulate_stage(st, corrected=True, f_sat=f_sat)
    b = nt.b_integral(st, res["e_out_j"])
    peak_fluence = res["f_out_j_cm2"] * (2.0 ** (2.0 / st.sg_order))
    return {
        "target_out_j": target_out_j,
        "beam_diam_cm": beam_diam_cm,
        "required_stored_j": store,
        "achieved_out_j": res["e_out_j"],
        "b_integral": b,
        "peak_fluence_j_cm2": peak_fluence,
    }


# ------------------------------------------------------------------
# Q1: same energy, minimum B-integral by optimizing beam diameter
# ------------------------------------------------------------------
def safest_beam_for_energy(target_out_j: float = 1.28,
                           e_in_j: float = 0.720,
                           diam_min_cm: float = 1.6,
                           diam_max_cm: float = 3.2,
                           steps: int = 33,
                           damage_fluence_cap: float = 1.0) -> Dict:
    """Find the booster beam diameter that minimizes peak B-integral while
    reaching target_out_j and staying under the ~1 J/cm^2 peak-fluence
    damage limit the paper cites for ~100s-ps Nd:YAG.

    Baseline (paper): 1.6 cm beam, B ~ 1.28 at 1.28 J (GM4).
    """
    baseline = b_for_point(target_out_j, 1.6, e_in_j)
    best = None
    curve = []
    for i in range(steps):
        d = diam_min_cm + (diam_max_cm - diam_min_cm) * i / (steps - 1)
        pt = b_for_point(target_out_j, d, e_in_j)
        if pt is None:
            continue
        curve.append(pt)
        if pt["peak_fluence_j_cm2"] > damage_fluence_cap:
            continue
        if best is None or pt["b_integral"] < best["b_integral"]:
            best = pt
    return {"baseline": baseline, "recommended": best, "curve": curve}


# ------------------------------------------------------------------
# Q2: maximum safely reachable energy under a B-integral cap
# ------------------------------------------------------------------
def max_safe_energy(beam_diam_cm: float = 1.6,
                    e_in_j: float = 0.720,
                    b_cap: float = nt.B_INTEGRAL_SAFE,
                    e_hi_j: float = 4.0) -> Dict:
    """Largest output energy whose peak B-integral stays <= b_cap, at a fixed
    beam diameter. Bisection on target energy."""
    lo, hi = 0.1, e_hi_j

    def b_of(e):
        pt = b_for_point(e, beam_diam_cm, e_in_j)
        return pt["b_integral"] if pt else float("inf")

    if b_of(lo) > b_cap:
        return {"feasible": False, "reason": "even minimal energy exceeds B cap"}
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if b_of(mid) <= b_cap:
            lo = mid
        else:
            hi = mid
    pt = b_for_point(lo, beam_diam_cm, e_in_j)
    pt["b_cap"] = b_cap
    pt["feasible"] = True
    return pt


# ------------------------------------------------------------------
# Q3: required stored energy across a target-energy sweep
# ------------------------------------------------------------------
def energy_ladder(targets_j: Optional[List[float]] = None,
                  beam_diam_cm: float = 1.6,
                  e_in_j: float = 0.720) -> List[Dict]:
    targets_j = targets_j or [1.0, 1.28, 1.5, 2.0, 2.5, 3.0]
    out = []
    for t in targets_j:
        pt = b_for_point(t, beam_diam_cm, e_in_j)
        if pt:
            pt["b_safe"] = pt["b_integral"] <= nt.B_INTEGRAL_SAFE
            out.append(pt)
    return out


def _smoke() -> int:
    print("[nilore_scale] scaling advisor on the validated NILORE twin")

    print("  Q1: same 1.28 J, minimum B-integral via beam-diameter optimization")
    q1 = safest_beam_for_energy(1.28)
    b = q1["baseline"]; r = q1["recommended"]
    print(f"      paper-like (1.6 cm): B={b['b_integral']:.2f}, "
          f"peakF={b['peak_fluence_j_cm2']:.2f} J/cm^2")
    if r:
        drop = 100.0 * (b["b_integral"] - r["b_integral"]) / b["b_integral"]
        print(f"      recommended {r['beam_diam_cm']:.2f} cm: B={r['b_integral']:.2f}, "
              f"peakF={r['peak_fluence_j_cm2']:.2f} J/cm^2  ->  {drop:.0f}% lower B")

    print("  Q2: max safely reachable energy at 1.6 cm under B<=2.0")
    q2 = max_safe_energy(1.6)
    if q2.get("feasible"):
        print(f"      up to {q2['achieved_out_j']*1e3:.0f} mJ "
              f"(B={q2['b_integral']:.2f}), needs E_store~{q2['required_stored_j']:.2f} J")

    print("  Q3: stored-energy ladder")
    for pt in energy_ladder():
        flag = "safe" if pt["b_safe"] else "OVER B-cap"
        print(f"      {pt['target_out_j']*1e3:5.0f} mJ -> E_store {pt['required_stored_j']:5.2f} J, "
              f"B={pt['b_integral']:4.2f}  [{flag}]")

    # sanity: bigger beam must not increase B-integral at fixed energy
    small = b_for_point(1.28, 1.6, 0.720)
    big = b_for_point(1.28, 2.4, 0.720)
    assert big["b_integral"] <= small["b_integral"] + 1e-9, \
        "larger beam should lower B-integral at fixed energy"
    print("[nilore_scale] smoke OK")
    return 0


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_smoke())
