#!/usr/bin/env python3
"""
================================================================================
safety.py  -  laser eye/skin hazard analysis (MPE, NOHD, hazard class)
================================================================================
A 1.28 J / 200 ps / 6.4 GW beam is extremely dangerous. Any real lab needs the
safety numbers: the Maximum Permissible Exposure (MPE), the Nominal Ocular
Hazard Distance (NOHD, how far away the beam is still eye-damaging), the optical
density (OD) of goggles needed, and the IEC 60825 hazard class. This module
computes them for the platform's output. It's the module that keeps a person
safe, which matters more than any efficiency number.

Model (simplified, 1064 nm, single pulse)
-----------------------------------------
  MPE (retinal, ~ns-us, 1064 nm) ~ 5e-3 J/cm^2 (corrected for wavelength).
  Eye collects through a 7 mm pupil -> energy into eye = fluence * pupil area.
  NOHD: distance where the diverging beam fluence drops to the MPE.
  Goggle OD: log10( beam fluence at eye / MPE ).

Reports MPE, on-axis hazard, NOHD, required goggle OD, and the hazard class.

Run:
    python safety.py
    python safety.py --energy-J 1.28 --divergence-mrad 0.5
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

PUPIL_DIAMETER_CM = 0.7      # 7 mm dark-adapted pupil
MPE_1064_JCM2 = 5e-3         # single-pulse retinal MPE near 1064 nm (approx)


@dataclass
class BeamHazard:
    energy_J: float = 1.28
    waist_radius_cm: float = 0.8
    divergence_mrad: float = 0.5
    mpe_Jcm2: float = MPE_1064_JCM2

    def fluence_at(self, distance_m: float) -> float:
        """On-axis fluence [J/cm^2] at a distance, beam expanding by divergence."""
        r_cm = self.waist_radius_cm + (self.divergence_mrad * 1e-3) * (distance_m * 100)
        area = np.pi * r_cm ** 2
        return self.energy_J / area

    def nohd_m(self) -> float:
        """Distance at which fluence falls to the MPE."""
        # solve energy/(pi r^2) = MPE for r, then back out distance
        r_mpe_cm = np.sqrt(self.energy_J / (np.pi * self.mpe_Jcm2))
        extra_cm = r_mpe_cm - self.waist_radius_cm
        if extra_cm <= 0:
            return 0.0
        return (extra_cm / (self.divergence_mrad * 1e-3)) / 100.0

    def required_OD(self, distance_m: float = 0.0) -> float:
        f = self.fluence_at(distance_m)
        return max(np.log10(f / self.mpe_Jcm2), 0.0)

    def hazard_class(self) -> str:
        # any J-level beam is Class 4 by a wide margin
        e_into_eye = self.fluence_at(0.0) * np.pi * (PUPIL_DIAMETER_CM / 2) ** 2
        if e_into_eye < 3.9e-7:
            return "Class 1 (safe)"
        if self.energy_J < 5e-3:
            return "Class 3R/3B"
        return "Class 4 (skin & fire hazard, diffuse reflections dangerous)"


def main():
    ap = argparse.ArgumentParser(description="Laser hazard analysis")
    ap.add_argument("--energy-J", type=float, default=1.28)
    ap.add_argument("--divergence-mrad", type=float, default=0.5)
    ap.add_argument("--waist-cm", type=float, default=0.8)
    args = ap.parse_args()

    h = BeamHazard(energy_J=args.energy_J, waist_radius_cm=args.waist_cm,
                   divergence_mrad=args.divergence_mrad)

    print("=" * 60)
    print(" Laser hazard analysis (1064 nm, single pulse)")
    print("=" * 60)
    print(f"  output energy        : {args.energy_J*1e3:.0f} mJ")
    print(f"  MPE (retinal)        : {h.mpe_Jcm2:.1e} J/cm^2")
    print(f"  fluence at aperture  : {h.fluence_at(0.0):.2f} J/cm^2")
    print(f"  exceeds MPE by       : {h.fluence_at(0.0)/h.mpe_Jcm2:.0e} x")
    print(f"  NOHD (eye-safe dist.): {h.nohd_m():.0f} m")
    print(f"  goggle OD at source  : {h.required_OD(0.0):.1f}")
    print(f"  hazard class         : {h.hazard_class()}")
    print("=" * 60)
    print("  WARNING: J-level ps pulses are a Class 4 hazard. Diffuse")
    print("  reflections can blind and ignite. Always use rated goggles.")
    print("=" * 60)

    if _HAVE_MPL:
        d = np.linspace(0.1, max(h.nohd_m() * 1.3, 10), 300)
        f = [h.fluence_at(x) for x in d]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(d, f, lw=2)
        plt.axhline(h.mpe_Jcm2, color="r", ls="--", label="MPE")
        plt.axvline(h.nohd_m(), color="tab:orange", ls=":", label=f"NOHD {h.nohd_m():.0f} m")
        plt.xlabel("distance [m]"); plt.ylabel("on-axis fluence [J/cm^2]")
        plt.title("Eye hazard vs distance")
        plt.legend(); plt.tight_layout(); plt.savefig("safety.png", dpi=130)
        print("Saved -> safety.png")
        plt.show()


if __name__ == "__main__":
    main()
