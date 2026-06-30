#!/usr/bin/env python3
"""
================================================================================
beam_quality.py  -  M^2 beam quality, beam-parameter product, brightness
================================================================================
A real beam isn't a perfect Gaussian. Its M^2 ("M-squared") factor says how many
times faster it diverges than an ideal Gaussian of the same waist. M^2 = 1 is
diffraction-limited; the booster rods in a high-energy chain typically push M^2
well above 1 because of thermal lensing and gain-induced aberration. M^2 sets
how tightly you can focus, which sets material-processing intensity and ranging
range. No module covered it, so here it is.

Key relations
-------------
  Real-beam divergence:   theta = M^2 * lambda / (pi w0)
  Beam-parameter product: BPP   = w0 * theta = M^2 * lambda / pi
  Real-beam size vs z:    w(z)  = w0 sqrt( 1 + ( M^2 lambda z / (pi w0^2) )^2 )
  Brightness:             B     = P / (lambda^2 M^4)   (radiance-like FOM)

Run:
    python beam_quality.py
    python beam_quality.py --m2 1.8 --w0-mm 8 --power 6.4e9
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

LAMBDA = 1064e-9


@dataclass
class BeamQuality:
    m2: float = 1.0
    w0_m: float = 8e-3        # waist radius
    lam: float = LAMBDA

    @property
    def divergence(self) -> float:
        """Half-angle far-field divergence [rad]."""
        return self.m2 * self.lam / (np.pi * self.w0_m)

    @property
    def bpp(self) -> float:
        """Beam-parameter product [m rad]."""
        return self.w0_m * self.divergence

    @property
    def rayleigh(self) -> float:
        """Rayleigh range [m] for the real beam."""
        return np.pi * self.w0_m ** 2 / (self.m2 * self.lam)

    def width(self, z):
        """Beam radius at distance z from the waist [m]."""
        return self.w0_m * np.sqrt(1.0 + (z / self.rayleigh) ** 2)

    def focal_spot(self, f_m, w_in_m):
        """1/e^2 focal-spot radius when focusing a collimated beam of radius
        w_in with a lens of focal length f."""
        return self.m2 * self.lam * f_m / (np.pi * w_in_m)

    def brightness(self, power_W) -> float:
        """Radiance-like figure of merit P / (lambda^2 M^4)."""
        return power_W / (self.lam ** 2 * self.m2 ** 2 * self.m2 ** 2)


def main():
    ap = argparse.ArgumentParser(description="M^2 beam-quality analysis")
    ap.add_argument("--m2", type=float, default=1.8)
    ap.add_argument("--w0-mm", type=float, default=8.0)
    ap.add_argument("--power", type=float, default=6.4e9,
                    help="peak power [W] (NILOP = 6.4 GW)")
    ap.add_argument("--focus-f-mm", type=float, default=200.0)
    args = ap.parse_args()

    bq = BeamQuality(m2=args.m2, w0_m=args.w0_mm * 1e-3)
    ideal = BeamQuality(m2=1.0, w0_m=args.w0_mm * 1e-3)
    spot = bq.focal_spot(args.focus_f_mm * 1e-3, args.w0_mm * 1e-3)
    spot_ideal = ideal.focal_spot(args.focus_f_mm * 1e-3, args.w0_mm * 1e-3)

    print("=" * 60)
    print(" Beam quality (M^2) analysis")
    print("=" * 60)
    print(f"  M^2                 : {args.m2:.2f}")
    print(f"  waist radius        : {args.w0_mm:.1f} mm")
    print(f"  far-field divergence: {bq.divergence*1e3:.3f} mrad "
          f"(ideal {ideal.divergence*1e3:.3f})")
    print(f"  beam-param product  : {bq.bpp*1e6:.2f} mm*mrad")
    print(f"  Rayleigh range      : {bq.rayleigh:.2f} m")
    print(f"  focal spot @ {args.focus_f_mm:.0f}mm : {spot*1e6:.1f} um "
          f"(ideal {spot_ideal*1e6:.1f} um)")
    print(f"  peak focal intensity: {args.power/(np.pi*spot**2)/1e4:.2e} W/cm^2")
    print(f"  brightness FOM      : {bq.brightness(args.power):.2e}")
    print("=" * 60)

    if _HAVE_MPL:
        z = np.linspace(-3 * bq.rayleigh, 3 * bq.rayleigh, 400)
        plt.figure(figsize=(8, 4.2))
        plt.plot(z, bq.width(z) * 1e3, lw=2, label=f"M^2={args.m2}")
        plt.plot(z, ideal.width(z) * 1e3, lw=2, ls="--", label="ideal (M^2=1)")
        plt.xlabel("z from waist [m]"); plt.ylabel("beam radius [mm]")
        plt.title("Real vs diffraction-limited beam expansion")
        plt.legend(); plt.tight_layout(); plt.savefig("beam_quality.png", dpi=130)
        print("Saved -> beam_quality.png")
        plt.show()


if __name__ == "__main__":
    main()
