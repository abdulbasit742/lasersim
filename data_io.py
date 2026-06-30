#!/usr/bin/env python3
"""
================================================================================
data_io.py  -  import real lab data and fit it to the LASERSIM models
================================================================================
A platform is only real when it can ingest MEASURED data and compare it to the
model. This module:

  1. Loads a measured beam-profile image (PNG/JPG/CSV/NPY) like the camera shots
     in the paper's Fig. 3/4 insets.
  2. Fits it to an n-th order super-Gaussian to extract beam radius, order,
     ellipticity, and a flatness/quality metric.
  3. Loads measured energy-vs-input (or energy-vs-current) tables (CSV) and
     compares them against the Frantz-Nodvik amplifier model, reporting the
     percentage agreement (the paper got 92/90/99% per stage).

No hard dependency on a specific camera format; images go through PIL if
available, else expect a 2D numpy array (.npy) or CSV.

Run:
    python data_io.py --image beam.png
    python data_io.py --energy-csv stage.csv      # cols: input_mJ,measured_mJ
    python data_io.py --demo                       # synthetic round-trip demo
================================================================================
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.optimize import curve_fit

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


# ==============================================================================
# IMAGE LOADING
# ==============================================================================
def load_image(path: str) -> np.ndarray:
    """Load a beam profile as a 2D float array, normalized to peak=1."""
    if path.endswith(".npy"):
        img = np.load(path).astype(float)
    elif path.endswith(".csv"):
        img = np.loadtxt(path, delimiter=",").astype(float)
    else:
        try:
            from PIL import Image
        except Exception:
            raise SystemExit("Install Pillow to load image files: pip install pillow")
        img = np.asarray(Image.open(path).convert("L"), dtype=float)
    img -= img.min()
    peak = img.max()
    return img / peak if peak > 0 else img


# ==============================================================================
# SUPER-GAUSSIAN FIT
# ==============================================================================
def super_gaussian_2d(coords, x0, y0, wx, wy, order, amp, offset):
    x, y = coords
    r = ((x - x0) / wx) ** 2 + ((y - y0) / wy) ** 2
    return (amp * np.exp(-2.0 * r ** (order / 2.0)) + offset).ravel()


@dataclass
class BeamFit:
    x0: float
    y0: float
    wx: float
    wy: float
    order: float
    ellipticity: float
    flatness: float


def fit_beam(img: np.ndarray) -> BeamFit:
    ny, nx = img.shape
    x = np.arange(nx); y = np.arange(ny)
    X, Y = np.meshgrid(x, y)
    # initial guesses from image moments
    tot = img.sum() + 1e-12
    x0 = (X * img).sum() / tot
    y0 = (Y * img).sum() / tot
    wx0 = np.sqrt(((X - x0) ** 2 * img).sum() / tot)
    wy0 = np.sqrt(((Y - y0) ** 2 * img).sum() / tot)
    p0 = [x0, y0, max(wx0, 1.0), max(wy0, 1.0), 2.0, 1.0, 0.0]
    try:
        popt, _ = curve_fit(super_gaussian_2d, (X, Y), img.ravel(), p0=p0,
                            maxfev=8000)
        x0, y0, wx, wy, order, amp, offset = popt
        wx, wy = abs(wx), abs(wy)
        order = abs(order)
    except Exception:
        wx, wy, order = wx0, wy0, 2.0
    ellip = min(wx, wy) / max(wx, wy)
    mask = img > 0.05
    flat = float(img[mask].mean() / img.max()) if mask.any() else 0.0
    return BeamFit(x0, y0, wx, wy, order, ellip, flat)


# ==============================================================================
# ENERGY DATA vs MODEL
# ==============================================================================
def load_energy_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """CSV with header 'input_mJ,measured_mJ'. Returns (input, measured) [mJ]."""
    ins, outs = [], []
    with open(path) as fh:
        rdr = csv.DictReader(fh)
        for row in rdr:
            ins.append(float(row["input_mJ"]))
            outs.append(float(row["measured_mJ"]))
    return np.array(ins), np.array(outs)


def compare_to_model(input_mJ, measured_mJ, stored_energy_J, rod_diameter_cm,
                     rod_length_cm=13.0, beam_radius_cm=0.8, passes=1):
    """Run the amplifier model on the same inputs and report agreement %."""
    from amplifier import GainModule, AmplifierStage
    gm = GainModule("fit", rod_diameter_cm, rod_length_cm, stored_energy_J)
    modeled = []
    for e_in in input_mJ:
        stage = AmplifierStage("fit", [gm], passes=passes,
                               beam_radius_cm=beam_radius_cm, beam_order_n=4)
        _, r = stage.run(e_in / 1e3)
        modeled.append(r.e_out_mJ)
    modeled = np.array(modeled)
    agree = 100.0 * (1.0 - np.abs(modeled - measured_mJ) / measured_mJ)
    return modeled, agree


# ==============================================================================
# DEMO
# ==============================================================================
def make_synthetic_beam(nx=256, order=4, wx=60, wy=70, noise=0.04):
    x = np.arange(nx); X, Y = np.meshgrid(x, x)
    r = ((X - nx/2) / wx) ** 2 + ((Y - nx/2) / wy) ** 2
    img = np.exp(-2.0 * r ** (order / 2.0))
    img += noise * np.random.default_rng(0).standard_normal(img.shape)
    return np.clip(img, 0, None) / img.max()


def main():
    ap = argparse.ArgumentParser(description="Import + fit real laser data")
    ap.add_argument("--image")
    ap.add_argument("--energy-csv")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    if args.image or args.demo:
        img = make_synthetic_beam() if args.demo else load_image(args.image)
        fit = fit_beam(img)
        print("=" * 56)
        print(" Beam-profile fit (super-Gaussian)")
        print("=" * 56)
        print(f"  beam radii  : wx={fit.wx:.1f}, wy={fit.wy:.1f} px")
        print(f"  order n     : {fit.order:.2f}  ({'Gaussian' if fit.order < 3 else 'super-Gaussian'})")
        print(f"  ellipticity : {fit.ellipticity:.3f}  (1.0 = round)")
        print(f"  flatness    : {fit.flatness:.3f}")
        print("=" * 56)
        if _HAVE_MPL:
            plt.imshow(img, cmap="turbo"); plt.title(f"beam, n={fit.order:.1f}")
            plt.colorbar(); plt.savefig("beam_fit.png", dpi=130)
            print("Saved -> beam_fit.png")

    if args.energy_csv:
        ins, meas = load_energy_csv(args.energy_csv)
        modeled, agree = compare_to_model(ins, meas, stored_energy_J=1.14,
                                          rod_diameter_cm=2.5)
        print("=" * 56)
        print(" Energy data vs Frantz-Nodvik model")
        print("=" * 56)
        for i, m, mod, a in zip(ins, meas, modeled, agree):
            print(f"  in {i:6.0f} mJ | meas {m:6.0f} | model {mod:6.0f} | {a:5.1f}% agree")
        print(f"  mean agreement: {agree.mean():.1f}%")
        print("=" * 56)

    if not (args.image or args.energy_csv or args.demo):
        ap.print_help()


if __name__ == "__main__":
    main()
