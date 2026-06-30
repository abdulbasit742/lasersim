#!/usr/bin/env python3
"""
================================================================================
adaptive_optics.py  -  deformable-mirror wavefront correction
================================================================================
wavefront.py measured the aberrated wavefront and its Strehl ratio. The fix is
ADAPTIVE OPTICS: a deformable mirror (DM) with N actuators that pushes a
correcting shape onto the beam to flatten the wavefront, recovering focal
intensity. But a DM with finite actuators can only correct low-order, smooth
aberration; high-spatial-frequency residue is left behind (fitting error). This
module models that trade-off.

Model
-----
  A DM with N actuators corrects Zernike modes up to ~ order set by N.
  Corrected modes are removed (down to a residual servo error); uncorrected
  high-order modes remain.
  Residual RMS -> recovered Strehl via Marechal: S = exp(-(2 pi sigma_res)^2).

Reports the residual wavefront error and Strehl before/after correction, and how
Strehl improves as you add actuators.

Run:
    python adaptive_optics.py
    python adaptive_optics.py --actuators 37
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

from wavefront import Wavefront, ZERNIKES


# how many Zernike modes a DM with N actuators can usefully correct
def correctable_modes(n_actuators: int) -> int:
    # roughly sqrt(N) radial orders -> ~N correctable modes, cap to our basis
    return int(np.clip(np.floor(np.sqrt(n_actuators)) * 2, 0, len(ZERNIKES)))


@dataclass
class DeformableMirror:
    n_actuators: int = 37
    servo_residual: float = 0.01     # residual RMS per corrected mode [waves]

    def correct(self, wf: Wavefront) -> Wavefront:
        """Return the residual wavefront after DM correction."""
        n_modes = correctable_modes(self.n_actuators)
        # modes are corrected in the canonical order (low-order first)
        order = [z for z in ZERNIKES if z in wf.coeffs]
        residual = {}
        for i, name in enumerate(ZERNIKES):
            a = wf.coeffs.get(name, 0.0)
            if i < n_modes:
                # corrected down to the servo residual
                residual[name] = np.sign(a) * min(abs(a), self.servo_residual)
            else:
                residual[name] = a   # uncorrected high-order mode
        return Wavefront({k: v for k, v in residual.items() if v != 0.0})


def main():
    ap = argparse.ArgumentParser(description="Deformable-mirror correction")
    ap.add_argument("--actuators", type=int, default=37)
    args = ap.parse_args()

    aberrated = Wavefront({"defocus": 0.12, "astig": 0.08, "coma": 0.05,
                           "spherical": 0.04, "trefoil": 0.03})
    dm = DeformableMirror(n_actuators=args.actuators)
    residual = dm.correct(aberrated)

    print("=" * 58)
    print(" Adaptive-optics wavefront correction")
    print("=" * 58)
    print(f"  actuators            : {args.actuators}")
    print(f"  correctable modes    : {correctable_modes(args.actuators)} of {len(ZERNIKES)}")
    print(f"  RMS error  before    : {aberrated.rms_error():.3f} waves")
    print(f"  RMS error  after     : {residual.rms_error():.3f} waves")
    print(f"  Strehl     before    : {aberrated.strehl():.3f}")
    print(f"  Strehl     after     : {residual.strehl():.3f}")
    gain = residual.strehl() / max(aberrated.strehl(), 1e-9)
    print(f"  focal intensity gain : {gain:.2f}x")
    print("=" * 58)

    if _HAVE_MPL:
        acts = [1, 4, 9, 16, 25, 37, 61, 97]
        strehls = []
        for n in acts:
            r = DeformableMirror(n_actuators=n).correct(aberrated)
            strehls.append(r.strehl())
        plt.figure(figsize=(8, 4.2))
        plt.plot(acts, strehls, "o-", lw=2)
        plt.axhline(aberrated.strehl(), color="gray", ls="--", label="uncorrected")
        plt.axhline(0.8, color="r", ls=":", label="diffraction-limited (0.8)")
        plt.xlabel("actuator count"); plt.ylabel("Strehl ratio")
        plt.title("Strehl recovery vs deformable-mirror actuators")
        plt.legend(); plt.tight_layout(); plt.savefig("adaptive_optics.png", dpi=130)
        print("Saved -> adaptive_optics.png")
        plt.show()


if __name__ == "__main__":
    main()
