#!/usr/bin/env python3
"""
================================================================================
cooling.py  -  coolant flow & convective heat removal at the rod barrel
================================================================================
thermal_fem.py assumed a fixed coolant temperature at the rod surface. But that
surface temperature isn't free: it depends on how fast water flows past the
barrel and how good the convective heat transfer is. The paper uses a 2.5 kW
chiller at >8 L/min. This module closes that gap: it models the coolant side,
turning flow rate into a convective film coefficient (via Dittus-Boelter) and
then into the actual rod-wall temperature for a given heat load.

Model
-----
  Reynolds:   Re = rho u D / mu
  Nusselt:    Nu = 0.023 Re^0.8 Pr^0.4         (Dittus-Boelter, turbulent)
  Film coeff: h  = Nu k_water / D
  Wall rise:  dT = q'' / h                      (q'' = heat flux at barrel)

Reports the flow regime, film coefficient, barrel-wall temperature rise, and the
minimum flow rate needed to keep the wall within budget.

Run:
    python cooling.py
    python cooling.py --flow-lpm 8 --heat-W 200
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

# water properties near 25 C
RHO = 997.0          # kg/m^3
MU = 8.9e-4          # Pa s
K_WATER = 0.606      # W/(m K)
CP = 4180.0          # J/(kg K)
PR = MU * CP / K_WATER


@dataclass
class CoolingChannel:
    rod_diameter_m: float = 15e-3
    rod_length_m: float = 0.13
    annulus_gap_m: float = 1.0e-3      # cooling annulus thickness

    @property
    def hydraulic_D(self) -> float:
        # annulus hydraulic diameter ~ 2 * gap
        return 2.0 * self.annulus_gap_m

    @property
    def flow_area(self) -> float:
        return np.pi * self.rod_diameter_m * self.annulus_gap_m

    @property
    def barrel_area(self) -> float:
        return np.pi * self.rod_diameter_m * self.rod_length_m

    def velocity(self, flow_lpm: float) -> float:
        q_m3s = flow_lpm / 1000.0 / 60.0
        return q_m3s / self.flow_area

    def reynolds(self, flow_lpm: float) -> float:
        return RHO * self.velocity(flow_lpm) * self.hydraulic_D / MU

    def film_coeff(self, flow_lpm: float) -> float:
        Re = self.reynolds(flow_lpm)
        Nu = 0.023 * Re ** 0.8 * PR ** 0.4 if Re > 2300 else 4.36  # turb / laminar
        return Nu * K_WATER / self.hydraulic_D

    def wall_rise(self, flow_lpm: float, heat_W: float) -> float:
        q_flux = heat_W / self.barrel_area
        return q_flux / self.film_coeff(flow_lpm)

    def min_flow_for_budget(self, heat_W: float, max_rise_K: float) -> float:
        for f in np.linspace(0.5, 30.0, 600):
            if self.wall_rise(f, heat_W) <= max_rise_K:
                return f
        return float("inf")


def main():
    ap = argparse.ArgumentParser(description="Rod coolant convective model")
    ap.add_argument("--flow-lpm", type=float, default=8.0)
    ap.add_argument("--heat-W", type=float, default=200.0)
    ap.add_argument("--max-rise", type=float, default=20.0)
    args = ap.parse_args()

    ch = CoolingChannel()
    Re = ch.reynolds(args.flow_lpm)
    regime = "turbulent" if Re > 2300 else "laminar"
    h = ch.film_coeff(args.flow_lpm)
    rise = ch.wall_rise(args.flow_lpm, args.heat_W)
    f_min = ch.min_flow_for_budget(args.heat_W, args.max_rise)

    print("=" * 60)
    print(" Rod barrel cooling (convective)")
    print("=" * 60)
    print(f"  flow rate          : {args.flow_lpm:.1f} L/min")
    print(f"  coolant velocity   : {ch.velocity(args.flow_lpm):.2f} m/s")
    print(f"  Reynolds number    : {Re:.0f} ({regime})")
    print(f"  film coefficient   : {h:.0f} W/(m^2 K)")
    print(f"  heat load          : {args.heat_W:.0f} W")
    print(f"  wall temp rise     : {rise:.1f} K")
    print(f"  min flow for {args.max_rise:.0f} K : {f_min:.1f} L/min")
    print(f"  (paper: >8 L/min, 2.5 kW chiller)")
    print("=" * 60)

    if _HAVE_MPL:
        flows = np.linspace(1, 20, 200)
        rises = [ch.wall_rise(f, args.heat_W) for f in flows]
        plt.figure(figsize=(8, 4.2))
        plt.plot(flows, rises, lw=2)
        plt.axhline(args.max_rise, color="r", ls="--", label="budget")
        plt.axvline(8, color="tab:green", ls=":", label="paper 8 L/min")
        plt.xlabel("flow rate [L/min]"); plt.ylabel("wall temp rise [K]")
        plt.title("Barrel wall temperature vs coolant flow")
        plt.legend(); plt.tight_layout(); plt.savefig("cooling.png", dpi=130)
        print("Saved -> cooling.png")
        plt.show()


if __name__ == "__main__":
    main()
