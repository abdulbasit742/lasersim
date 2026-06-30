#!/usr/bin/env python3
"""
================================================================================
sweep.py  -  batch parameter-sweep + optimization engine
================================================================================
The whole point of a platform: don't run ONE simulation, run THOUSANDS and find
the optimum. This engine sweeps any set of parameters across the LASERSIM
models, runs them in parallel, and reports the best configuration.

Features
--------
  * N-dimensional grid sweeps over any model parameters.
  * Parallel execution across CPU cores (ProcessPoolExecutor).
  * Optional GPU/large-array backend: set LASERSIM_XP=cupy to use CuPy on your
    RTX A6000s for the vectorized amplifier sweeps (falls back to numpy).
  * Built-in objectives: maximize output energy while keeping B-integral safe.
  * CSV export of the full result table.

Run:
    python sweep.py amplifier       # sweep amplifier stored-energy & beam size
    python sweep.py oscillator      # sweep pump ratio & output coupler
    python sweep.py --csv out.csv amplifier
================================================================================
"""
from __future__ import annotations

import argparse
import csv
import itertools
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

# Optional GPU backend (CuPy). Defaults to numpy. Your 2x RTX A6000 can drive
# the vectorized amplifier sweeps if cupy is installed and LASERSIM_XP=cupy.
if os.environ.get("LASERSIM_XP", "numpy").lower() == "cupy":
    try:
        import cupy as xp  # type: ignore
        _BACKEND = "cupy"
    except Exception:
        import numpy as xp
        _BACKEND = "numpy (cupy unavailable)"
else:
    import numpy as xp
    _BACKEND = "numpy"


# ==============================================================================
# GENERIC GRID SWEEP
# ==============================================================================
@dataclass
class SweepSpec:
    """A named axis to sweep: parameter name + values."""
    name: str
    values: Sequence[float]


def grid(specs: List[SweepSpec]) -> List[Dict[str, float]]:
    """Cartesian product of all axes -> list of param dicts."""
    names = [s.name for s in specs]
    combos = itertools.product(*[s.values for s in specs])
    return [dict(zip(names, c)) for c in combos]


def run_grid(eval_fn: Callable[[Dict[str, float]], Dict[str, float]],
             points: List[Dict[str, float]],
             workers: int = 0) -> List[Dict[str, float]]:
    """Evaluate eval_fn over all points, optionally in parallel."""
    if workers and workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rows = list(ex.map(eval_fn, points))
    else:
        rows = [eval_fn(p) for p in points]
    # merge inputs + outputs
    return [{**p, **r} for p, r in zip(points, rows)]


def best(rows: List[Dict[str, float]], objective: str,
         maximize: bool = True,
         constraint: Callable[[Dict[str, float]], bool] = None) -> Dict[str, float]:
    feasible = [r for r in rows if (constraint is None or constraint(r))]
    if not feasible:
        return {}
    return (max if maximize else min)(feasible, key=lambda r: r[objective])


# ==============================================================================
# VECTORIZED AMPLIFIER SWEEP (GPU-ready)
# ==============================================================================
def vectorized_amplifier_sweep(f_store_grid, beam_radius_grid,
                               f_sat=0.3, f_in=0.05, rod_len_cm=13.0,
                               n2=6.21e-16, lam_cm=1064e-7, tau_p=200e-12,
                               circular=True):
    """Fully vectorized single-pass Frantz-Nodvik over a 2D parameter grid.
    Runs on numpy or cupy (xp). Returns (E_out, B) arrays [J, rad].
    Beam radius in cm; f_store, f_sat, f_in in J/cm^2."""
    FS, BR = xp.meshgrid(xp.asarray(f_store_grid), xp.asarray(beam_radius_grid))
    g0 = xp.exp(FS / f_sat)
    f_out = f_sat * xp.log(1.0 + g0 * (xp.expm1(f_in / f_sat)))
    area = xp.pi * BR ** 2
    e_out = f_out * area
    # peak fluence for a 4th-order super-Gaussian, then peak intensity & B
    f_peak = (2.0 ** (2.0 / 4)) * e_out / (xp.pi * BR * BR)
    I_peak = 0.937 * f_peak / tau_p
    n2_eff = n2 * (2.0 / 3.0 if circular else 1.0)
    B = (2.0 * xp.pi / lam_cm) * n2_eff * I_peak * rod_len_cm
    return e_out, B


# ==============================================================================
# OBJECTIVE WRAPPERS (for the generic grid path / parallel CPU)
# ==============================================================================
def eval_amplifier(params: Dict[str, float]) -> Dict[str, float]:
    from amplifier import GainModule, AmplifierStage
    gm = GainModule("X", diameter_cm=2.5, length_cm=13.0,
                    stored_energy_J=params["stored_energy_J"])
    stage = AmplifierStage("X", [gm], passes=int(params.get("passes", 1)),
                           beam_radius_cm=params["beam_radius_cm"],
                           beam_order_n=4, circular_pol=True)
    _, res = stage.run(params.get("e_in_J", 0.72))
    return {"e_out_mJ": res.e_out_mJ, "B": res.b_integral,
            "peak_fluence": res.peak_fluence}


def eval_oscillator(params: Dict[str, float]) -> Dict[str, float]:
    from laser_platform import Cavity, FourLevelLaser
    cav = Cavity(R2=params["R2"], Rp=params["pump_ratio"] * 1.0)
    # set pump relative to threshold of THIS cavity
    cav2 = Cavity(R2=params["R2"])
    cav2_rp = params["pump_ratio"] * cav2.Rp_threshold
    cav_final = Cavity(R2=params["R2"], Rp=cav2_rp)
    _, S_ss = FourLevelLaser(cav_final).steady_state()
    return {"P_out_W": cav_final.output_power(S_ss),
            "r": cav_final.r}


# ==============================================================================
# DRIVER
# ==============================================================================
def sweep_amplifier(csv_path=None):
    print(f"[backend: {_BACKEND}]  vectorized amplifier sweep")
    f_store = np.linspace(0.05, 0.30, 60)      # J/cm^2
    beam_r = np.linspace(0.4, 1.2, 60)         # cm
    E, B = vectorized_amplifier_sweep(f_store, beam_r)
    E = np.asarray(getattr(E, "get", lambda: E)()) if _BACKEND.startswith("cupy") else np.asarray(E)
    B = np.asarray(getattr(B, "get", lambda: B)()) if _BACKEND.startswith("cupy") else np.asarray(B)

    # objective: max energy subject to B < 3 (safe from self-focusing)
    safe = B < 3.0
    masked = np.where(safe, E, -np.inf)
    idx = np.unravel_index(np.argmax(masked), masked.shape)
    print(f"  grid: {E.size} configs ({E.shape[0]}x{E.shape[1]})")
    print(f"  best safe config: E_out = {E[idx]*1e3:.0f} mJ, B = {B[idx]:.2f}")
    print(f"    beam_radius = {beam_r[idx[0]]:.2f} cm, f_store = {f_store[idx[1]]:.3f} J/cm^2")

    if csv_path:
        with open(csv_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["f_store_Jcm2", "beam_radius_cm", "E_out_mJ", "B"])
            for i in range(E.shape[0]):
                for j in range(E.shape[1]):
                    w.writerow([f"{f_store[j]:.4f}", f"{beam_r[i]:.4f}",
                                f"{E[i, j]*1e3:.2f}", f"{B[i, j]:.4f}"])
        print(f"  wrote {csv_path}")


def sweep_oscillator(csv_path=None):
    print("  generic parallel oscillator sweep")
    specs = [
        SweepSpec("R2", np.linspace(0.80, 0.99, 12)),
        SweepSpec("pump_ratio", np.linspace(1.1, 8.0, 12)),
    ]
    pts = grid(specs)
    rows = run_grid(eval_oscillator, pts, workers=os.cpu_count())
    top = best(rows, objective="P_out_W", maximize=True)
    print(f"  swept {len(rows)} configs")
    print(f"  best: P_out = {top['P_out_W']:.3f} W at R2={top['R2']:.3f}, "
          f"pump_ratio={top['pump_ratio']:.2f} (r={top['r']:.2f})")
    if csv_path:
        with open(csv_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"  wrote {csv_path}")


def main():
    ap = argparse.ArgumentParser(description="LASERSIM batch sweep engine")
    ap.add_argument("target", choices=["amplifier", "oscillator"])
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()
    print("=" * 60)
    print(" LASERSIM sweep engine")
    print("=" * 60)
    if args.target == "amplifier":
        sweep_amplifier(args.csv)
    else:
        sweep_oscillator(args.csv)
    print("=" * 60)


if __name__ == "__main__":
    main()
