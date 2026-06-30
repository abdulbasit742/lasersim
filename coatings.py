#!/usr/bin/env python3
"""
================================================================================
coatings.py  -  multilayer thin-film coating reflectivity (transfer matrix)
================================================================================
Every surface in the chain (lenses, windows, mirrors, polarizers) carries a
thin-film coating: anti-reflection (AR) on transmissive optics to kill Fresnel
loss and back-reflections, high-reflection (HR) on mirrors. These are
multilayer dielectric stacks, and their reflectivity vs wavelength is computed
with the optical TRANSFER-MATRIX METHOD. The chain has dozens of surfaces, so a
0.2% AR residual per surface compounds; this module lets you design and check a
stack.

Model
-----
  Each layer: characteristic matrix
      M = [[cos d, i sin d / eta], [i eta sin d, cos d]],  d = 2 pi n t / lambda
  Stack matrix = product of layer matrices. Reflectivity from the total matrix
  and the substrate/incident admittances.

Includes quarter-wave AR (single layer) and a quarter-wave HR stack (alternating
high/low index).

Run:
    python coatings.py                 # AR + HR examples vs wavelength
    python coatings.py --hr-pairs 15
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


def layer_matrix(n: float, thickness_nm: float, lam_nm: float):
    d = 2.0 * np.pi * n * thickness_nm / lam_nm
    return np.array([[np.cos(d), 1j * np.sin(d) / n],
                     [1j * n * np.sin(d), np.cos(d)]], dtype=complex)


def reflectivity(layers: List[Tuple[float, float]], lam_nm: float,
                 n_incident: float = 1.0, n_substrate: float = 1.52) -> float:
    """layers = list of (index, thickness_nm) from incident side to substrate."""
    M = np.eye(2, dtype=complex)
    for n, t in layers:
        M = M @ layer_matrix(n, t, lam_nm)
    n0, ns = n_incident, n_substrate
    B = M[0, 0] + M[0, 1] * ns
    C = M[1, 0] + M[1, 1] * ns
    r = (n0 * B - C) / (n0 * B + C)
    return float(np.abs(r) ** 2)


def ar_single(lam0_nm: float, n_film: float, n_substrate: float):
    """Quarter-wave AR layer (ideal n_film = sqrt(n_sub))."""
    t = lam0_nm / (4.0 * n_film)
    return [(n_film, t)]


def hr_stack(lam0_nm: float, n_high: float, n_low: float, pairs: int):
    """Quarter-wave HR stack: alternating high/low index pairs."""
    th = lam0_nm / (4.0 * n_high)
    tl = lam0_nm / (4.0 * n_low)
    layers = []
    for _ in range(pairs):
        layers.append((n_high, th))
        layers.append((n_low, tl))
    return layers


def main():
    ap = argparse.ArgumentParser(description="Thin-film coating reflectivity")
    ap.add_argument("--lam0", type=float, default=1064.0)
    ap.add_argument("--hr-pairs", type=int, default=15)
    args = ap.parse_args()

    n_sub = 1.52
    ar = ar_single(args.lam0, np.sqrt(n_sub), n_sub)
    hr = hr_stack(args.lam0, 2.30, 1.45, args.hr_pairs)   # TiO2 / SiO2

    R_ar = reflectivity(ar, args.lam0, n_substrate=n_sub)
    R_hr = reflectivity(hr, args.lam0, n_substrate=n_sub)
    R_bare = ((1.0 - n_sub) / (1.0 + n_sub)) ** 2

    print("=" * 60)
    print(" Thin-film coating reflectivity (transfer matrix)")
    print("=" * 60)
    print(f"  design wavelength   : {args.lam0:.0f} nm")
    print(f"  bare substrate R    : {R_bare*100:.2f} %")
    print(f"  single-layer AR R   : {R_ar*100:.3f} %")
    print(f"  HR stack ({args.hr_pairs} pairs) R: {R_hr*100:.3f} %")
    print("=" * 60)

    if _HAVE_MPL:
        lams = np.linspace(800, 1400, 400)
        r_ar = [reflectivity(ar, l, n_substrate=n_sub) for l in lams]
        r_hr = [reflectivity(hr, l, n_substrate=n_sub) for l in lams]
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
        ax[0].plot(lams, np.array(r_ar) * 100, lw=2)
        ax[0].axvline(args.lam0, color="r", ls="--")
        ax[0].set(title="AR coating", xlabel="wavelength [nm]", ylabel="R [%]")
        ax[1].plot(lams, np.array(r_hr) * 100, lw=2, color="tab:purple")
        ax[1].axvline(args.lam0, color="r", ls="--")
        ax[1].set(title=f"HR stack ({args.hr_pairs} pairs)",
                  xlabel="wavelength [nm]", ylabel="R [%]")
        plt.tight_layout(); plt.savefig("coatings.png", dpi=130)
        print("Saved -> coatings.png")
        plt.show()


if __name__ == "__main__":
    main()
