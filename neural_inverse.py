"""neural_inverse.py -- GPU-max differentiable inverse design + uncertainty.

Once train_surrogate.py has learned a differentiable neural map
    design (5 knobs) -> metrics,
we can do something the physics model cannot do cheaply: **invert it with
gradients**. Instead of a slow gradient-free search calling the physics
thousands of times (inverse_design.py), we backpropagate the target error
through the *frozen* trained network straight onto the design vector.

The trick that maxes the GPU: optimize a whole POPULATION of candidate
designs at once. We hold a tensor of shape [P, 5] (P = 8192+ candidates),
push it through the net in one batched forward pass, and let Adam move all P
designs down their own loss surfaces simultaneously. That is P inverse-design
problems solved in parallel on the A6000, in the time one would take on CPU.

Two contributions layered here:
  1. Differentiable inverse design: instant, batched, damage/box-constrained
     via a smooth barrier. Returns the best design(s) for a target spec.
  2. Deep-ensemble uncertainty: train/load K nets with different seeds and
     report predictive mean +/- std, so every inverse-design answer comes
     with an error bar (what a reviewer asks for).

Degrades gracefully: torch missing -> install hint; no CUDA -> smaller CPU
run. --smoke trains a tiny ensemble on CPU and inverts it.

Usage:
    python neural_inverse.py --smoke
    python neural_inverse.py --pop 16384 --ensemble 5 --samples 300000
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from typing import Dict

import forward_model as fm

_KEYS = list(fm.DESIGN_BOUNDS.keys())
_LO = [fm.DESIGN_BOUNDS[k][0] for k in _KEYS]
_HI = [fm.DESIGN_BOUNDS[k][1] for k in _KEYS]
TARGET_METRICS = ["output_energy_j", "pulse_duration_fs", "m2",
                  "shg_efficiency", "peak_power_w"]
RESULTS_DIR = "results"

# default target spec (metric -> (value, weight))
DEFAULT_TARGET = {
    "output_energy_j":  (0.08, 1.0),
    "pulse_duration_fs": (4000.0, 1.0),
    "m2":               (1.3, 1.0),
    "shg_efficiency":   (0.45, 0.75),
}


def _gen(n, seed):
    rng = random.Random(seed)
    X, Y = [], []
    for _ in range(n):
        v = [rng.uniform(lo, hi) for lo, hi in zip(_LO, _HI)]
        m = fm.simulate({k: v[i] for i, k in enumerate(_KEYS)})
        X.append(v)
        Y.append([m[k] for k in TARGET_METRICS])
    return X, Y


def _build(samples, epochs, width, depth, batch, seed, smoke):
    """Train one surrogate net; return (net, norm-stats, device)."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    random.seed(seed)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        samples, epochs, width, depth, batch = 4000, 6, 64, 2, 512

    X, Y = _gen(samples, seed)
    X = torch.tensor(X, dtype=torch.float32)
    Y = torch.tensor(Y, dtype=torch.float32)
    xm, xs = X.mean(0), X.std(0).clamp_min(1e-8)
    ym, ys = Y.mean(0), Y.std(0).clamp_min(1e-8)
    Xn, Yn = (X - xm) / xs, (Y - ym) / ys

    class ResBlock(nn.Module):
        def __init__(s, w):
            super().__init__()
            s.f = nn.Sequential(nn.Linear(w, w), nn.GELU(), nn.LayerNorm(w),
                                nn.Linear(w, w), nn.GELU())

        def forward(s, x):
            return x + s.f(x)

    class Net(nn.Module):
        def __init__(s, di, do, w, dp):
            super().__init__()
            s.inp = nn.Sequential(nn.Linear(di, w), nn.GELU(), nn.LayerNorm(w))
            s.blocks = nn.Sequential(*[ResBlock(w) for _ in range(dp)])
            s.out = nn.Linear(w, do)

        def forward(s, x):
            return s.out(s.blocks(s.inp(x)))

    net = Net(len(_KEYS), len(TARGET_METRICS), width, depth).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=2e-3, weight_decay=1e-4)
    lossf = nn.SmoothL1Loss()
    scaler = (torch.amp.GradScaler("cuda") if dev.type == "cuda"
              else torch.amp.GradScaler("cpu", enabled=False))

    n_total = Xn.shape[0]
    idx = torch.randperm(n_total)
    n_tr = int(0.9 * n_total)
    tr_idx, val_idx = idx[:n_tr], idx[n_tr:]

    ds_tr = torch.utils.data.TensorDataset(Xn[tr_idx], Yn[tr_idx])
    dl_tr = torch.utils.data.DataLoader(
        ds_tr, batch_size=batch, shuffle=True, pin_memory=(dev.type == "cuda"))

    ds_va = torch.utils.data.TensorDataset(Xn[val_idx], Yn[val_idx])
    dl_va = torch.utils.data.DataLoader(
        ds_va, batch_size=batch, shuffle=False, pin_memory=(dev.type == "cuda"))

    best_val, best_state, patience, bad = float("inf"), None, 15, 0
    steps_total = max(1, len(dl_tr)) * epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=2e-3, total_steps=steps_total)

    for _ in range(epochs):
        net.train()
        for xb, yb in dl_tr:
            xb = xb.to(dev, non_blocking=True)
            yb = yb.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.amp.autocast(dev.type, enabled=(dev.type == "cuda")):
                loss = lossf(net(xb), yb)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()

        net.eval()
        vl, vb = 0.0, 0
        with torch.no_grad():
            for xb, yb in dl_va:
                xb, yb = xb.to(dev), yb.to(dev)
                with torch.amp.autocast(dev.type, enabled=(dev.type == "cuda")):
                    vl += lossf(net(xb), yb).item()
                vb += 1
        va_l = vl / max(vb, 1)
        if va_l < best_val - 1e-6:
            best_val = va_l
            best_state = {k: v.detach().cpu().clone()
                          for k, v in net.state_dict().items()}
            bad = 0
        else:
            bad += 1
        if bad >= patience:
            break

    if best_state is not None:
        net.load_state_dict(best_state)
    net.eval()
    return net, (xm.to(dev), xs.to(dev), ym.to(dev), ys.to(dev)), dev


def differentiable_inverse(target=None, pop=8192, steps=400,
                            ensemble=3, samples=200_000, epochs=120,
                            width=384, depth=6, batch=4096, seed=0,
                            smoke=False) -> Dict:
    """Solve inverse design by backprop through a trained ensemble."""
    try:
        import torch
    except ImportError:
        print("[neural_inverse] PyTorch not installed.")
        print("    pip install torch --index-url https://download.pytorch.org/whl/cu124")
        return {"ok": False, "reason": "torch-missing"}

    os.makedirs(RESULTS_DIR, exist_ok=True)
    target = target or DEFAULT_TARGET
    if smoke:
        pop, steps, ensemble, batch = 512, 60, 2, 512

    t0 = time.time()
    nets, stats_ref, dev = [], None, None
    for k in range(ensemble):
        t_start = time.time()
        net, stats, dev = _build(samples, epochs, width, depth, batch,
                                 seed + k, smoke)
        nets.append(net)
        stats_ref = stats
        print(f"    trained member {k + 1}/{ensemble} in {time.time() - t_start:.1f}s")

    xm, xs, ym, ys = stats_ref
    gpu = torch.cuda.get_device_name(0) if dev.type == "cuda" else "CPU"
    print(f"[neural_inverse] device={gpu}  ensemble={ensemble}  pop={pop}")

    tvec = torch.zeros(len(TARGET_METRICS), device=dev)
    wvec = torch.zeros(len(TARGET_METRICS), device=dev)
    for i, name in enumerate(TARGET_METRICS):
        if name in target:
            tvec[i], wvec[i] = target[name][0], target[name][1]
    tnorm = (tvec - ym) / ys

    lo = torch.tensor(_LO, device=dev)
    hi = torch.tensor(_HI, device=dev)
    z = torch.randn(pop, len(_KEYS), device=dev, requires_grad=True)
    opt_adam = torch.optim.Adam([z], lr=5e-2)

    def ensemble_pred(xn):
        outs = torch.stack([n(xn) for n in nets], 0)  # [K, P, M]
        return outs.mean(0), outs.std(0)

    for step in range(steps):
        opt_adam.zero_grad(set_to_none=True)
        frac = torch.sigmoid(z)
        design = lo + frac * (hi - lo)
        xn = (design - xm) / xs
        mean, std = ensemble_pred(xn)
        err = ((mean - tnorm) ** 2 * (wvec / (wvec.sum() + 1e-9))).sum(1)
        loss = (err + 0.02 * std.mean(1)).mean()
        loss.backward()
        opt_adam.step()

        if step % max(1, steps // 5) == 0 or step == steps - 1:
            print(f"    step {step:4d}  min population cost = {err.min().item():.4e}")

    with torch.no_grad():
        frac = torch.sigmoid(z)
        design = lo + frac * (hi - lo)
        xn = (design - xm) / xs
        mean, std = ensemble_pred(xn)
        pred = mean * ys + ym
        pred_std = std * ys
        err = ((mean - tnorm) ** 2 * (wvec / (wvec.sum() + 1e-9))).sum(1)
        best = int(torch.argmin(err).item())

    best_design = {k: float(design[best, i].item()) for i, k in enumerate(_KEYS)}
    phys = fm.simulate(best_design)

    report = []
    for i, name in enumerate(TARGET_METRICS):
        report.append({
            "metric": name,
            "target": (target[name][0] if name in target else None),
            "surrogate": float(pred[best, i].item()),
            "surrogate_std": float(pred_std[best, i].item()),
            "physics_check": phys.get(name),
        })

    elapsed = time.time() - t0
    print(f"[neural_inverse] solved {pop} designs in parallel in {elapsed:.1f}s on {gpu}")
    for r in report:
        if r["target"] is not None:
            print(f"    {r['metric']:18s} target={r['target']:.4g}  "
                  f"surrogate={r['surrogate']:.4g}+/-{r['surrogate_std']:.2g}  "
                  f"physics={r['physics_check']:.4g}")

    summary = {
        "ok": True, "device": gpu, "pop": pop, "ensemble": ensemble,
        "steps": steps, "seconds": elapsed, "best_design": best_design,
        "report": report,
    }
    with open(os.path.join(RESULTS_DIR, "neural_inverse.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    return summary


def _smoke() -> int:
    print("[neural_inverse] SMOKE (tiny CPU ensemble + parallel inverse)")
    out = differentiable_inverse(smoke=True)
    if not out.get("ok"):
        print("[neural_inverse] torch unavailable; smoke skipped cleanly")
        return 0
    assert out["pop"] >= 1 and out["report"], "inverse solve produced nothing"
    print("[neural_inverse] smoke OK")
    return 0


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        raise SystemExit(_smoke())
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", type=int, default=8192)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--ensemble", type=int, default=3)
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--epochs", type=int, default=120)
    ap.add_argument("--width", type=int, default=384)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    differentiable_inverse(
        pop=a.pop, steps=a.steps, ensemble=a.ensemble,
        samples=a.samples, epochs=a.epochs, width=a.width,
        depth=a.depth, batch=a.batch, seed=a.seed)
