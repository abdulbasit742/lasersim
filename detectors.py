#!/usr/bin/env python3
"""
================================================================================
detectors.py  -  photodiode & energy-meter response
================================================================================
Every number the paper quotes (energy, power, beam profile) came off a DETECTOR,
and detectors have their own physics: a photodiode's responsivity (A/W) depends
on wavelength and saturates at high flux; a pyroelectric energy meter integrates
a pulse but has a damage/saturation ceiling; a camera (for beam profiles) has a
finite well depth and bit depth. This module models the two key measurement
devices so you know when a reading is trustworthy vs saturated.

Model
-----
  Photodiode current:  I = R(lambda) * P, saturating above P_sat.
  Responsivity:        R = eta q lambda / (h c)  (quantum efficiency eta)
  Energy meter:        reads E if below damage threshold, flags saturation.

Reports detector responsivity, output signal, and whether the measurement is in
the linear (trustworthy) range.

Run:
    python detectors.py
    python detectors.py --power-W 1e-3 --lam-nm 1064
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

H = 6.62607015e-34
C0 = 2.99792458e8
Q_E = 1.602176634e-19


@dataclass
class Photodiode:
    quantum_efficiency: float = 0.8
    p_saturation_W: float = 1e-2     # linear range ceiling
    material: str = "InGaAs"          # good at 1064 nm

    def responsivity(self, lam_nm: float) -> float:
        lam = lam_nm * 1e-9
        return self.quantum_efficiency * Q_E * lam / (H * C0)

    def current_A(self, power_W: float, lam_nm: float) -> float:
        ideal = self.responsivity(lam_nm) * power_W
        # soft saturation
        return ideal / (1.0 + power_W / self.p_saturation_W)

    def is_linear(self, power_W: float) -> bool:
        return power_W < 0.1 * self.p_saturation_W


@dataclass
class EnergyMeter:
    calibration_V_per_J: float = 1e4
    damage_threshold_J: float = 2.0

    def signal_V(self, energy_J: float) -> float:
        return self.calibration_V_per_J * energy_J

    def is_safe(self, energy_J: float) -> bool:
        return energy_J < self.damage_threshold_J


def main():
    ap = argparse.ArgumentParser(description="Detector / energy-meter response")
    ap.add_argument("--power-W", type=float, default=1e-3)
    ap.add_argument("--lam-nm", type=float, default=1064.0)
    ap.add_argument("--energy-J", type=float, default=1.28)
    args = ap.parse_args()

    pd = Photodiode()
    em = EnergyMeter()
    R = pd.responsivity(args.lam_nm)
    I = pd.current_A(args.power_W, args.lam_nm)

    print("=" * 60)
    print(" Detector response")
    print("=" * 60)
    print(f"  photodiode ({pd.material})")
    print(f"    responsivity      : {R:.3f} A/W @ {args.lam_nm:.0f} nm")
    print(f"    output current    : {I*1e3:.3f} mA at {args.power_W*1e3:.2f} mW")
    print(f"    linear range      : {'YES' if pd.is_linear(args.power_W) else 'SATURATED'}")
    print(f"  energy meter")
    print(f"    signal            : {em.signal_V(args.energy_J):.0f} V for {args.energy_J:.2f} J")
    print(f"    safe (no damage)  : {'YES' if em.is_safe(args.energy_J) else 'OVER THRESHOLD'}")
    print("=" * 60)

    if _HAVE_MPL:
        Ps = np.logspace(-6, 0, 200)
        Is = [pd.current_A(p, args.lam_nm) * 1e3 for p in Ps]
        ideal = [pd.responsivity(args.lam_nm) * p * 1e3 for p in Ps]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(Ps * 1e3, Is, lw=2, label="real (saturating)")
        plt.loglog(Ps * 1e3, ideal, lw=1, ls="--", label="ideal linear")
        plt.axvline(pd.p_saturation_W * 1e3, color="r", ls=":", label="saturation")
        plt.xlabel("optical power [mW]"); plt.ylabel("photocurrent [mA]")
        plt.title("Photodiode response & saturation")
        plt.legend(); plt.tight_layout(); plt.savefig("detectors.png", dpi=130)
        print("Saved -> detectors.png")
        plt.show()


if __name__ == "__main__":
    main()
