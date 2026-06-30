#!/usr/bin/env python3
"""
================================================================================
beam_combining.py  -  coherent & spectral beam combining
================================================================================
One rod can only store so much before ASE/damage cap it (see ase.py, damage.py).
The way past that ceiling is to run N amplifier channels in parallel and COMBINE
their outputs. Two flavours:
  * COHERENT combining: lock all channels to the same phase and interfere them
    into one beam. Efficiency falls with residual phase error (piston) between
    channels.
  * SPECTRAL combining: give each channel a slightly different wavelength and
    overlap them with a grating; near-lossless but needs bandwidth.
This module models the combining efficiency and how many channels you need to
scale the 1.28 J system to a target energy.

Model
-----
  Coherent efficiency:  eta = exp(-sigma_phi^2)  (sigma_phi = RMS phase error, rad)
  N-channel combined energy = N * E_channel * eta
  Channels needed for target E_t: N = ceil(E_t / (E_channel * eta))

Run:
    python beam_combining.py
    python beam_combining.py --channels 8 --phase-err 0.3
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
class BeamCombiner:
    channel_energy_J: float = 1.28
    mode: str = "coherent"          # "coherent" or "spectral"
    phase_err_rad: float = 0.2      # RMS residual piston phase error
    spectral_eff: float = 0.95      # grating combiner efficiency

    def efficiency(self) -> float:
        if self.mode == "spectral":
            return self.spectral_eff
        return float(np.exp(-self.phase_err_rad ** 2))

    def combined_energy_J(self, n_channels: int) -> float:
        return n_channels * self.channel_energy_J * self.efficiency()

    def channels_for_target(self, target_J: float) -> int:
        per = self.channel_energy_J * self.efficiency()
        return int(np.ceil(target_J / per)) if per > 0 else 0


def main():
    ap = argparse.ArgumentParser(description="Coherent/spectral beam combining")
    ap.add_argument("--channels", type=int, default=8)
    ap.add_argument("--phase-err", type=float, default=0.2, help="RMS phase error [rad]")
    ap.add_argument("--mode", choices=["coherent", "spectral"], default="coherent")
    ap.add_argument("--target-J", type=float, default=10.0)
    args = ap.parse_args()

    bc = BeamCombiner(mode=args.mode, phase_err_rad=args.phase_err)
    eta = bc.efficiency()
    combined = bc.combined_energy_J(args.channels)
    n_needed = bc.channels_for_target(args.target_J)

    print("=" * 60)
    print(f" Beam combining ({args.mode})")
    print("=" * 60)
    print(f"  channel energy      : {bc.channel_energy_J*1e3:.0f} mJ")
    print(f"  combining mode      : {args.mode}")
    if args.mode == "coherent":
        print(f"  RMS phase error     : {args.phase_err:.2f} rad")
    print(f"  combining efficiency: {eta*100:.1f} %")
    print(f"  {args.channels} channels combined : {combined*1e3:.0f} mJ ({combined:.2f} J)")
    print(f"  channels for {args.target_J:.0f} J  : {n_needed}")
    print("=" * 60)

    if _HAVE_MPL:
        errs = np.linspace(0, 1.5, 200)
        effs = [np.exp(-e ** 2) * 100 for e in errs]
        plt.figure(figsize=(8, 4.2))
        plt.plot(errs, effs, lw=2)
        plt.axvline(args.phase_err, color="tab:green", ls=":", label="operating")
        plt.axhline(90, color="r", ls="--", label="90% (lambda/20 rms)")
        plt.xlabel("RMS phase error [rad]"); plt.ylabel("coherent combining eff [%]")
        plt.title("Coherent combining efficiency vs phase error")
        plt.legend(); plt.tight_layout(); plt.savefig("beam_combining.png", dpi=130)
        print("Saved -> beam_combining.png")
        plt.show()


if __name__ == "__main__":
    main()
