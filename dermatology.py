#!/usr/bin/env python3
"""
================================================================================
dermatology.py  -  picosecond laser dermatology (tattoo / pigment removal)
================================================================================
The paper lists dermatology/medical surgery as applications (refs [8-10]). Ps
pulses are the modern standard for tattoo and pigment removal because they're
shorter than the target's THERMAL RELAXATION TIME: the pulse deposits energy
faster than heat can diffuse out of the pigment particle, so the particle is
fragmented PHOTOACOUSTICALLY (a pressure shockwave) rather than just heated,
sparing surrounding tissue. This module captures that selective-photothermolysis
physics.

Model
-----
  Thermal relaxation time of a particle of diameter d:
      tau_r ~ d^2 / (k_alpha)         (k_alpha = thermal diffusivity term)
  Selective photoacoustic regime when pulse_duration << tau_r.
  Safe fluence window: above fragmentation threshold, below epidermal-damage
  (burn) threshold.

Reports the thermal relaxation time for a pigment size, whether the ps pulse is
in the photoacoustic regime, and the safe treatment fluence window.

Run:
    python dermatology.py
    python dermatology.py --particle-nm 200 --pulse-ps 200
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

# thermal diffusivity of tissue/pigment ~ 1.3e-7 m^2/s
DIFFUSIVITY = 1.3e-7


@dataclass
class DermaTreatment:
    particle_diameter_nm: float = 200.0   # tattoo ink / melanosome size
    pulse_ps: float = 200.0
    frag_threshold_Jcm2: float = 0.3      # photoacoustic fragmentation onset
    burn_threshold_Jcm2: float = 3.0      # epidermal damage limit

    def thermal_relaxation_s(self) -> float:
        d = self.particle_diameter_nm * 1e-9
        return d ** 2 / (27.0 * DIFFUSIVITY)   # ~ d^2 / (k*alpha), k~27 for sphere

    def is_photoacoustic(self) -> bool:
        return (self.pulse_ps * 1e-12) < self.thermal_relaxation_s()

    def confinement_ratio(self) -> float:
        """tau_relax / pulse_duration. >>1 means well thermally confined."""
        return self.thermal_relaxation_s() / (self.pulse_ps * 1e-12)

    def safe_window(self):
        return self.frag_threshold_Jcm2, self.burn_threshold_Jcm2


def main():
    ap = argparse.ArgumentParser(description="Picosecond dermatology model")
    ap.add_argument("--particle-nm", type=float, default=200.0)
    ap.add_argument("--pulse-ps", type=float, default=200.0)
    args = ap.parse_args()

    t = DermaTreatment(particle_diameter_nm=args.particle_nm, pulse_ps=args.pulse_ps)
    tau_r = t.thermal_relaxation_s()
    lo, hi = t.safe_window()

    print("=" * 60)
    print(" Picosecond dermatology (selective photothermolysis)")
    print("=" * 60)
    print(f"  pigment particle    : {args.particle_nm:.0f} nm")
    print(f"  pulse duration      : {args.pulse_ps:.0f} ps")
    print(f"  thermal relaxation  : {tau_r*1e9:.2f} ns")
    print(f"  confinement ratio   : {t.confinement_ratio():.1e} (tau_r / pulse)")
    print(f"  regime              : {'PHOTOACOUSTIC (fragmentation)' if t.is_photoacoustic() else 'photothermal (heating)'}")
    print(f"  safe fluence window : {lo:.2f} - {hi:.2f} J/cm^2")
    print("=" * 60)
    print("  Below window: no clearance. Above: epidermal burn/scarring risk.")
    print("=" * 60)

    if _HAVE_MPL:
        sizes = np.linspace(20, 2000, 200)
        taus = [DermaTreatment(s, args.pulse_ps).thermal_relaxation_s() * 1e9 for s in sizes]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(sizes, taus, lw=2, label="thermal relaxation time")
        plt.axhline(args.pulse_ps / 1e3, color="r", ls="--",
                    label=f"pulse {args.pulse_ps:.0f} ps")
        plt.axvline(args.particle_nm, color="tab:green", ls=":", label="particle")
        plt.xlabel("particle diameter [nm]"); plt.ylabel("thermal relaxation [ns]")
        plt.title("Selective photothermolysis: confinement window")
        plt.legend(); plt.tight_layout(); plt.savefig("dermatology.png", dpi=130)
        print("Saved -> dermatology.png")
        plt.show()


if __name__ == "__main__":
    main()
