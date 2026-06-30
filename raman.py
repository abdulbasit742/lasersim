#!/usr/bin/env python3
"""
================================================================================
raman.py  -  stimulated Raman scattering (SRS) threshold & conversion
================================================================================
At very high intensity, light can scatter off molecular/optical vibrations and
be amplified at a downshifted (Stokes) wavelength: stimulated Raman scattering.
In a high-energy ps chain it's a PARASITIC LOSS: energy bleeds out of the main
beam into a Stokes beam (in long air paths, in fused-silica optics, in any
long transparent medium). It also seeds beam breakup. The classic figure of
merit is the Raman gain-length product g_R * I * L; once it exceeds ~25-30 the
Stokes wave grows from noise and steals energy. No module covered this.

Model
-----
  Stokes growth (undepleted pump): I_S(L) = I_S(0) * exp(g_R * I_pump * L)
  SRS threshold: g_R * I_pump * L_eff ~ 25 (G_th, from noise to ~pump level)
  Reports the gain exponent for the chain, whether SRS turns on, and the
  Stokes wavelength shift for a given Raman medium.

Run:
    python raman.py
    python raman.py --intensity 5e13 --length-m 2 --medium air
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

C0 = 2.99792458e8
G_THRESHOLD = 25.0     # classic SRS threshold gain exponent (noise -> pump)


@dataclass
class RamanMedium:
    name: str
    g_raman_m_per_W: float    # Raman gain coefficient [m/W]
    shift_cm1: float          # Raman shift [cm^-1]


MEDIA: Dict[str, RamanMedium] = {
    # representative values
    "air": RamanMedium("air (N2)", 1.0e-13, 2331.0),
    "fused_silica": RamanMedium("fused silica", 1.5e-13, 440.0),
    "water": RamanMedium("water", 1.4e-13, 3400.0),
    "methane": RamanMedium("methane", 6.6e-13, 2914.0),
}


def stokes_wavelength_nm(pump_nm: float, shift_cm1: float) -> float:
    """Stokes wavelength from the Raman shift."""
    nu_pump = 1e7 / pump_nm          # cm^-1
    nu_stokes = nu_pump - shift_cm1
    return 1e7 / nu_stokes if nu_stokes > 0 else float("inf")


@dataclass
class SRS:
    medium: RamanMedium
    pump_nm: float = 1064.0

    def gain_exponent(self, intensity_W_m2: float, length_m: float) -> float:
        return self.medium.g_raman_m_per_W * intensity_W_m2 * length_m

    def above_threshold(self, intensity_W_m2: float, length_m: float) -> bool:
        return self.gain_exponent(intensity_W_m2, length_m) >= G_THRESHOLD

    def threshold_intensity(self, length_m: float) -> float:
        return G_THRESHOLD / (self.medium.g_raman_m_per_W * length_m)

    def stokes_nm(self) -> float:
        return stokes_wavelength_nm(self.pump_nm, self.medium.shift_cm1)


def main():
    ap = argparse.ArgumentParser(description="Stimulated Raman scattering")
    ap.add_argument("--intensity", type=float, default=5e13, help="pump intensity [W/m^2]")
    ap.add_argument("--length-m", type=float, default=2.0, help="interaction length [m]")
    ap.add_argument("--medium", choices=list(MEDIA), default="air")
    args = ap.parse_args()

    srs = SRS(MEDIA[args.medium])
    G = srs.gain_exponent(args.intensity, args.length_m)
    I_th = srs.threshold_intensity(args.length_m)

    print("=" * 60)
    print(f" Stimulated Raman scattering: {srs.medium.name}")
    print("=" * 60)
    print(f"  pump wavelength     : {srs.pump_nm:.0f} nm")
    print(f"  Raman shift         : {srs.medium.shift_cm1:.0f} cm^-1")
    print(f"  Stokes wavelength   : {srs.stokes_nm():.1f} nm")
    print(f"  intensity / length  : {args.intensity:.1e} W/m^2 over {args.length_m:.1f} m")
    print(f"  gain exponent gIL   : {G:.1f} (threshold ~{G_THRESHOLD:.0f})")
    print(f"  SRS status          : {'ABOVE THRESHOLD (energy loss!)' if G >= G_THRESHOLD else 'safe'}")
    print(f"  threshold intensity : {I_th:.1e} W/m^2 for this length")
    print("=" * 60)

    if _HAVE_MPL:
        Is = np.linspace(1e12, max(args.intensity * 1.5, 1e14), 200)
        Gs = [srs.gain_exponent(i, args.length_m) for i in Is]
        plt.figure(figsize=(8, 4.2))
        plt.plot(Is, Gs, lw=2)
        plt.axhline(G_THRESHOLD, color="r", ls="--", label="SRS threshold")
        plt.axvline(args.intensity, color="tab:green", ls=":", label="operating point")
        plt.xlabel("pump intensity [W/m^2]"); plt.ylabel("Raman gain exponent gIL")
        plt.title(f"SRS gain vs intensity ({srs.medium.name}, {args.length_m:.0f} m)")
        plt.legend(); plt.tight_layout(); plt.savefig("raman.png", dpi=130)
        print("Saved -> raman.png")
        plt.show()


if __name__ == "__main__":
    main()
