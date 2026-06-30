#!/usr/bin/env python3
"""
================================================================================
wavefront.py  -  Zernike wavefront aberrations & Strehl ratio
================================================================================
M^2 (beam_quality.py) is a single scalar. The full story is the WAVEFRONT: the
shape of the phase across the beam. Thermal lensing, pump non-uniformity, and
rod imperfections add aberrations (defocus, astigmatism, spherical, coma) that
distort the wavefront and lower the STREHL RATIO: the ratio of actual peak focal
intensity to the ideal diffraction-limited peak. Strehl ~ 1 is perfect; below
~0.8 the focus is visibly degraded. This connects the rod's thermal/aberration
state to delivered focal intensity.

Model
-----
  Wavefront expanded in Zernike modes: W(r,phi) = sum_j a_j Z_j(r,phi).
  RMS wavefront error sigma = sqrt(sum a_j^2) (orthonormal Zernikes, waves).
  Marechal Strehl approximation: S = exp(-(2 pi sigma)^2).

Reports the RMS wavefront error and Strehl ratio for a set of aberration
coefficients, and the focal-intensity penalty.

Run:
    python wavefront.py
    python wavefront.py --defocus 0.1 --astig 0.05 --spherical 0.03
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Dict

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


# ---- orthonormal Zernike polynomials (Noll), unit circle -------------------
def zernike(name, R, PHI):
    if name == "defocus":
        return np.sqrt(3) * (2 * R ** 2 - 1)
    if name == "astig":
        return np.sqrt(6) * R ** 2 * np.cos(2 * PHI)
    if name == "coma":
        return np.sqrt(8) * (3 * R ** 3 - 2 * R) * np.cos(PHI)
    if name == "spherical":
        return np.sqrt(5) * (6 * R ** 4 - 6 * R ** 2 + 1)
    if name == "trefoil":
        return np.sqrt(8) * R ** 3 * np.cos(3 * PHI)
    raise ValueError(f"unknown Zernike '{name}'")


ZERNIKES = ["defocus", "astig", "coma", "spherical", "trefoil"]


@dataclass
class Wavefront:
    coeffs: Dict[str, float] = field(default_factory=dict)  # waves RMS per mode
    npix: int = 257

    def rms_error(self) -> float:
        """RMS wavefront error in waves (orthonormal -> quadrature sum)."""
        return float(np.sqrt(sum(a ** 2 for a in self.coeffs.values())))

    def strehl(self) -> float:
        """Marechal approximation: S = exp(-(2 pi sigma)^2)."""
        sigma = self.rms_error()
        return float(np.exp(-(2 * np.pi * sigma) ** 2))

    def map(self):
        x = np.linspace(-1, 1, self.npix)
        X, Y = np.meshgrid(x, x)
        R = np.hypot(X, Y)
        PHI = np.arctan2(Y, X)
        W = np.zeros_like(R)
        for name, a in self.coeffs.items():
            W += a * zernike(name, R, PHI)
        W[R > 1] = np.nan
        return W


def main():
    ap = argparse.ArgumentParser(description="Zernike wavefront + Strehl ratio")
    for z in ZERNIKES:
        ap.add_argument(f"--{z}", type=float, default=0.0,
                        help=f"{z} coefficient [waves RMS]")
    args = ap.parse_args()

    coeffs = {z: getattr(args, z) for z in ZERNIKES if getattr(args, z) != 0.0}
    if not coeffs:
        coeffs = {"defocus": 0.08, "astig": 0.05, "spherical": 0.03}
    wf = Wavefront(coeffs)

    print("=" * 56)
    print(" Wavefront aberration & Strehl ratio")
    print("=" * 56)
    for name, a in coeffs.items():
        print(f"  {name:<12}: {a:+.3f} waves")
    print("-" * 56)
    print(f"  RMS wavefront error : {wf.rms_error():.3f} waves")
    print(f"  Strehl ratio        : {wf.strehl():.3f}")
    q = "diffraction-limited" if wf.strehl() >= 0.8 else "degraded focus"
    print(f"  focus quality       : {q} (>=0.8 = good)")
    print(f"  peak focal intensity: {wf.strehl()*100:.0f}% of ideal")
    print("=" * 56)

    if _HAVE_MPL:
        W = wf.map()
        plt.figure(figsize=(5.4, 4.6))
        im = plt.imshow(W, cmap="RdBu", extent=[-1, 1, -1, 1])
        plt.colorbar(im, label="wavefront [waves]")
        plt.title(f"Wavefront (Strehl {wf.strehl():.2f})")
        plt.tight_layout(); plt.savefig("wavefront.png", dpi=130)
        print("Saved -> wavefront.png")
        plt.show()


if __name__ == "__main__":
    main()
