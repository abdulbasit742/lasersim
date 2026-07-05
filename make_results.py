"""make_results.py -- one command, professor-ready results.

Runs the full novelty story end to end and writes everything into results/:

  1. Forward model at a nominal design (baseline numbers).
  2. A pump-power sweep (energy / M^2 / SHG tradeoff) -> sweep_pump.csv + PNG.
  3. A trained ML surrogate with held-out R^2 + a wall-clock speedup figure.
  4. Constraint-aware INVERSE DESIGN for a target spec (the headline result).
  5. results/RESULTS.md tying it together for a reader.

Usage:
    python make_results.py            # reference model, fast
    python make_results.py --full     # route through laser_platform if available
    python make_results.py --smoke    # tiny, CI-friendly run

Zero mandatory deps beyond the stdlib + this repo. matplotlib and scipy /
scikit-learn are used automatically if installed, and skipped cleanly if not.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import forward_model as fm
import inverse_design as idz
import surrogate as sg

RESULTS_DIR = "results"


def _ensure_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def _maybe_plot(xs, series, xlabel, title, fname):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for label, ys in series.items():
        ax.plot(xs, ys, marker="o", ms=3, label=label)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    path = os.path.join(RESULTS_DIR, fname)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def run(full: bool = False, smoke: bool = False) -> dict:
    _ensure_dir()
    sp = fm.SystemParams()
    t0 = time.time()

    # 1) baseline -------------------------------------------------
    baseline_design = fm.default_design()
    baseline = fm.simulate(baseline_design, sp=sp, full=full)

    # 2) pump sweep ----------------------------------------------
    lo, hi = fm.DESIGN_BOUNDS["pump_power_w"]
    n = 12 if smoke else 40
    pumps = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    sweep_rows = []
    for p in pumps:
        d = dict(baseline_design); d["pump_power_w"] = p
        m = fm.simulate(d, sp=sp, full=full)
        sweep_rows.append((p, m["output_energy_j"], m["m2"], m["shg_efficiency"]))
    csv_path = os.path.join(RESULTS_DIR, "sweep_pump.csv")
    with open(csv_path, "w") as fh:
        fh.write("pump_power_w,output_energy_j,m2,shg_efficiency\n")
        for r in sweep_rows:
            fh.write(",".join(f"{x:.6g}" for x in r) + "\n")
    plot_path = _maybe_plot(
        [r[0] for r in sweep_rows],
        {"output energy [J]": [r[1] for r in sweep_rows],
         "M^2": [r[2] for r in sweep_rows],
         "SHG eff": [r[3] for r in sweep_rows]},
        "pump power [W]", "Pump-power tradeoff (energy vs beam quality vs SHG)",
        "sweep_pump.png")

    # 3) surrogate ------------------------------------------------
    n_tr = 200 if smoke else 900
    n_te = 80 if smoke else 300
    model, r2, meta = sg.build_surrogate(n_train=n_tr, n_test=n_te, sp=sp,
                                         full=full, seed=7)
    # speedup: physics call vs surrogate call, wall clock
    probe = fm.default_design()
    vec = [probe[k] for k in fm.DESIGN_BOUNDS]
    reps = 300 if smoke else 3000
    t = time.time()
    for _ in range(reps):
        fm.simulate(probe, sp=sp, full=full)
    phys_t = (time.time() - t) / reps
    t = time.time()
    for _ in range(reps):
        model.predict_one(vec)
    surr_t = (time.time() - t) / reps
    speedup = phys_t / surr_t if surr_t > 0 else float("inf")

    # 4) inverse design (headline) -------------------------------
    target = idz.DEFAULT_TARGET
    inv = idz.design_for(target=target, sp=sp, full=full, seed=11)
    with open(os.path.join(RESULTS_DIR, "inverse_design.json"), "w") as fh:
        json.dump({"design": inv["design"], "metrics": inv["metrics"],
                   "target_report": inv["target_report"], "engine": inv["engine"],
                   "cost": inv["cost"]}, fh, indent=2)

    elapsed = time.time() - t0

    # 5) RESULTS.md ----------------------------------------------
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append("# lasersim -- Results\n")
    lines.append(f"_Generated {ts} | mode={'full-chain' if full else 'reference forward model'}"
                 f"{' | SMOKE' if smoke else ''} | wall clock {elapsed:.2f}s_\n")
    lines.append("## 1. Baseline operating point\n")
    lines.append("| metric | value |\n|---|---|")
    for k, v in baseline.items():
        lines.append(f"| {k} | {v:.6g} |")
    lines.append("")
    lines.append("## 2. Pump-power sweep\n")
    lines.append(f"Data: `sweep_pump.csv` ({len(sweep_rows)} points)."
                 + (f" Figure: `sweep_pump.png`." if plot_path else " (matplotlib not installed; CSV only.)"))
    lines.append("\nShows the core engineering tradeoff: pushing pump power buys "
                 "output energy but degrades beam quality (M^2) via thermal load.\n")
    lines.append("## 3. ML surrogate (novelty #2)\n")
    lines.append(f"Engine: **{meta['engine']}**, trained on {meta['n_train']} "
                 f"samples, tested on {meta['n_test']}.\n")
    lines.append("| metric | held-out R^2 |\n|---|---|")
    for k, v in r2.items():
        lines.append(f"| {k} | {v:.4f} |")
    lines.append("")
    lines.append(f"Wall-clock per evaluation: physics = {phys_t*1e6:.2f} us, "
                 f"surrogate = {surr_t*1e6:.2f} us  ->  **{speedup:.0f}x speedup**.\n")
    lines.append("## 4. Inverse design (novelty #1, headline)\n")
    lines.append(f"Optimizer: **{inv['engine']}**, final cost {inv['cost']:.4g}, "
                 "damage-constrained.\n")
    lines.append("Recovered design:\n")
    lines.append("| knob | value |\n|---|---|")
    for k, v in inv["design"].items():
        lines.append(f"| {k} | {v:.6g} |")
    lines.append("\nTarget vs achieved:\n")
    lines.append("| metric | target | achieved | rel. error |\n|---|---|---|---|")
    tr = inv["target_report"]
    for i, name in enumerate(tr["metric"]):
        lines.append(f"| {name} | {tr['target'][i]:.4g} | {tr['achieved'][i]:.4g} "
                     f"| {tr['rel_error_pct'][i]:+.1f}% |")
    lines.append("")
    lines.append("---\n")
    lines.append("See `NOVELTY.md` for the research framing. Reproduce with "
                 "`python make_results.py` (add `--full` to route the numbers "
                 "through the full engine chain).\n")

    md_path = os.path.join(RESULTS_DIR, "RESULTS.md")
    with open(md_path, "w") as fh:
        fh.write("\n".join(lines))

    print(f"[make_results] wrote {md_path}")
    print(f"[make_results] surrogate speedup ~{speedup:.0f}x, "
          f"inverse-design cost {inv['cost']:.3g}, {elapsed:.2f}s total")
    return {"results_md": md_path, "speedup": speedup, "inv_cost": inv["cost"],
            "r2": r2}


def _smoke() -> int:
    out = run(full=False, smoke=True)
    assert os.path.exists(out["results_md"]), "RESULTS.md not written"
    assert out["inv_cost"] < 5.0, "inverse design did not converge in smoke"
    print("[make_results] smoke OK")
    return 0


if __name__ == "__main__":
    full = "--full" in sys.argv
    if "--smoke" in sys.argv:
        raise SystemExit(_smoke())
    run(full=full, smoke=False)
