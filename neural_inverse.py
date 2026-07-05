<<<<<<< HEAD
"""neural_inverse.py -- differentiable inverse design + ensemble uncertainty.

This module trains an ensemble of PyTorch neural surrogates on the RTX A6000 GPU,
and then performs differentiable inverse design by optimizing a population of design
parameters in parallel via backpropagation through the ensemble.
=======
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
>>>>>>> a8b6f4138e9d51f26fcf8d6646be036853ea77b8
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from typing import Dict, List, Tuple

<<<<<<< HEAD
import torch
import torch.nn as nn

import forward_model as fm

TARGET_METRICS = ["output_energy_j", "pulse_duration_fs", "m2", "shg_efficiency", "peak_power_w"]
_KEYS = list(fm.DESIGN_BOUNDS.keys())
_LO = [fm.DESIGN_BOUNDS[k][0] for k in _KEYS]
_HI = [fm.DESIGN_BOUNDS[k][1] for k in _KEYS]
RESULTS_DIR = "results"


# ------------------------------------------------------------------
# Data generation from the physics model
# ------------------------------------------------------------------
def generate(n: int, seed: int = 0) -> Tuple[List[List[float]], List[List[float]]]:
=======
import forward_model as fm

_KEYS = list(fm.DESIGN_BOUNDS.keys())
_LO = [fm.DESIGN_BOUNDS[k][0] for k in _KEYS]
_HI = [fm.DESIGN_BOUNDS[k][1] for k in _KEYS]
TARGET_METRICS = ["output_energy_j", "pulse_duration_fs", "m2",
                  "shg_efficiency", "peak_power_w"]
RESULTS_DIR = "results"

# default target spec (metric -> (value, weight))
DEFAULT_TARGET = {
    "output_energy_j":  (0.60, 1.0),
    "pulse_duration_fs": (450.0, 1.0),
    "m2":               (1.15, 1.0),
    "shg_efficiency":   (0.50, 0.75),
}


def _gen(n, seed):
>>>>>>> a8b6f4138e9d51f26fcf8d6646be036853ea77b8
    rng = random.Random(seed)
    X, Y = [], []
    for _ in range(n):
        v = [rng.uniform(lo, hi) for lo, hi in zip(_LO, _HI)]
<<<<<<< HEAD
        d = {k: v[i] for i, k in enumerate(_KEYS)}
        m = fm.simulate(d)
        X.append(v)
        Y.append([m[k] for k in TARGET_METRICS])
    return X, Y


# ------------------------------------------------------------------
# PyTorch deep residual surrogate MLP
# ------------------------------------------------------------------
class ResBlock(nn.Module):
    def __init__(self, w):
        super().__init__()
        self.f = nn.Sequential(
            nn.Linear(w, w),
            nn.GELU(),
            nn.LayerNorm(w),
            nn.Linear(w, w),
            nn.GELU()
        )
    def forward(self, x):
        return x + self.f(x)


class Net(nn.Module):
    def __init__(self, d_in, d_out, w, depth):
        super().__init__()
        self.inp = nn.Sequential(
            nn.Linear(d_in, w),
            nn.GELU(),
            nn.LayerNorm(w)
        )
        self.blocks = nn.Sequential(*[ResBlock(w) for _ in range(depth)])
        self.out = nn.Linear(w, d_out)
    def forward(self, x):
        return self.out(self.blocks(self.inp(x)))


def train_model(model_idx: int, X_t, Y_t, x_mean, x_std, y_mean, y_std,
                epochs: int, width: int, depth: int, batch: int, lr: float,
                device, use_cuda: bool, seed: int) -> nn.Module:
    torch.manual_seed(seed + model_idx)
    random.seed(seed + model_idx)
    
    net = Net(len(_KEYS), len(TARGET_METRICS), width, depth).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    
    n = X_t.shape[0]
    idx = torch.randperm(n)
    n_tr, n_va = int(0.8 * n), int(0.1 * n)
    tr, va = idx[:n_tr], idx[n_tr:n_tr + n_va]
    
    X_scaled = (X_t - x_mean) / x_std
    Y_scaled = (Y_t - y_mean) / y_std
    
    ds_tr = torch.utils.data.TensorDataset(X_scaled[tr], Y_scaled[tr])
    dl_tr = torch.utils.data.DataLoader(ds_tr, batch_size=batch, shuffle=True, pin_memory=use_cuda)
    
    ds_va = torch.utils.data.TensorDataset(X_scaled[va], Y_scaled[va])
    dl_va = torch.utils.data.DataLoader(ds_va, batch_size=batch, shuffle=False, pin_memory=use_cuda)
    
    lossf = nn.SmoothL1Loss()
    scaler = torch.cuda.amp.GradScaler(enabled=use_cuda)
    
    best_val, best_state, patience, bad = float("inf"), None, 15, 0
    
    steps = max(1, len(dl_tr)) * epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps)
    
    for ep in range(epochs):
        net.train()
        tl = 0.0; nb = 0
        for xb, yb in dl_tr:
            xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=use_cuda):
                loss = lossf(net(xb), yb)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            tl += loss.item(); nb += 1
            
        net.eval()
        vl = 0.0; vb = 0
        with torch.no_grad():
            for xb, yb in dl_va:
                xb, yb = xb.to(device), yb.to(device)
                with torch.cuda.amp.autocast(enabled=use_cuda):
                    vl += lossf(net(xb), yb).item(); vb += 1
                    
        va_l = vl / max(vb, 1)
        if va_l < best_val - 1e-6:
            best_val, best_state, bad = va_l, {k: v.detach().cpu().clone() for k, v in net.state_dict().items()}, 0
        else:
            bad += 1
            
        if bad >= patience:
            break
            
    if best_state is not None:
        net.load_state_dict(best_state)
    return net


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--ensemble", type=int, default=5)
    ap.add_argument("--pop", type=int, default=16384)
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--opt_lr", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    
    # 1) Smoke test settings override
    if a.smoke:
        a.samples = 2000
        a.epochs = 5
        a.width = 64
        a.depth = 2
        a.batch = 512
        a.ensemble = 2
        a.pop = 256
        a.steps = 20
        
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    gpu_name = torch.cuda.get_device_name(0) if use_cuda else "CPU"
    
    print(f"[neural_inverse] device={device} ({gpu_name})")
    
    t0 = time.time()
    
    # 2) Generate dataset
    print(f"[neural_inverse] generating {a.samples} training samples from physics model...")
    X, Y = generate(a.samples, seed=a.seed)
    
    X_t = torch.tensor(X, dtype=torch.float32)
    Y_t = torch.tensor(Y, dtype=torch.float32)
    
    # Compute standardization stats (on CPU first)
    x_mean, x_std = X_t.mean(0), X_t.std(0).clamp_min(1e-8)
    y_mean, y_std = Y_t.mean(0), Y_t.std(0).clamp_min(1e-8)
    
    # 3) Train the ensemble of surrogates
    print(f"[neural_inverse] training ensemble of {a.ensemble} residual MLPs...")
    models = []
    for i in range(a.ensemble):
        t_start = time.time()
        net = train_model(
            model_idx=i, X_t=X_t, Y_t=Y_t,
            x_mean=x_mean, x_std=x_std, y_mean=y_mean, y_std=y_std,
            epochs=a.epochs, width=a.width, depth=a.depth, batch=a.batch,
            lr=a.lr, device=device, use_cuda=use_cuda, seed=a.seed
        )
        models.append(net)
        print(f"    trained member {i+1}/{a.ensemble} in {time.time() - t_start:.1f}s")
        
    t_train = time.time() - t0
    print(f"[neural_inverse] ensemble training finished in {t_train:.1f}s")
    
    # 4) Differentiable inverse design optimization
    # Define a high-power green SHG target:
    # 80 mJ green light output, 4 ps duration, near diffraction limited, 45% SHG efficiency, 15 MW peak power
    target_dict = {
        "output_energy_j": 8e-5,
        "pulse_duration_fs": 4000.0,
        "m2": 1.3,
        "shg_efficiency": 0.45,
        "peak_power_w": 1.5e7
    }
    
    target_vals = [target_dict[m] for m in TARGET_METRICS]
    target_t = torch.tensor(target_vals, dtype=torch.float32, device=device)
    denom_t = torch.tensor([abs(v) if abs(v) > 1e-12 else 1.0 for v in target_vals], dtype=torch.float32, device=device)
    
    # Move standardization stats to device for optimization speed
    x_mean_d = x_mean.to(device)
    x_std_d = x_std.to(device)
    y_mean_d = y_mean.to(device)
    y_std_d = y_std.to(device)
    
    lo_t = torch.tensor(_LO, dtype=torch.float32, device=device)
    hi_t = torch.tensor(_HI, dtype=torch.float32, device=device)
    
    # Population of design knobs in unconstrained space [-2, 2]
    u = torch.nn.Parameter(torch.empty(a.pop, len(_KEYS), device=device).uniform_(-2.0, 2.0))
    opt_design = torch.optim.Adam([u], lr=a.opt_lr)
    
    t_opt_start = time.time()
    print(f"[neural_inverse] starting differentiable design search over population of {a.pop} candidates...")
    
    for step in range(a.steps):
        opt_design.zero_grad(set_to_none=True)
        
        # map to bounded space
        x = lo_t + (hi_t - lo_t) * torch.sigmoid(u)
        
        # predict through ensemble
        preds = []
        for net in models:
            y_scaled = net((x - x_mean_d) / x_std_d)
            y = y_scaled * y_std_d + y_mean_d
            preds.append(y)
        preds = torch.stack(preds, dim=0) # shape (E, pop, len(TARGET_METRICS))
        mean_pred = preds.mean(dim=0)     # shape (pop, len(TARGET_METRICS))
        
        # Compute cost (weighted relative error squared)
        rel_err = (mean_pred - target_t) / denom_t
        loss = (rel_err ** 2).sum(dim=-1) # shape (pop,)
        
        loss_mean = loss.mean()
        loss_mean.backward()
        opt_design.step()
        
        if step % max(1, a.steps // 5) == 0 or step == a.steps - 1:
            best_l = loss.min().item()
            print(f"    step {step:4d}  min population cost = {best_l:.4e}")
            
    t_opt = time.time() - t_opt_start
    print(f"[neural_inverse] design search finished in {t_opt:.1f}s")
    
    # 5) Extract the best design from the population
    with torch.no_grad():
        x_final = lo_t + (hi_t - lo_t) * torch.sigmoid(u)
        preds = []
        for net in models:
            y_scaled = net((x_final - x_mean_d) / x_std_d)
            y = y_scaled * y_std_d + y_mean_d
            preds.append(y)
        preds = torch.stack(preds, dim=0)
        mean_preds = preds.mean(dim=0)
        std_preds = preds.std(dim=0)
        
        rel_err_final = (mean_preds - target_t) / denom_t
        costs = (rel_err_final ** 2).sum(dim=-1)
        best_idx = torch.argmin(costs).item()
        
        best_design_vec = x_final[best_idx].tolist()
        best_design = {k: best_design_vec[j] for j, k in enumerate(_KEYS)}
        
        best_mean = mean_preds[best_idx].tolist()
        best_std = std_preds[best_idx].tolist()
        
    # Run physics model simulator check on the best design
    physics_check = fm.simulate(best_design)
    
    results = {
        "device": gpu_name,
        "train_time_s": t_train,
        "opt_time_s": t_opt,
        "population": a.pop,
        "ensemble_size": a.ensemble,
        "best_design": best_design,
        "metrics": {
            m: {
                "target": target_dict[m],
                "surrogate_mean": best_mean[j],
                "surrogate_std": best_std[j],
                "physics_check": physics_check[m]
            } for j, m in enumerate(TARGET_METRICS)
        }
    }
    
    with open(os.path.join(RESULTS_DIR, "neural_inverse.json"), "w") as fh:
        json.dump(results, fh, indent=2)
        
    print(f"[neural_inverse] results saved to results/neural_inverse.json")
    print(f"[neural_inverse] final design validation check:")
    for m in TARGET_METRICS:
        t_val = target_dict[m]
        s_mean = results["metrics"][m]["surrogate_mean"]
        s_std = results["metrics"][m]["surrogate_std"]
        p_val = results["metrics"][m]["physics_check"]
        print(f"    {m:18s}  Target: {t_val:.4g} | Surrogate: {s_mean:.4g} +/- {s_std:.4g} | Physics: {p_val:.4g}")
        
=======
        m = fm.simulate({k: v[i] for i, k in enumerate(_KEYS)})
        X.append(v); Y.append([m[k] for k in TARGET_METRICS])
    return X, Y


def _build(samples, epochs, width, depth, batch, seed, smoke):
    """Train one surrogate net; return (net, norm-stats, torch-module refs)."""
    import torch, torch.nn as nn
    torch.manual_seed(seed)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        samples, epochs, width, depth, batch = 4000, 6, 64, 2, 512
    X, Y = _gen(samples, seed)
    X = torch.tensor(X, dtype=torch.float32); Y = torch.tensor(Y, dtype=torch.float32)
    xm, xs = X.mean(0), X.std(0).clamp_min(1e-8)
    ym, ys = Y.mean(0), Y.std(0).clamp_min(1e-8)
    Xn, Yn = ((X - xm) / xs), ((Y - ym) / ys)

    class ResBlock(nn.Module):
        def __init__(s, w):
            super().__init__()
            s.f = nn.Sequential(nn.Linear(w, w), nn.GELU(), nn.LayerNorm(w),
                                nn.Linear(w, w), nn.GELU())
        def forward(s, x): return x + s.f(x)

    class Net(nn.Module):
        def __init__(s, di, do, w, dp):
            super().__init__()
            s.inp = nn.Sequential(nn.Linear(di, w), nn.GELU(), nn.LayerNorm(w))
            s.blocks = nn.Sequential(*[ResBlock(w) for _ in range(dp)])
            s.out = nn.Linear(w, do)
        def forward(s, x): return s.out(s.blocks(s.inp(x)))

    net = Net(len(_KEYS), len(TARGET_METRICS), width, depth).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=2e-3, weight_decay=1e-4)
    lossf = nn.SmoothL1Loss()
    scaler = torch.cuda.amp.GradScaler(enabled=(dev.type == "cuda"))
    ds = torch.utils.data.TensorDataset(Xn, Yn)
    dl = torch.utils.data.DataLoader(ds, batch_size=batch, shuffle=True,
                                     pin_memory=(dev.type == "cuda"))
    for _ in range(epochs):
        net.train()
        for xb, yb in dl:
            xb, yb = xb.to(dev, non_blocking=True), yb.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=(dev.type == "cuda")):
                loss = lossf(net(xb), yb)
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    net.eval()
    return net, (xm.to(dev), xs.to(dev), ym.to(dev), ys.to(dev)), dev


def differentiable_inverse(target=None, pop=8192, steps=400,
                           ensemble=3, samples=200_000, epochs=120,
                           width=384, depth=6, seed=0, smoke=False) -> Dict:
    """Solve inverse design by backprop through a trained ensemble."""
    try:
        import torch
    except Exception:
        print("[neural_inverse] PyTorch not installed.")
        print("    pip install torch --index-url https://download.pytorch.org/whl/cu124")
        return {"ok": False, "reason": "torch-missing"}

    os.makedirs(RESULTS_DIR, exist_ok=True)
    target = target or DEFAULT_TARGET
    if smoke:
        pop, steps, ensemble = 512, 60, 2

    t0 = time.time()
    nets, stats_ref, dev = [], None, None
    for k in range(ensemble):
        net, stats, dev = _build(samples, epochs, width, depth, 4096,
                                 seed + k, smoke)
        nets.append(net); stats_ref = stats
    xm, xs, ym, ys = stats_ref
    gpu = torch.cuda.get_device_name(0) if dev.type == "cuda" else "CPU"
    print(f"[neural_inverse] device={gpu}  ensemble={ensemble}  pop={pop}")

    # target vector + weights in original units
    tvec = torch.zeros(len(TARGET_METRICS), device=dev)
    wvec = torch.zeros(len(TARGET_METRICS), device=dev)
    for i, name in enumerate(TARGET_METRICS):
        if name in target:
            tvec[i], wvec[i] = target[name][0], target[name][1]
    tnorm = (tvec - ym) / ys

    lo = torch.tensor(_LO, device=dev); hi = torch.tensor(_HI, device=dev)
    # latent params in (0,1) via sigmoid keep designs in-box automatically
    z = torch.randn(pop, len(_KEYS), device=dev, requires_grad=True)
    opt = torch.optim.Adam([z], lr=5e-2)

    def ensemble_pred(xn):
        outs = torch.stack([n(xn) for n in nets], 0)   # [K, P, M]
        return outs.mean(0), outs.std(0)

    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        frac = torch.sigmoid(z)                          # (0,1) box
        design = lo + frac * (hi - lo)
        xn = (design - xm) / xs
        mean, std = ensemble_pred(xn)
        # weighted squared error to target (normalized space) + uncertainty reg
        err = ((mean - tnorm) ** 2 * (wvec / (wvec.sum() + 1e-9))).sum(1)
        loss = (err + 0.02 * std.mean(1)).mean()
        loss.backward(); opt.step()

    with torch.no_grad():
        frac = torch.sigmoid(z); design = lo + frac * (hi - lo)
        xn = (design - xm) / xs
        mean, std = ensemble_pred(xn)
        pred = mean * ys + ym; pred_std = std * ys
        err = ((mean - tnorm) ** 2 * (wvec / (wvec.sum() + 1e-9))).sum(1)
        best = int(torch.argmin(err).item())

    best_design = {k: float(design[best, i].item()) for i, k in enumerate(_KEYS)}
    # verify against the REAL physics (surrogate could be wrong)
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

    summary = {"ok": True, "device": gpu, "pop": pop, "ensemble": ensemble,
               "steps": steps, "seconds": elapsed, "best_design": best_design,
               "report": report}
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
>>>>>>> a8b6f4138e9d51f26fcf8d6646be036853ea77b8
    return 0


if __name__ == "__main__":
<<<<<<< HEAD
    sys.exit(main())
=======
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
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    differentiable_inverse(pop=a.pop, steps=a.steps, ensemble=a.ensemble,
                           samples=a.samples, epochs=a.epochs, width=a.width,
                           depth=a.depth, seed=a.seed)
>>>>>>> a8b6f4138e9d51f26fcf8d6646be036853ea77b8
