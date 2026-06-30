#!/usr/bin/env python3
"""
================================================================================
ranging.py  -  laser-ranging link budget & range precision
================================================================================
The paper lists satellite/lunar laser ranging as a target application. Ranging
fires a short pulse at a distant retroreflector and times the return. The key
question is the LINK BUDGET: of the billions of photons sent, how many come
back? And given that, how precisely can you measure the range? This module is
the radar-equation analogue for photon-counting laser ranging.

Model (one-way * two-way, simplified)
-------------------------------------
  Photons sent      = E_pulse / (h nu)
  Beam spreads      over solid angle ~ (theta_div)^2 at range R
  Hit target area   A_t -> fraction collected by retroreflector
  Return spreads    back over the retro's diffraction cone
  Collected by RX   aperture A_rx, times atmospheric T^2 and efficiencies
  Range precision   sigma_R = c * tau_pulse / (2 sqrt(N_return))

Reports photons transmitted, mean photons returned per shot, and the resulting
single-shot range precision.

Run:
    python ranging.py
    python ranging.py --range-km 1000 --energy-mJ 1280
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

C0 = 2.99792458e8
H = 6.62607015e-34


@dataclass
class RangingLink:
    energy_J: float = 1.28
    pulse_ps: float = 200.0
    lam_nm: float = 1064.0
    div_urad: float = 10.0          # transmit divergence (half-angle)
    retro_area_m2: float = 0.5      # effective retroreflector array area
    rx_diameter_m: float = 1.0      # receiver telescope aperture
    atmos_transmission: float = 0.7 # one-way
    optics_eff: float = 0.5         # combined TX+RX optical efficiency
    detector_qe: float = 0.2        # photon-counting detector QE

    @property
    def photon_energy(self):
        return H * C0 / (self.lam_nm * 1e-9)

    def photons_sent(self):
        return self.energy_J / self.photon_energy

    def photons_returned(self, range_m: float):
        # outgoing beam footprint area at the target
        spot_area = np.pi * (self.div_urad * 1e-6 * range_m) ** 2
        frac_on_retro = min(self.retro_area_m2 / spot_area, 1.0)
        # return beam diffraction spread from the retro (lambda/D_retro)
        retro_D = np.sqrt(self.retro_area_m2)
        return_div = self.lam_nm * 1e-9 / retro_D
        return_area = np.pi * (return_div * range_m) ** 2
        frac_on_rx = min((np.pi * (self.rx_diameter_m / 2) ** 2) / return_area, 1.0)
        n = (self.photons_sent() * frac_on_retro * frac_on_rx
             * self.atmos_transmission ** 2 * self.optics_eff * self.detector_qe)
        return n

    def range_precision_m(self, range_m: float):
        n = self.photons_returned(range_m)
        single_shot = C0 * (self.pulse_ps * 1e-12) / 2.0
        return single_shot / np.sqrt(n) if n > 0 else float("inf")


def main():
    ap = argparse.ArgumentParser(description="Laser-ranging link budget")
    ap.add_argument("--range-km", type=float, default=1000.0)
    ap.add_argument("--energy-mJ", type=float, default=1280.0)
    ap.add_argument("--div-urad", type=float, default=10.0)
    args = ap.parse_args()

    link = RangingLink(energy_J=args.energy_mJ / 1e3, div_urad=args.div_urad)
    R = args.range_km * 1e3
    sent = link.photons_sent()
    ret = link.photons_returned(R)
    prec = link.range_precision_m(R)

    print("=" * 60)
    print(" Laser-ranging link budget")
    print("=" * 60)
    print(f"  pulse energy        : {args.energy_mJ:.0f} mJ @ {link.pulse_ps:.0f} ps")
    print(f"  range               : {args.range_km:.0f} km")
    print(f"  photons sent        : {sent:.2e}")
    print(f"  photons returned    : {ret:.2e} per shot")
    print(f"  single-shot precision: {prec*100:.1f} cm")
    if ret >= 1:
        print(f"  -> photon-counting regime: average {ret:.1f} returns/shot")
    else:
        print(f"  -> need ~{int(np.ceil(1/ret))} shots for one return photon")
    print("=" * 60)

    if _HAVE_MPL:
        ranges = np.linspace(200e3, 400000e3, 200)
        rets = [link.photons_returned(R) for R in ranges]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(ranges / 1e3, rets, lw=2)
        plt.axhline(1.0, color="r", ls="--", label="1 photon/shot")
        plt.xlabel("range [km]"); plt.ylabel("photons returned / shot")
        plt.title("Laser-ranging return vs range")
        plt.legend(); plt.tight_layout(); plt.savefig("ranging.png", dpi=130)
        print("Saved -> ranging.png")
        plt.show()


if __name__ == "__main__":
    main()
