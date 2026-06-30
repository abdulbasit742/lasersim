#!/usr/bin/env python3
"""
================================================================================
isolator.py  -  Faraday optical isolator
================================================================================
The paper puts Faraday isolators (ISO-1, ISO-2) between stages to block back-
reflections from re-entering and damaging earlier amplifiers (a self-lasing /
damage risk in a high-gain chain). A Faraday rotator turns polarization by an
angle set by the Verdet constant, the magnetic field, and the crystal length;
with input/output polarizers it passes the forward beam and rejects the
backward one. This module models the rotation, the isolation ratio, and how
temperature/field errors degrade it.

Model
-----
  Faraday rotation:  beta = V * B * L      (V = Verdet constant [rad/(T m)])
  For an isolator set beta = 45 deg. Forward + backward passes add to 90 deg so
  a crossed polarizer blocks the return.
  Isolation:  I = -20 log10( sin(2*(beta - 45deg)) )  [dB] (rotation error)

Run:
    python isolator.py
    python isolator.py --field-T 1.0 --length-mm 20
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class FaradayIsolator:
    verdet_rad_per_Tm: float = 35.0    # TGG near 1064 nm (~rad/(T m))
    field_T: float = 1.0
    length_mm: float = 18.0

    def rotation_deg(self) -> float:
        beta = self.verdet_rad_per_Tm * self.field_T * (self.length_mm * 1e-3)
        return np.degrees(beta)

    def isolation_dB(self) -> float:
        """Isolation set by deviation of the rotation from 45 deg."""
        err = np.radians(self.rotation_deg() - 45.0)
        leak = np.sin(err) ** 2          # power fraction leaking backward
        leak = max(leak, 1e-6)           # floor (polarizer extinction)
        return -10.0 * np.log10(leak)

    def field_for_45deg(self) -> float:
        """Magnetic field needed to hit exactly 45 deg rotation."""
        beta = np.radians(45.0)
        return beta / (self.verdet_rad_per_Tm * (self.length_mm * 1e-3))


def main():
    ap = argparse.ArgumentParser(description="Faraday optical isolator")
    ap.add_argument("--field-T", type=float, default=None)
    ap.add_argument("--length-mm", type=float, default=18.0)
    args = ap.parse_args()

    iso = FaradayIsolator(length_mm=args.length_mm)
    if args.field_T is not None:
        iso.field_T = args.field_T
    else:
        iso.field_T = iso.field_for_45deg()

    print("=" * 60)
    print(" Faraday optical isolator")
    print("=" * 60)
    print(f"  Verdet constant     : {iso.verdet_rad_per_Tm:.0f} rad/(T m) (TGG)")
    print(f"  crystal length      : {args.length_mm:.0f} mm")
    print(f"  magnetic field      : {iso.field_T:.3f} T")
    print(f"  Faraday rotation    : {iso.rotation_deg():.1f} deg (target 45)")
    print(f"  isolation           : {iso.isolation_dB():.1f} dB")
    print(f"  field for exact 45  : {iso.field_for_45deg():.3f} T")
    print("=" * 60)
    print("  Protects upstream amplifiers from back-reflections.")
    print("=" * 60)

    if _HAVE_MPL:
        fields = np.linspace(0.5, 1.5, 200)
        isos = []
        for B in fields:
            iso.field_T = B
            isos.append(iso.isolation_dB())
        plt.figure(figsize=(8, 4.2))
        plt.plot(fields, isos, lw=2)
        plt.axvline(iso.field_for_45deg(), color="r", ls="--", label="45 deg field")
        plt.xlabel("magnetic field [T]"); plt.ylabel("isolation [dB]")
        plt.title("Isolation vs magnetic field (rotation tuning)")
        plt.legend(); plt.tight_layout(); plt.savefig("isolator.png", dpi=130)
        print("Saved -> isolator.png")
        plt.show()


if __name__ == "__main__":
    main()
