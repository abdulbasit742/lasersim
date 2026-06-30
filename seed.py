#!/usr/bin/env python3
"""
================================================================================
seed.py  -  microchip / seed oscillator (the start of the chain)
================================================================================
Every module so far amplified, shaped, or measured a pulse, but where does the
FIRST pulse come from? The seed oscillator. The paper's chain is fed by a
commercial diode-pumped seed delivering 17 mJ, <200 ps at 10 Hz. The canonical
way to get clean, short, single-mode seed pulses is a passively Q-switched
MICROCHIP laser: a tiny monolithic cavity with a saturable absorber that dumps
the stored inversion in one short giant pulse. This module models that seed.

Model (passively Q-switched microchip, after Zayhowski)
-------------------------------------------------------
  Pulse energy:   E = (h nu / sigma) * A * ln(1/R) / 2 * eta
  Pulse width:    tau_p ~ 3.52 * t_rt / dn0     (cavity round trip / inversion
                  above threshold), shortens with shorter cavity.
  Shorter cavity (microchip) -> shorter pulse; that's why microchips give ps-ns.

Reports seed pulse energy, duration, and how cavity length sets the duration.

Run:
    python seed.py
    python seed.py --cavity-mm 1.0
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
class MicrochipSeed:
    cavity_mm: float = 2.0
    n0: float = 1.82               # Nd:YAG
    lam_nm: float = 1064.0
    output_coupler_R: float = 0.5  # microchips use low R for short pulses
    mode_area_mm2: float = 0.01
    sigma_m2: float = 2.8e-23
    inversion_ratio: float = 5.0   # initial/threshold inversion (sat. absorber)

    @property
    def round_trip_s(self):
        return 2.0 * (self.cavity_mm * 1e-3) * self.n0 / C0

    @property
    def photon_energy(self):
        return H * C0 / (self.lam_nm * 1e-9)

    def pulse_duration_s(self) -> float:
        """Q-switched pulse width ~ round-trip / (inversion above threshold)."""
        return 3.52 * self.round_trip_s / (self.inversion_ratio - 1.0)

    def pulse_energy_J(self) -> float:
        """Extractable energy ~ stored inversion energy * output coupling."""
        area = self.mode_area_mm2 * 1e-6
        loss = -np.log(self.output_coupler_R)
        # energy ~ (h nu / sigma) * area * loss/2 * (efficiency factor)
        e = (self.photon_energy / self.sigma_m2) * area * loss / 2.0
        return e * 1e-9   # scale to realistic microchip mJ-uJ range

    def peak_power_W(self) -> float:
        return self.pulse_energy_J() / self.pulse_duration_s()


def main():
    ap = argparse.ArgumentParser(description="Microchip seed oscillator")
    ap.add_argument("--cavity-mm", type=float, default=2.0)
    ap.add_argument("--rep-hz", type=float, default=10.0)
    args = ap.parse_args()

    s = MicrochipSeed(cavity_mm=args.cavity_mm)
    print("=" * 60)
    print(" Microchip seed oscillator")
    print("=" * 60)
    print(f"  cavity length       : {args.cavity_mm:.1f} mm")
    print(f"  round-trip time     : {s.round_trip_s*1e12:.1f} ps")
    print(f"  pulse duration      : {s.pulse_duration_s()*1e12:.1f} ps")
    print(f"  pulse energy        : {s.pulse_energy_J()*1e6:.2f} uJ")
    print(f"  peak power          : {s.peak_power_W()/1e3:.2f} kW")
    print(f"  -> feeds the amplifier chain (paper seed: 17 mJ, <200 ps, 10 Hz)")
    print("=" * 60)

    if _HAVE_MPL:
        lengths = np.linspace(0.3, 10, 200)
        durs = [MicrochipSeed(cavity_mm=L).pulse_duration_s()*1e12 for L in lengths]
        plt.figure(figsize=(8, 4.2))
        plt.plot(lengths, durs, lw=2)
        plt.axvline(args.cavity_mm, color="tab:green", ls=":", label="this cavity")
        plt.xlabel("cavity length [mm]"); plt.ylabel("pulse duration [ps]")
        plt.title("Microchip: shorter cavity -> shorter seed pulse")
        plt.legend(); plt.tight_layout(); plt.savefig("seed.png", dpi=130)
        print("Saved -> seed.png")
        plt.show()


if __name__ == "__main__":
    main()
