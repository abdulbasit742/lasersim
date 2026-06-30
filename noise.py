#!/usr/bin/env python3
"""
================================================================================
noise.py  -  relative intensity noise (RIN) & shot-noise floor
================================================================================
The paper's 1.1% RMS energy stability (and jitter.py, sensitivity.py) all live
on top of a deeper question: what is the FUNDAMENTAL noise floor, and how does
pump noise transfer to the output? Every laser has:
  * a SHOT-NOISE floor set by photon statistics (sqrt(N)/N),
  * technical RIN from pump-current ripple and vibration, and
  * a pump-to-output transfer that the relaxation-oscillation resonance can
    AMPLIFY noise near its resonant frequency.
This module models the RIN spectrum, the shot-noise limit, and how pump RIN maps
to output RIN through the laser's transfer function.

Model
-----
  Shot-noise RIN:  RIN_shot = 1 / N_photons  (per Hz, white)
  Pump transfer:   |H(f)|^2 with a relaxation-oscillation peak at f_relax
  Output RIN(f) = pump_RIN * |H(f)|^2 + shot-noise floor

Reports the shot-noise floor, integrated RMS, and the resonant amplification.

Run:
    python noise.py
    python noise.py --pump-rin-db -120 --f-relax-khz 50
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
class NoiseModel:
    photons_per_pulse: float = 1e17
    pump_rin_dbc_hz: float = -120.0     # pump relative intensity noise [dBc/Hz]
    f_relax_khz: float = 50.0           # relaxation-oscillation frequency
    damping: float = 0.1                # resonance damping ratio

    def shot_noise_rin(self) -> float:
        """White shot-noise RIN level [1/Hz]."""
        return 1.0 / self.photons_per_pulse

    def transfer(self, f_hz):
        """Pump-to-output transfer |H(f)|^2 with relaxation resonance."""
        f0 = self.f_relax_khz * 1e3
        x = f_hz / f0
        return 1.0 / ((1 - x ** 2) ** 2 + (2 * self.damping * x) ** 2)

    def output_rin(self, f_hz):
        pump_lin = 10 ** (self.pump_rin_dbc_hz / 10.0)
        return pump_lin * self.transfer(f_hz) + self.shot_noise_rin()

    def peak_amplification_dB(self) -> float:
        return 10 * np.log10(self.transfer(self.f_relax_khz * 1e3))


def main():
    ap = argparse.ArgumentParser(description="Laser RIN / noise model")
    ap.add_argument("--pump-rin-db", type=float, default=-120.0)
    ap.add_argument("--f-relax-khz", type=float, default=50.0)
    args = ap.parse_args()

    nm = NoiseModel(pump_rin_dbc_hz=args.pump_rin_db, f_relax_khz=args.f_relax_khz)
    shot = nm.shot_noise_rin()

    print("=" * 60)
    print(" Laser intensity noise (RIN)")
    print("=" * 60)
    print(f"  photons / pulse     : {nm.photons_per_pulse:.1e}")
    print(f"  shot-noise RIN      : {10*np.log10(shot):.1f} dBc/Hz (white floor)")
    print(f"  pump RIN            : {args.pump_rin_db:.0f} dBc/Hz")
    print(f"  relaxation freq     : {args.f_relax_khz:.0f} kHz")
    print(f"  resonant amplification: {nm.peak_amplification_dB():.1f} dB at f_relax")
    print("=" * 60)
    print("  Pump noise near the relaxation resonance is amplified onto output.")
    print("=" * 60)

    if _HAVE_MPL:
        f = np.logspace(2, 7, 400)
        rin = [10 * np.log10(nm.output_rin(ff)) for ff in f]
        plt.figure(figsize=(8, 4.2))
        plt.semilogx(f, rin, lw=2, label="output RIN")
        plt.axhline(10 * np.log10(shot), color="r", ls="--", label="shot-noise floor")
        plt.axvline(args.f_relax_khz * 1e3, color="tab:green", ls=":", label="relaxation freq")
        plt.xlabel("frequency [Hz]"); plt.ylabel("RIN [dBc/Hz]")
        plt.title("Relative intensity noise spectrum")
        plt.legend(); plt.tight_layout(); plt.savefig("noise.png", dpi=130)
        print("Saved -> noise.png")
        plt.show()


if __name__ == "__main__":
    main()
