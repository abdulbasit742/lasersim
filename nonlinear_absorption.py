#!/usr/bin/env python3
"""
================================================================================
nonlinear_absorption.py  -  two-photon & nonlinear absorption
================================================================================
At the intensities in this chain, transparent optics stop being perfectly
transparent: TWO-PHOTON ABSORPTION (TPA) kicks in, where a material absorbs two
photons at once and the loss grows with INTENSITY (not just a fixed coefficient).
This both steals energy and heats the optic locally (a damage precursor). It's a
distinct loss channel from linear absorption (coatings) and from Raman (raman.py).

Model (Beer-Lambert with a nonlinear term)
------------------------------------------
  dI/dz = -alpha I - beta I^2
  alpha = linear absorption [1/m], beta = TPA coefficient [m/W].
  Closed-form transmission over length L for the nonlinear part:
      I(L) = I0 e^{-alpha L} / (1 + (beta I0 / alpha)(1 - e^{-alpha L}))

Reports the nonlinear transmission, the effective (intensity-dependent) loss,
and the intensity at which TPA loss equals linear loss.

Run:
    python nonlinear_absorption.py
    python nonlinear_absorption.py --intensity 5e13 --length-mm 10
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
class NonlinearAbsorber:
    name: str = "fused silica"
    alpha_per_m: float = 1e-2         # linear absorption [1/m]
    beta_m_per_W: float = 3e-13       # two-photon absorption coeff [m/W]

    def transmission(self, I0_Wm2: float, length_m: float) -> float:
        aL = self.alpha_per_m * length_m
        if self.alpha_per_m > 0:
            denom = 1.0 + (self.beta_m_per_W * I0_Wm2 / self.alpha_per_m) * (1 - np.exp(-aL))
            I_L = I0_Wm2 * np.exp(-aL) / denom
        else:
            I_L = I0_Wm2 / (1.0 + self.beta_m_per_W * I0_Wm2 * length_m)
        return float(I_L / I0_Wm2)

    def effective_loss(self, I0_Wm2: float, length_m: float) -> float:
        return 1.0 - self.transmission(I0_Wm2, length_m)

    def tpa_equals_linear_intensity(self) -> float:
        """Intensity where beta I = alpha (TPA loss matches linear loss)."""
        return self.alpha_per_m / self.beta_m_per_W


def main():
    ap = argparse.ArgumentParser(description="Two-photon / nonlinear absorption")
    ap.add_argument("--intensity", type=float, default=5e13, help="peak intensity [W/m^2]")
    ap.add_argument("--length-mm", type=float, default=10.0)
    args = ap.parse_args()

    na = NonlinearAbsorber()
    L = args.length_mm * 1e-3
    T = na.transmission(args.intensity, L)
    I_cross = na.tpa_equals_linear_intensity()

    print("=" * 60)
    print(f" Nonlinear absorption: {na.name}")
    print("=" * 60)
    print(f"  linear absorption   : {na.alpha_per_m:.1e} /m")
    print(f"  TPA coefficient beta: {na.beta_m_per_W:.1e} m/W")
    print(f"  intensity           : {args.intensity:.1e} W/m^2")
    print(f"  length              : {args.length_mm:.0f} mm")
    print(f"  transmission        : {T*100:.2f} %")
    print(f"  total loss          : {na.effective_loss(args.intensity, L)*100:.2f} %")
    print(f"  TPA=linear at I     : {I_cross:.1e} W/m^2")
    print(f"  -> {'TPA-dominated (nonlinear loss)' if args.intensity > I_cross else 'linear-dominated'}")
    print("=" * 60)

    if _HAVE_MPL:
        Is = np.logspace(11, 15, 200)
        loss = [na.effective_loss(i, L) * 100 for i in Is]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(Is, loss, lw=2)
        plt.axvline(I_cross, color="r", ls="--", label="TPA = linear")
        plt.axvline(args.intensity, color="tab:green", ls=":", label="operating")
        plt.xlabel("intensity [W/m^2]"); plt.ylabel("loss [%]")
        plt.title(f"Nonlinear absorption loss vs intensity ({na.name})")
        plt.legend(); plt.tight_layout(); plt.savefig("nonlinear_absorption.png", dpi=130)
        print("Saved -> nonlinear_absorption.png")
        plt.show()


if __name__ == "__main__":
    main()
