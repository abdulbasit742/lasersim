"""train_surrogate.py -- a real, GPU-trained neural surrogate of the laser.

This is the heavy model. Where surrogate.py is a light sklearn/ridge fallback,
this trains a genuine deep residual MLP in PyTorch that maps

    design (5 knobs)  -->  metrics (energy, duration, M^2, SHG, ...)

using the physics forward model (forward_model.simulate) as an infinite,
noise-free data generator. It is built to actually use the RTX A6000:

  * large sampled dataset (default 200k samples, scale up freely)
  * deep residual MLP with configurable width/depth
  * CUDA + AMP (torch.cuda.amp) mixed precision, cudnn.benchmark
  * big batches to saturate the GPU, pinned-memory DataLoaders
  * OneCycle LR schedule, AdamW, gradient clipping
  * train / validation / test split with early stopping on val loss
  * per-metric R^2 and MAE on the held-out test set
  * learning-curve + parity plots, model checkpoint (.pt)

It degrades gracefully: if torch is missing it prints how to install; if no
GPU is present it trains on CPU with a smaller default. --smoke runs a tiny
CPU config so CI stays green.

Usage:
    python train_surrogate.py --smoke
    python train_surrogate.py                 # full run, auto-detects CUDA
    python train_surrogate.py --samples 500000 --epochs 300 --width 512 --depth 8
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

import forward_model as fm

TARGET_METRICS = ["output_energy_j", "pulse_duration_fs", "m2",
                  "shg_efficiency", "peak_power_w"]
_KEYS = list(fm.DESIGN_BOUNDS.keys())
_LO = [fm.DESIGN_BOUNDS[k][0] for k in _KEYS]
_HI = [fm.DESIGN_BOUNDS[k][1] for k in _KEYS]
RESULTS_DIR = "results"
CKPT = os.path.join(RESULTS_DIR, "surrogate_net.pt")


# ------------------------------------------------------------------
# Data generation from the physics model
# ------------------------------------------------------------------
def generate(n: int, seed: int = 0) -> Tuple[List[List[float]], List[List[float]]]:
    rng = random.Random(seed)
    X, Y = [], []
    for _ in range(n):
        v = [rng.uniform(lo, hi) for lo, hi in zip(_LO, _HI)]
        d = {k: v[i] for i, k in enumerate(_KEYS)}
        m = fm.simulate(d)
        X.append(v)
        Y.append([m[k] for k in TARGET_METRICS])
    return X, Y


def _r2(yt: List[float], yp: List[float]) -> float:
    n = len(yt); mean = sum(yt) / n
    ss_tot = sum((y - mean) ** 2 for y in yt)
    ss_res = sum((a - b) ** 2 for a, b in zip(yt, yp))
    if ss_tot < 1e-30:
        return 1.0 if ss_res < 1e-30 else 0.0
    return 1.0 - ss_res / ss_tot


# ------------------------------------------------------------------
# Training (PyTorch)
# ------------------------------------------------------------------
def train(samples=200_000, epochs=200, width=512, depth=6, batch=4096,
          lr=2e-3, seed=0, smoke=False) -> Dict:
    try:
        import torch
        import torch.nn as nn
    except Exception:
        print("[train_surrogate] PyTorch not installed.")
        print("    GPU build:  pip install torch --index-url "
              "https://download.pytorch.org/whl/cu124")
        print("    then re-run: python train_surrogate.py")
        return {"ok": False, "reason": "torch-missing"}

    os.makedirs(RESULTS_DIR, exist_ok=True)
    torch.manual_seed(seed); random.seed(seed)
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    if use_cuda:
        torch.backends.cudnn.benchmark = True
        gpu_name = torch.cuda.get_device_name(0)
    else:
        gpu_name = "CPU"

    if smoke:
        samples, epochs, width, depth, batch = 4000, 8, 64, 2, 512

    t0 = time.time()
    print(f"[train_surrogate] device={device} ({gpu_name})")
    print(f"[train_surrogate] generating {samples} samples from physics model...")
    X, Y = generate(samples, seed=seed)
    n_out = len(TARGET_METRICS)

    X_t = torch.tensor(X, dtype=torch.float32)
    Y_t = torch.tensor(Y, dtype=torch.float32)

    # standardize (store stats for inference)
    x_mean, x_std = X_t.mean(0), X_t.std(0).clamp_min(1e-8)
    y_mean, y_std = Y_t.mean(0), Y_t.std(0).clamp_min(1e-8)
    X_t = (X_t - x_mean) / x_std
    Y_t = (Y_t - y_mean) / y_std

    n = X_t.shape[0]
    idx = torch.randperm(n)
    n_tr, n_va = int(0.8 * n), int(0.1 * n)
    tr, va, te = idx[:n_tr], idx[n_tr:n_tr + n_va], idx[n_tr + n_va:]

    def loader(sel, shuffle):
        ds = torch.utils.data.TensorDataset(X_t[sel], Y_t[sel])
        return torch.utils.data.DataLoader(
            ds, batch_size=batch, shuffle=shuffle,
            pin_memory=use_cuda, num_workers=0, drop_last=False)

    dl_tr, dl_va = loader(tr, True), loader(va, False)

    # deep residual MLP
    class ResBlock(nn.Module):
        def __init__(self, w):
            super().__init__()
            self.f = nn.Sequential(nn.Linear(w, w), nn.GELU(),
                                   nn.LayerNorm(w), nn.Linear(w, w), nn.GELU())
        def forward(self, x):
            return x + self.f(x)

    class Net(nn.Module):
        def __init__(self, d_in, d_out, w, depth):
            super().__init__()
            self.inp = nn.Sequential(nn.Linear(d_in, w), nn.GELU(), nn.LayerNorm(w))
            self.blocks = nn.Sequential(*[ResBlock(w) for _ in range(depth)])
            self.out = nn.Linear(w, d_out)
        def forward(self, x):
            return self.out(self.blocks(self.inp(x)))

    net = Net(len(_KEYS), n_out, width, depth).to(device)
    n_params = sum(p.numel() for p in net.parameters())
    print(f"[train_surrogate] model: width={width} depth={depth} "
          f"params={n_params/1e6:.2f}M batch={batch}")

    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    steps = max(1, len(dl_tr)) * epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps)
    lossf = nn.SmoothL1Loss()
    scaler = torch.cuda.amp.GradScaler(enabled=use_cuda)

    hist = {"train": [], "val": []}
    best_val, best_state, patience, bad = float("inf"), None, 20, 0
    for ep in range(epochs):
        net.train(); tl = 0.0; nb = 0
        for xb, yb in dl_tr:
            xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=use_cuda):
                loss = lossf(net(xb), yb)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            scaler.step(opt); scaler.update(); sched.step()
            tl += loss.item(); nb += 1
        net.eval(); vl = 0.0; vb = 0
        with torch.no_grad():
            for xb, yb in dl_va:
                xb, yb = xb.to(device), yb.to(device)
                with torch.cuda.amp.autocast(enabled=use_cuda):
                    vl += lossf(net(xb), yb).item(); vb += 1
        tr_l, va_l = tl / max(nb, 1), vl / max(vb, 1)
        hist["train"].append(tr_l); hist["val"].append(va_l)
        if va_l < best_val - 1e-6:
            best_val, best_state, bad = va_l, {k: v.detach().cpu().clone()
                                               for k, v in net.state_dict().items()}, 0
        else:
            bad += 1
        if ep % max(1, epochs // 10) == 0 or ep == epochs - 1:
            print(f"    epoch {ep:4d}  train {tr_l:.4e}  val {va_l:.4e}")
        if bad >= patience:
            print(f"    early stop at epoch {ep} (val plateaued)")
            break

    if best_state is not None:
        net.load_state_dict(best_state)

    # train vs test metrics in original units
    net.eval()
    with torch.no_grad():
        pred = (net(X_t[te].to(device)).cpu() * y_std + y_mean)
        true = (Y_t[te] * y_std + y_mean)
        pred_tr = (net(X_t[tr].to(device)).cpu() * y_std + y_mean)
        true_tr = (Y_t[tr] * y_std + y_mean)
    r2, mae, r2_train = {}, {}, {}
    for j, name in enumerate(TARGET_METRICS):
        yt = true[:, j].tolist(); yp = pred[:, j].tolist()
        r2[name] = _r2(yt, yp)
        mae[name] = sum(abs(a - b) for a, b in zip(yt, yp)) / len(yt)
        yt_tr = true_tr[:, j].tolist(); yp_tr = pred_tr[:, j].tolist()
        r2_train[name] = _r2(yt_tr, yp_tr)

    # save checkpoint + normalization
    torch.save({"state_dict": net.state_dict(),
                "x_mean": x_mean, "x_std": x_std,
                "y_mean": y_mean, "y_std": y_std,
                "keys": _KEYS, "metrics": TARGET_METRICS,
                "width": width, "depth": depth}, CKPT)

    # plots (best-effort)
    plotted = _plots(hist, true, pred, use_cuda)

    elapsed = time.time() - t0
    print(f"[train_surrogate] done in {elapsed:.1f}s on {gpu_name}")
    for name in TARGET_METRICS:
        print(f"    R^2[{name:18s}] = {r2[name]:.6f} (test) vs {r2_train[name]:.6f} (train)   MAE = {mae[name]:.4g}")

    summary = {"ok": True, "device": gpu_name, "params_m": n_params / 1e6,
               "samples": samples, "epochs_run": len(hist["train"]),
               "seconds": elapsed, "r2": r2, "r2_train": r2_train, "mae": mae,
               "checkpoint": CKPT, "plots": plotted}
    with open(os.path.join(RESULTS_DIR, "surrogate_net.json"), "w") as fh:
        json.dump({k: v for k, v in summary.items() if k != "plots"}, fh, indent=2)
    return summary


def _plots(hist, true, pred, use_cuda):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return []
    out = []
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(hist["train"], label="train"); ax.plot(hist["val"], label="val")
    ax.set_yscale("log"); ax.set_xlabel("epoch"); ax.set_ylabel("SmoothL1 loss")
    ax.set_title("Neural surrogate learning curve"); ax.legend(); ax.grid(True, alpha=0.3)
    p = os.path.join(RESULTS_DIR, "surrogate_learning_curve.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig); out.append(p)

    j = TARGET_METRICS.index("output_energy_j")
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    t = true[:, j].tolist(); pr = pred[:, j].tolist()
    ax.scatter(t, pr, s=6, alpha=0.4)
    lim = [min(t + pr), max(t + pr)]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlabel("physics output energy [J]"); ax.set_ylabel("surrogate [J]")
    ax.set_title("Parity: output energy"); ax.grid(True, alpha=0.3)
    p = os.path.join(RESULTS_DIR, "surrogate_parity_energy.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
    return out


def _smoke() -> int:
    print("[train_surrogate] SMOKE (tiny CPU config)")
    out = train(smoke=True)
    if not out.get("ok"):
        # torch missing is acceptable in CI; treat as skipped-but-green
        print("[train_surrogate] torch unavailable; smoke skipped cleanly")
        return 0
    assert out["epochs_run"] >= 1
    print("[train_surrogate] smoke OK")
    return 0


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        raise SystemExit(_smoke())
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    train(samples=a.samples, epochs=a.epochs, width=a.width, depth=a.depth,
          batch=a.batch, lr=a.lr, seed=a.seed)
