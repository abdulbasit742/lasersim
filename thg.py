#!/usr/bin/env python3
"""
================================================================================
thg.py  -  third-harmonic generation: 1064 nm -> 355 nm (UV)
================================================================================
Green (532 nm, see shg.py) can be mixed with the leftover fundamental (1064 nm)
in a second crystal to make ultraviolet at 355 nm: this is SUM-FREQUENCY
generation, 1064 + 532 -> 355. UV ps pulses are used for micromachining,
photolithography, and pumping shorter-wavelength parametric stages.

The two-crystal THG chain:
   crystal 1 (SHG):  1064 -> 532   (efficiency from shg.py)
   crystal 2 (SFG):  1064 + 532 -> 355
Maximum THG efficiency needs the SHG stage tuned to ~ the optimum green
fraction (classically ~ 1/3 of the fundamental into green) so the SFG stage has
matched photon numbers of red and green.

Run:
    python thg.py
    python thg.py --energy-J 1.28 --tau-ps 200
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

from shg import SHGCrystal, peak_intensity


@dataclass
class SFGCrystal:
    """Sum-frequency crystal mixing 1064 + 532 -> 355 nm."""
    name: str = "LBO"
    length_mm: float = 10.0
    deff_pm_V: float = 0.82
    n: float = 1.60

    def sfg_efficiency(self, I_red, I_green):
        """Photon-limited SFG conversion. Efficiency peaks when red/green photon
        flux are matched; modeled as a saturating product of both intensities."""
        # normalized drive ~ sqrt(I_red * I_green) * deff * L
        L = self.length_mm * 1e-3
        deff = self.deff_pm_V * 1e-12
        drive = (deff * L) * np.sqrt(max(I_red, 0.0) * max(I_green, 0.0)) * 3.0e-6
        return float(np.tanh(drive) ** 2)


def thg_chain(energy_J, tau_s, radius_cm, green_fraction=None):
    """Run SHG then SFG. If green_fraction given, force the SHG split; else use
    the shg.py physical efficiency."""
    I_fund = peak_intensity(energy_J, tau_s, radius_cm)
    shg = SHGCrystal(beam_radius_cm=radius_cm)
    if green_fraction is None:
        eta_shg = shg.efficiency(I_fund)
    else:
        eta_shg = green_fraction
    e_green = eta_shg * energy_J
    e_red_left = (1.0 - eta_shg) * energy_J

    I_green = peak_intensity(e_green, tau_s, radius_cm)
    I_red = peak_intensity(e_red_left, tau_s, radius_cm)

    sfg = SFGCrystal()
    eta_sfg = sfg.sfg_efficiency(I_red, I_green)
    # UV energy limited by the smaller of the two input energies (photon match)
    e_uv = eta_sfg * min(e_green + e_red_left, 2.0 * min(e_green, e_red_left))
    return {"eta_shg": eta_shg, "e_green_mJ": e_green * 1e3,
            "e_red_left_mJ": e_red_left * 1e3, "eta_sfg": eta_sfg,
            "e_uv_mJ": e_uv * 1e3, "thg_overall": e_uv / energy_J}


def main():
    ap = argparse.ArgumentParser(description="Third-harmonic generation 1064->355")
    ap.add_argument("--energy-J", type=float, default=1.28)
    ap.add_argument("--tau-ps", type=float, default=200.0)
    ap.add_argument("--radius-cm", type=float, default=0.8)
    args = ap.parse_args()

    r = thg_chain(args.energy_J, args.tau_ps * 1e-12, args.radius_cm)

    print("=" * 60)
    print(" Third-harmonic generation: 1064 -> 355 nm (UV)")
    print("=" * 60)
    print(f"  fundamental        : {args.energy_J*1e3:.0f} mJ @ {args.tau_ps:.0f} ps")
    print(f"  SHG (1064->532)    : {r['eta_shg']*100:.1f}% -> {r['e_green_mJ']:.0f} mJ green")
    print(f"  red left over      : {r['e_red_left_mJ']:.0f} mJ")
    print(f"  SFG (1064+532->355): {r['eta_sfg']*100:.1f}%")
    print(f"  UV output (355 nm) : {r['e_uv_mJ']:.0f} mJ")
    print(f"  overall THG eff.   : {r['thg_overall']*100:.1f}%")
    print("=" * 60)

    if _HAVE_MPL:
        fracs = np.linspace(0.05, 0.8, 100)
        uv = [thg_chain(args.energy_J, args.tau_ps*1e-12, args.radius_cm, f)["e_uv_mJ"]
              for f in fracs]
        plt.figure(figsize=(8, 4.2))
        plt.plot(fracs * 100, uv, lw=2)
        plt.xlabel("green fraction from SHG [%]"); plt.ylabel("UV output [mJ]")
        plt.title("THG: UV yield vs SHG split (optimum ~1/3 green)")
        plt.tight_layout(); plt.savefig("thg.png", dpi=130)
        print("Saved -> thg.png")
        plt.show()


if __name__ == "__main__":
    main()
