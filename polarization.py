#!/usr/bin/env python3
"""
================================================================================
polarization.py  -  Jones-calculus polarization optics for the amplifier chain
================================================================================
The paper relies heavily on polarization control, and none of the other modules
covered it:
  * quarter-wave plates (lambda/4) before each gain module to make the beam
    CIRCULARLY polarized -> reduces the nonlinear index n2 by 2/3,
  * half-wave plates (lambda/2) to rotate linear polarization,
  * thin-film polarizers (TFP) to combine/separate s- and p-polarization in the
    double-pass amplifier folds,
  * Faraday isolators to block back-reflections into earlier stages.

This module implements all of those as 2x2 Jones matrices, lets you build an
optical chain, and computes the output polarization state + the effective n2
reduction the beam will experience in the next gain module.

Run:
    python polarization.py             # model the AMP-1 double-pass pol. path
    python polarization.py --demo waveplate-sweep
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


# ==============================================================================
# JONES VECTORS (polarization states)
# ==============================================================================
H = np.array([1.0, 0.0], dtype=complex)              # horizontal / p
V = np.array([0.0, 1.0], dtype=complex)              # vertical / s
D = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)  # +45 diagonal
L = np.array([1.0, 1j], dtype=complex) / np.sqrt(2)   # left circular
R = np.array([1.0, -1j], dtype=complex) / np.sqrt(2)  # right circular


# ==============================================================================
# JONES MATRICES (optical elements)
# ==============================================================================
def rot(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def waveplate(retardance, angle=0.0):
    """General linear retarder. retardance in radians (pi=HWP, pi/2=QWP)."""
    J = np.array([[np.exp(-1j * retardance / 2), 0],
                  [0, np.exp(1j * retardance / 2)]], dtype=complex)
    return rot(angle) @ J @ rot(-angle)


def hwp(angle=0.0):
    return waveplate(np.pi, angle)


def qwp(angle=0.0):
    return waveplate(np.pi / 2, angle)


def polarizer(angle=0.0):
    """Ideal linear polarizer transmitting along `angle`."""
    P = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    return rot(angle) @ P @ rot(-angle)


def tfp(transmit="p"):
    """Thin-film polarizer: transmits p (horizontal) or s (vertical)."""
    return polarizer(0.0) if transmit == "p" else polarizer(np.pi / 2)


def faraday_rotator(angle=np.pi / 4):
    """Non-reciprocal 45-degree rotator (the heart of an isolator)."""
    return rot(angle)


# ==============================================================================
# ANALYSIS
# ==============================================================================
def apply(chain: List[np.ndarray], state: np.ndarray) -> np.ndarray:
    out = state.astype(complex)
    for M in chain:
        out = M @ out
    return out


def stokes(state: np.ndarray) -> Tuple[float, float, float, float]:
    ex, ey = state
    S0 = abs(ex) ** 2 + abs(ey) ** 2
    S1 = abs(ex) ** 2 - abs(ey) ** 2
    S2 = 2 * np.real(ex * np.conj(ey))
    S3 = -2 * np.imag(ex * np.conj(ey))
    return float(S0), float(S1), float(S2), float(S3)


def ellipticity(state: np.ndarray) -> float:
    """Degree of circular polarization, |S3|/S0. 1.0 = perfectly circular."""
    S0, _, _, S3 = stokes(state)
    return abs(S3) / S0 if S0 > 0 else 0.0


def n2_reduction(state: np.ndarray, n2_linear: float = 6.21e-16) -> float:
    """Effective nonlinear index. Circular polarization reduces n2 to 2/3.
    Interpolate by degree of circularity (S3)."""
    circ = ellipticity(state)
    factor = 1.0 - circ * (1.0 - 2.0 / 3.0)
    return n2_linear * factor


def classify(state: np.ndarray) -> str:
    e = ellipticity(state)
    if e > 0.95:
        return "circular"
    if e < 0.05:
        return "linear"
    return "elliptical"


# ==============================================================================
# DEMOS
# ==============================================================================
def demo_amp_path():
    """AMP-1 style: linear seed -> QWP at 45 deg -> circular into the gain rod."""
    seed = H.copy()
    print("=" * 60)
    print(" Polarization path: linear seed -> QWP(45) -> gain module")
    print("=" * 60)
    chain = [qwp(np.pi / 4)]
    out = apply(chain, seed)
    print(f"  input  : {classify(seed)}  (n2 = {n2_reduction(seed):.3e})")
    print(f"  output : {classify(out)}  ellipticity {ellipticity(out):.3f}")
    print(f"  n2 into gain rod : {n2_reduction(out):.3e} cm^2/W")
    print(f"  -> B-integral reduced by factor {n2_reduction(out)/n2_reduction(seed):.3f}")
    print("=" * 60)


def demo_waveplate_sweep():
    angles = np.linspace(0, np.pi / 2, 200)
    circ = [ellipticity(qwp(a) @ H) for a in angles]
    best = angles[int(np.argmax(circ))]
    print(f"QWP angle for max circular polarization: {np.degrees(best):.1f} deg "
          f"(ellipticity {max(circ):.3f})")
    if _HAVE_MPL:
        plt.plot(np.degrees(angles), circ, lw=2)
        plt.axvline(45, color="r", ls="--")
        plt.xlabel("QWP fast-axis angle [deg]")
        plt.ylabel("degree of circular polarization")
        plt.title("QWP angle -> circularity (n2 mitigation)")
        plt.tight_layout(); plt.savefig("polarization.png", dpi=130)
        print("Saved -> polarization.png")
        plt.show()


def main():
    ap = argparse.ArgumentParser(description="Jones-calculus polarization optics")
    ap.add_argument("--demo", choices=["amp-path", "waveplate-sweep"],
                    default="amp-path")
    args = ap.parse_args()
    if args.demo == "waveplate-sweep":
        demo_waveplate_sweep()
    else:
        demo_amp_path()


if __name__ == "__main__":
    main()
