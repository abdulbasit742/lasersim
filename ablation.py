#!/usr/bin/env python3
"""
================================================================================
ablation.py  -  picosecond-laser material ablation & micromachining
================================================================================
The paper lists material processing as a target application. Picosecond pulses
ablate material almost athermally: above a threshold fluence, each pulse removes
a thin layer whose depth grows LOGARITHMICALLY with fluence (the classic
two-region log-ablation law). This module models ablation depth per pulse,
threshold fluence, and the processing throughput (volume removed per second)
for a scanning beam, so you can size a micromachining job.

Model
-----
  Depth per pulse (single-region log law):
      d(F) = delta * ln(F / F_th),   for F > F_th
  delta = effective penetration depth (energy absorption length).
  Throughput = depth/pulse * spot area * rep rate (per scanned spot).

Reports threshold fluence, depth per pulse, and material removal rate.

Run:
    python ablation.py
    python ablation.py --fluence 2.0 --material steel
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class AblationMaterial:
    name: str
    f_threshold_Jcm2: float    # ablation threshold fluence
    penetration_nm: float      # effective penetration depth delta


MATERIALS: Dict[str, AblationMaterial] = {
    "steel": AblationMaterial("stainless steel", 0.10, 15.0),
    "aluminum": AblationMaterial("aluminum", 0.20, 12.0),
    "silicon": AblationMaterial("silicon", 0.18, 30.0),
    "fused_silica": AblationMaterial("fused silica", 2.5, 100.0),
    "copper": AblationMaterial("copper", 0.35, 10.0),
}


@dataclass
class Ablator:
    material: AblationMaterial
    spot_radius_um: float = 25.0
    rep_hz: float = 10.0

    def depth_per_pulse_nm(self, fluence_Jcm2: float) -> float:
        if fluence_Jcm2 <= self.material.f_threshold_Jcm2:
            return 0.0
        return self.material.penetration_nm * np.log(
            fluence_Jcm2 / self.material.f_threshold_Jcm2)

    def spot_area_cm2(self) -> float:
        return np.pi * (self.spot_radius_um * 1e-4) ** 2

    def removal_rate_mm3_per_s(self, fluence_Jcm2: float) -> float:
        depth_cm = self.depth_per_pulse_nm(fluence_Jcm2) * 1e-7
        vol_cm3 = depth_cm * self.spot_area_cm2()
        return vol_cm3 * self.rep_hz * 1e3   # cm^3 -> mm^3

    def pulse_energy_for_fluence(self, fluence_Jcm2: float) -> float:
        return fluence_Jcm2 * self.spot_area_cm2()


def main():
    ap = argparse.ArgumentParser(description="Picosecond ablation / micromachining")
    ap.add_argument("--fluence", type=float, default=2.0, help="fluence [J/cm^2]")
    ap.add_argument("--material", choices=list(MATERIALS), default="steel")
    ap.add_argument("--spot-um", type=float, default=25.0)
    ap.add_argument("--rep-hz", type=float, default=10.0)
    args = ap.parse_args()

    ab = Ablator(MATERIALS[args.material], spot_radius_um=args.spot_um, rep_hz=args.rep_hz)
    d = ab.depth_per_pulse_nm(args.fluence)
    rate = ab.removal_rate_mm3_per_s(args.fluence)
    e_pulse = ab.pulse_energy_for_fluence(args.fluence)

    print("=" * 60)
    print(f" Picosecond ablation: {ab.material.name}")
    print("=" * 60)
    print(f"  fluence             : {args.fluence:.2f} J/cm^2")
    print(f"  threshold fluence   : {ab.material.f_threshold_Jcm2:.2f} J/cm^2")
    print(f"  spot radius         : {args.spot_um:.0f} um")
    print(f"  pulse energy needed : {e_pulse*1e3:.3f} mJ")
    print(f"  depth per pulse     : {d:.1f} nm")
    print(f"  removal rate        : {rate:.3e} mm^3/s @ {args.rep_hz:.0f} Hz")
    if d <= 0:
        print("  -> below threshold: no ablation")
    print("=" * 60)

    if _HAVE_MPL:
        Fs = np.linspace(0.01, max(args.fluence * 2, 5), 200)
        depths = [ab.depth_per_pulse_nm(f) for f in Fs]
        plt.figure(figsize=(8, 4.2))
        plt.semilogx(Fs, depths, lw=2)
        plt.axvline(ab.material.f_threshold_Jcm2, color="r", ls="--", label="threshold")
        plt.axvline(args.fluence, color="tab:green", ls=":", label="operating")
        plt.xlabel("fluence [J/cm^2] (log)"); plt.ylabel("depth per pulse [nm]")
        plt.title(f"Log-ablation law: {ab.material.name}")
        plt.legend(); plt.tight_layout(); plt.savefig("ablation.png", dpi=130)
        print("Saved -> ablation.png")
        plt.show()


if __name__ == "__main__":
    main()
