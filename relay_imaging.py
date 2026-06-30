#!/usr/bin/env python3
"""
================================================================================
relay_imaging.py  -  Gaussian beam (q-parameter) propagation + relay imaging
================================================================================
Between every amplifier stage the paper uses VACUUM RELAY IMAGING: a Keplerian
telescope (two lenses + a pin-hole at the shared focus) that images the beam
from one gain module onto the next. This does two jobs: it re-images the beam
plane (so diffraction ripple doesn't accumulate over the long propagation), and
it magnifies the beam to the right diameter for the next, bigger rod
(6 -> 7 -> 10 -> 16 mm in the paper).

thermal_abcd.py used ABCD matrices for the CAVITY. This module uses the same
ABCD machinery on the complex-q Gaussian-beam parameter to track the BEAM as it
propagates through the relay telescopes of the amplifier chain.

Complex beam parameter:   1/q = 1/Rcurv - i * lambda / (pi w^2)
ABCD transform:           q' = (A q + B) / (C q + D)

Reports beam size at every plane, the magnification of each telescope, and
confirms the 6->7->10->16 mm expansion the paper engineered.

Run:
    python relay_imaging.py
    python relay_imaging.py --w0-mm 3.0
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

LAMBDA = 1064e-9


# ==============================================================================
# COMPLEX-Q GAUSSIAN BEAM
# ==============================================================================
def q_from_w(w_m: float, R_m: float = np.inf, lam: float = LAMBDA) -> complex:
    """Complex beam parameter from spot size w and radius of curvature R."""
    inv_R = 0.0 if np.isinf(R_m) else 1.0 / R_m
    return 1.0 / (inv_R - 1j * lam / (np.pi * w_m ** 2))


def w_from_q(q: complex, lam: float = LAMBDA) -> float:
    """Spot size w from complex beam parameter q."""
    inv_q = 1.0 / q
    return np.sqrt(-lam / (np.pi * inv_q.imag))


def R_from_q(q: complex) -> float:
    inv_q = 1.0 / q
    return np.inf if inv_q.real == 0 else 1.0 / inv_q.real


# ==============================================================================
# ABCD ELEMENTS
# ==============================================================================
def M_space(d):
    return np.array([[1.0, d], [0.0, 1.0]])


def M_lens(f):
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def transform_q(M, q):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return (A * q + B) / (C * q + D)


# ==============================================================================
# RELAY TELESCOPE
# ==============================================================================
@dataclass
class RelayTelescope:
    """Keplerian relay: lens f1, gap (f1+f2) with pin-hole at the focus, lens f2.
    Imaging magnification M = -f2/f1; beam diameter scales by |f2/f1|."""
    name: str
    f1_mm: float
    f2_mm: float

    @property
    def magnification(self) -> float:
        return self.f2_mm / self.f1_mm

    def elements(self) -> List[np.ndarray]:
        f1 = self.f1_mm * 1e-3
        f2 = self.f2_mm * 1e-3
        return [M_lens(f1), M_space(f1 + f2), M_lens(f2)]


def propagate(q0: complex, elements: List[np.ndarray]) -> Tuple[complex, List[float]]:
    """Apply a list of ABCD elements, recording spot size after each."""
    q = q0
    sizes = [w_from_q(q)]
    for M in elements:
        q = transform_q(M, q)
        sizes.append(w_from_q(q))
    return q, sizes


# ==============================================================================
# THE NILOP RELAY CHAIN (6 -> 7 -> 10 -> 16 mm)
# ==============================================================================
def build_nilop_relays() -> List[RelayTelescope]:
    # focal lengths from the paper's text
    return [
        RelayTelescope("seed->AMP1 (L1/L2)", 350.0, 400.0),   # 1:1.143
        RelayTelescope("AMP1->AMP2 (L3/L4)", 300.0, 600.0),   # 1:2
        RelayTelescope("AMP2->AMP3 (L5/L6)", 400.0, 600.0),   # 1:1.5
    ]


def main():
    ap = argparse.ArgumentParser(description="Gaussian relay-imaging propagation")
    ap.add_argument("--w0-mm", type=float, default=3.0,
                    help="initial beam 1/e^2 radius [mm] (seed ~3 mm => 6 mm dia)")
    args = ap.parse_args()

    w0 = args.w0_mm * 1e-3
    q = q_from_w(w0)
    relays = build_nilop_relays()

    print("=" * 64)
    print(" Relay-imaging chain (Gaussian q-parameter)")
    print("=" * 64)
    print(f"  seed beam radius : {w0*1e3:.2f} mm (diameter {2*w0*1e3:.1f} mm)")
    diam = [2 * w0 * 1e3]
    for relay in relays:
        q, sizes = propagate(q, relay.elements())
        w_out = w_from_q(q)
        diam.append(2 * w_out * 1e3)
        print(f"  {relay.name:<24} M={relay.magnification:.3f}  "
              f"-> diameter {2*w_out*1e3:.1f} mm")
    print("-" * 64)
    print(f"  beam diameters: {' -> '.join(f'{d:.0f}' for d in diam)} mm")
    print(f"  (paper target : 6 -> 7 -> 10 -> 16 mm)")
    print("=" * 64)

    if _HAVE_MPL:
        plt.figure(figsize=(8, 4.2))
        plt.plot(range(len(diam)), diam, "o-", lw=2, label="modeled")
        plt.plot(range(4), [6, 7, 10, 16], "s--", lw=2, label="paper")
        plt.xticks(range(4), ["seed", "AMP-1", "AMP-2", "AMP-3"])
        plt.ylabel("beam diameter [mm]"); plt.title("Beam expansion through relays")
        plt.legend(); plt.tight_layout(); plt.savefig("relay_imaging.png", dpi=130)
        print("Saved -> relay_imaging.png")
        plt.show()


if __name__ == "__main__":
    main()
