#!/usr/bin/env python3
"""
================================================================================
pockels.py  -  Pockels-cell pulse picker / switch
================================================================================
A Pockels cell is the fast electro-optic switch that selects ONE pulse from the
oscillator train and gates it into the amplifier (and switches the regen dump,
and gates ASE in contrast.py). Apply the half-wave voltage and the cell rotates
polarization 90 deg so a polarizer transmits the pulse; off-voltage and it's
blocked. Two real limits: the finite HIGH VOLTAGE you must supply, and the
finite EXTINCTION RATIO that lets neighbouring pulses leak through. This module
models both.

Model
-----
  Half-wave voltage:  V_pi = lambda d / (2 n^3 r63 L)   (longitudinal-ish)
  Transmission:       T(V) = sin^2( pi/2 * V / V_pi )
  Extinction ratio:   ER = T(V_pi) / T(0)
  Neighbour leakage:  fraction of adjacent train pulses passed within the
                      finite electrical switching window.

Run:
    python pockels.py
    python pockels.py --voltage 3200 --rep-mhz 100
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
class PockelsCell:
    lam_nm: float = 1064.0
    aperture_mm: float = 8.0          # d, electrode spacing
    length_mm: float = 25.0           # L, crystal length
    n0: float = 1.51                  # KD*P index
    r63_pm_V: float = 26.4            # electro-optic coefficient [pm/V]
    static_extinction: float = 1e-3   # residual leakage at 0 V (crystal quality)
    switch_window_ns: float = 6.0      # electrical on-time window

    def half_wave_voltage(self) -> float:
        lam = self.lam_nm * 1e-9
        r63 = self.r63_pm_V * 1e-12
        d = self.aperture_mm * 1e-3
        L = self.length_mm * 1e-3
        return lam * d / (2.0 * self.n0 ** 3 * r63 * L)

    def transmission(self, V: float) -> float:
        Vpi = self.half_wave_voltage()
        return np.sin(np.pi / 2.0 * V / Vpi) ** 2 + self.static_extinction

    def extinction_ratio(self) -> float:
        return self.transmission(self.half_wave_voltage()) / self.transmission(0.0)

    def neighbour_leakage(self, rep_mhz: float) -> int:
        """Number of adjacent train pulses that fall inside the switch window."""
        spacing_ns = 1e3 / rep_mhz
        return int(self.switch_window_ns / spacing_ns)


def main():
    ap = argparse.ArgumentParser(description="Pockels-cell pulse picker")
    ap.add_argument("--voltage", type=float, default=None, help="applied voltage [V]")
    ap.add_argument("--rep-mhz", type=float, default=100.0, help="oscillator rep rate")
    args = ap.parse_args()

    pc = PockelsCell()
    Vpi = pc.half_wave_voltage()
    V = args.voltage if args.voltage is not None else Vpi

    print("=" * 60)
    print(" Pockels-cell pulse picker")
    print("=" * 60)
    print(f"  half-wave voltage Vpi : {Vpi:.0f} V")
    print(f"  applied voltage       : {V:.0f} V")
    print(f"  transmission          : {pc.transmission(V)*100:.1f} %")
    print(f"  extinction ratio      : {pc.extinction_ratio():.0f} : 1")
    print(f"  switch window         : {pc.switch_window_ns:.1f} ns")
    print(f"  neighbour leakage     : {pc.neighbour_leakage(args.rep_mhz)} adjacent pulses "
          f"(@ {args.rep_mhz:.0f} MHz)")
    print("=" * 60)

    if _HAVE_MPL:
        Vs = np.linspace(0, 1.5 * Vpi, 300)
        T = [pc.transmission(v) for v in Vs]
        plt.figure(figsize=(8, 4.2))
        plt.plot(Vs, T, lw=2)
        plt.axvline(Vpi, color="r", ls="--", label="V_pi (full transmission)")
        plt.xlabel("applied voltage [V]"); plt.ylabel("transmission")
        plt.title("Pockels-cell transmission vs voltage")
        plt.legend(); plt.tight_layout(); plt.savefig("pockels.png", dpi=130)
        print("Saved -> pockels.png")
        plt.show()


if __name__ == "__main__":
    main()
