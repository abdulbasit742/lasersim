#!/usr/bin/env python3
"""
================================================================================
breakdown.py  -  laser-induced air breakdown at relay-telescope foci
================================================================================
The paper notes that at the focus of each relay telescope the intensity gets so
high it causes AIR BREAKDOWN (a spark/plasma), which wrecks the beam, so they
put the focus inside a VACUUM TUBE pumped to 6.5e-4 mbar. This module models
that: it computes the focal intensity, compares it to the air-breakdown
threshold (which rises as pressure drops), and tells you the maximum pressure
you can tolerate, i.e. how hard you must pump the vacuum relay.

Model
-----
  Focal intensity:  I = P / (pi w_focus^2)
  Air breakdown threshold scales inversely with pressure (roughly):
      I_th(p) ~ I_th(1 atm) * (p_atm / p)
  Breakdown when I >= I_th(p). Solve for the pressure that keeps I < I_th.

Run:
    python breakdown.py
    python breakdown.py --power 6.4e9 --focus-um 30
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

P_ATM_MBAR = 1013.25
# representative air breakdown threshold at 1 atm for ~100 ps, 1064 nm
I_BREAKDOWN_1ATM_Wcm2 = 2e11


@dataclass
class FocusBreakdown:
    peak_power_W: float = 6.4e9
    focus_radius_um: float = 30.0
    i_th_1atm: float = I_BREAKDOWN_1ATM_Wcm2

    def focal_intensity_Wcm2(self) -> float:
        area_cm2 = np.pi * (self.focus_radius_um * 1e-4) ** 2
        return self.peak_power_W / area_cm2

    def threshold_at_pressure(self, p_mbar: float) -> float:
        """Breakdown threshold rises as pressure drops (fewer molecules)."""
        return self.i_th_1atm * (P_ATM_MBAR / max(p_mbar, 1e-9))

    def breaks_down(self, p_mbar: float) -> bool:
        return self.focal_intensity_Wcm2() >= self.threshold_at_pressure(p_mbar)

    def max_safe_pressure_mbar(self) -> float:
        """Highest pressure that keeps focal intensity below breakdown."""
        I = self.focal_intensity_Wcm2()
        if I <= 0:
            return P_ATM_MBAR
        return self.i_th_1atm * P_ATM_MBAR / I


def main():
    ap = argparse.ArgumentParser(description="Air breakdown at relay foci")
    ap.add_argument("--power", type=float, default=6.4e9, help="peak power [W]")
    ap.add_argument("--focus-um", type=float, default=30.0)
    args = ap.parse_args()

    fb = FocusBreakdown(peak_power_W=args.power, focus_radius_um=args.focus_um)
    I = fb.focal_intensity_Wcm2()
    p_max = fb.max_safe_pressure_mbar()

    print("=" * 60)
    print(" Air breakdown at relay-telescope focus")
    print("=" * 60)
    print(f"  peak power          : {args.power/1e9:.2f} GW")
    print(f"  focal spot radius   : {args.focus_um:.0f} um")
    print(f"  focal intensity     : {I:.2e} W/cm^2")
    print(f"  breakdown @ 1 atm   : {'YES' if fb.breaks_down(P_ATM_MBAR) else 'no'}")
    print(f"  max safe pressure   : {p_max:.2e} mbar")
    print(f"  paper vacuum level  : 6.5e-4 mbar ({'sufficient' if 6.5e-4 < p_max else 'insufficient'})")
    print("=" * 60)

    if _HAVE_MPL:
        ps = np.logspace(-5, 3.1, 200)
        th = [fb.threshold_at_pressure(p) for p in ps]
        plt.figure(figsize=(8, 4.2))
        plt.loglog(ps, th, lw=2, label="breakdown threshold")
        plt.axhline(I, color="tab:green", ls="--", label="focal intensity")
        plt.axvline(p_max, color="r", ls=":", label=f"max safe {p_max:.1e} mbar")
        plt.xlabel("pressure [mbar]"); plt.ylabel("intensity [W/cm^2]")
        plt.title("Air-breakdown threshold vs pressure")
        plt.legend(); plt.tight_layout(); plt.savefig("breakdown.png", dpi=130)
        print("Saved -> breakdown.png")
        plt.show()


if __name__ == "__main__":
    main()
