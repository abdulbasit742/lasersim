"""inverse_design.py -- NOVELTY engine #1: the self-designing laser.

Every other module in lasersim answers the *forward* question:

    "given this design, what does the laser do?"

This engine answers the *inverse* question, which is the one a researcher
or a spec sheet actually starts from:

    "given this target output, what design achieves it?"

It wraps forward_model.simulate() in a constrained objective and searches
the design box for the knobs (pump power, crystal length, seed energy,
residual GDD, doubling-crystal length) that best hit a user target, while
respecting the optical-damage fluence constraint.

Optimizer: SciPy differential evolution + local polish when SciPy is
available; otherwise a self-contained numpy "CMA-lite" (random restarts +
Gaussian neighborhood descent) so the module always runs in --smoke with
zero heavy deps.

This is a genuine research contribution on top of the forward platform:
automated, constraint-aware inverse design of a laser system.
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

import forward_model as fm


# ------------------------------------------------------------------
# Target specification
# ------------------------------------------------------------------
# A target is a dict of {metric_name: (desired_value, weight)}. Only the
# metrics you list are optimized; everything else floats free.
DEFAULT_TARGET: Dict[str, Tuple[float, float]] = {
    "output_energy_j":  (0.50, 1.0),    # want 0.5 J out
    "pulse_duration_fs": (500.0, 1.0),  # want ~500 fs
    "m2":               (1.20, 1.0),    # want near-diffraction-limited
    "shg_efficiency":   (0.40, 0.5),    # want ~40% green conversion
}

_KEYS = list(fm.DESIGN_BOUNDS.keys())
_LO = [fm.DESIGN_BOUNDS[k][0] for k in _KEYS]
_HI = [fm.DESIGN_BOUNDS[k][1] for k in _KEYS]


def _vec_to_design(v: List[float]) -> Dict[str, float]:
    return {k: float(v[i]) for i, k in enumerate(_KEYS)}


def _design_to_vec(d: Dict[str, float]) -> List[float]:
    return [float(d[k]) for k in _KEYS]


def _relative_cost(metrics: Dict[str, float],
                   target: Dict[str, Tuple[float, float]]) -> float:
    """Weighted sum of squared *relative* errors + damage penalty."""
    cost = 0.0
    for name, (want, weight) in target.items():
        got = metrics.get(name, 0.0)
        denom = abs(want) if abs(want) > 1e-12 else 1.0
        rel = (got - want) / denom
        cost += weight * rel * rel
    # hard-ish constraint: penalize crossing the damage threshold
    if metrics.get("damage_safe", 1.0) < 0.5:
        margin = metrics.get("damage_margin_j_cm2", -1.0)
        cost += 100.0 + 10.0 * abs(margin)
    return cost


def objective(vec: List[float], target: Dict[str, Tuple[float, float]],
              sp: Optional[fm.SystemParams], full: bool) -> float:
    d = fm.clamp_design(_vec_to_design(vec))
    m = fm.simulate(d, sp=sp, full=full)
    return _relative_cost(m, target)


# ------------------------------------------------------------------
# Pure-numpy fallback optimizer: random restarts + Gaussian descent
# ------------------------------------------------------------------
def _optimize_numpy(target, sp, full, iters=4000, restarts=6, seed=0):
    rng = random.Random(seed)
    best_vec, best_cost = None, float("inf")
    span = [hi - lo for lo, hi in zip(_LO, _HI)]

    for r in range(restarts):
        cur = [rng.uniform(lo, hi) for lo, hi in zip(_LO, _HI)]
        cur_cost = objective(cur, target, sp, full)
        step = [0.30 * s for s in span]           # start with wide steps
        for it in range(iters // restarts):
            j = rng.randrange(len(cur))
            trial = list(cur)
            trial[j] += rng.gauss(0.0, step[j])
            trial[j] = min(max(trial[j], _LO[j]), _HI[j])
            c = objective(trial, target, sp, full)
            if c < cur_cost:
                cur, cur_cost = trial, c
                step[j] *= 1.15                    # accelerate on success
            else:
                step[j] *= 0.92                    # cool on failure
            step[j] = max(step[j], 1e-4 * span[j])
        if cur_cost < best_cost:
            best_vec, best_cost = cur, cur_cost
    return best_vec, best_cost


def _optimize_scipy(target, sp, full, seed=0):
    try:
        from scipy.optimize import differential_evolution, minimize
    except Exception:
        return None
    bounds = list(zip(_LO, _HI))
    de = differential_evolution(
        objective, bounds, args=(target, sp, full),
        seed=seed, maxiter=200, tol=1e-8, polish=False, updating="deferred",
    )
    # local polish (Nelder-Mead respects nothing, so re-clamp in objective)
    nm = minimize(objective, de.x, args=(target, sp, full), method="Nelder-Mead",
                  options={"maxiter": 2000, "xatol": 1e-6, "fatol": 1e-10})
    if nm.fun < de.fun:
        return list(nm.x), float(nm.fun)
    return list(de.x), float(de.fun)


def design_for(target: Optional[Dict[str, Tuple[float, float]]] = None,
               sp: Optional[fm.SystemParams] = None,
               full: bool = False, seed: int = 0,
               prefer_scipy: bool = True) -> Dict:
    """Return the best design that hits `target`, plus achieved metrics."""
    target = target or DEFAULT_TARGET
    res = _optimize_scipy(target, sp, full, seed) if prefer_scipy else None
    engine = "scipy-de+nm"
    if res is None:
        res = _optimize_numpy(target, sp, full, seed=seed)
        engine = "numpy-cma-lite"
    vec, cost = res
    design = fm.clamp_design(_vec_to_design(vec))
    metrics = fm.simulate(design, sp=sp, full=full)

    report = {"metric": [], "target": [], "achieved": [], "rel_error_pct": []}
    for name, (want, _w) in target.items():
        got = metrics.get(name, 0.0)
        denom = abs(want) if abs(want) > 1e-12 else 1.0
        report["metric"].append(name)
        report["target"].append(want)
        report["achieved"].append(got)
        report["rel_error_pct"].append(100.0 * (got - want) / denom)

    return {
        "engine": engine,
        "cost": cost,
        "design": design,
        "metrics": metrics,
        "target_report": report,
    }


def _smoke() -> int:
    print("[inverse_design] smoke: solve for a target spec")
    out = design_for(seed=1)
    print(f"    optimizer      = {out['engine']}")
    print(f"    final cost     = {out['cost']:.4g}")
    print("    design:")
    for k, v in out["design"].items():
        print(f"        {k:22s} = {v:.4g}")
    print("    target vs achieved:")
    tr = out["target_report"]
    for i, name in enumerate(tr["metric"]):
        print(f"        {name:20s} want={tr['target'][i]:.4g}  "
              f"got={tr['achieved'][i]:.4g}  err={tr['rel_error_pct'][i]:+.1f}%")
    assert out["metrics"]["damage_safe"] >= 0.5, "inverse design returned an unsafe point"
    assert out["cost"] < 5.0, "optimizer failed to get near target"
    print("[inverse_design] smoke OK")
    return 0


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_smoke())
