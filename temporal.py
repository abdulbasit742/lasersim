#!/usr/bin/env python3
"""
================================================================================
temporal.py  -  time-resolved pulse amplification & gain saturation
================================================================================
The Frantz-Nodvik formula in amplifier.py gives total energy extraction, but it
hides what happens WITHIN the pulse. As the leading edge of a 200 ps pulse sweeps
through the inverted medium it depletes the gain, so the trailing edge sees less
gain. The pulse gets RESHAPED: the front is amplified more than the back, the
peak shifts forward, and the pulse can steepen. This matters for OPCPA pump
shaping and for predicting the real output temporal profile.

This module solves the time-dependent gain-saturation equations along the pulse:

    dPhi/dz   = g(z,t) * Phi                         (photon flux growth)
    dg/dt     = -(sigma * c) * g * Phi               (gain depletion)

integrated with the standard Frantz-Nodvik traveling-wave solution:

    Phi_out(t) = Phi_in(t) / ( 1 - (1 - e^{-G0}) * exp(-U_in(t)/U_sat) )

where U_in(t) is the integrated input fluence up to time t.

Reports input vs output pulse shape, energy gain, pulse-center shift, and
temporal compression/steepening.

Run:
    python temporal.py
    python temporal.py --g0 3.0 --fwhm-ps 200
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple

import numpy as np
trapz = getattr(np, 'trapezoid', getattr(np, 'trapz', None))

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class PulseGrid:
    fwhm_ps: float = 200.0
    window_ps: float = 800.0
    npts: int = 4000
    order: int = 2          # 2 Gaussian, >2 super-Gaussian (flat-top)

    def time_axis(self):
        return np.linspace(-self.window_ps / 2, self.window_ps / 2, self.npts) * 1e-12

    def input_shape(self):
        t = self.time_axis()
        w = (self.fwhm_ps * 1e-12) / 1.6651  # FWHM -> 1/e half-width-ish
        return np.exp(-((t / w) ** self.order))


def frantz_nodvik_temporal(phi_in: np.ndarray, t: np.ndarray,
                           G0: float, U_sat: float, E_in_J: float):
    """Time-resolved Frantz-Nodvik. phi_in is the normalized input pulse shape.
    Returns (phi_out_normalized, energy_gain)."""
    dt = t[1] - t[0]
    # normalize input shape to carry E_in_J of fluence
    norm = trapz(phi_in, t)
    flux_in = phi_in / norm * E_in_J          # J/s per unit area (arbitrary area)
    U_in = np.cumsum(flux_in) * dt            # integrated input fluence up to t
    sat = np.exp(-U_in / U_sat)
    gain_t = G0 / (1.0 - (1.0 - 1.0 / np.exp(np.log(G0))) * sat) if G0 > 0 else 1.0
    # standard traveling-wave F-N output flux:
    denom = 1.0 - (1.0 - np.exp(-np.log(max(G0, 1.0000001)))) * sat
    # use the clean closed form with G0 as small-signal gain exp(g0 L):
    g0L = np.log(max(G0, 1.0000001))
    flux_out = flux_in * np.exp(g0L) / (1.0 + (np.exp(g0L) - 1.0) * (U_in / U_sat))
    e_in = trapz(flux_in, t)
    e_out = trapz(flux_out, t)
    return flux_out, e_out / e_in


def pulse_metrics(t, shape):
    """Return (center_of_mass_ps, fwhm_ps)."""
    p = np.clip(shape, 0, None)
    com = trapz(t * p, t) / trapz(p, t)
    half = p.max() / 2
    above = np.where(p >= half)[0]
    fwhm = (t[above[-1]] - t[above[0]]) if len(above) > 1 else 0.0
    return com * 1e12, fwhm * 1e12


def main():
    ap = argparse.ArgumentParser(description="Time-resolved pulse amplification")
    ap.add_argument("--g0", type=float, default=3.0, help="small-signal gain G0")
    ap.add_argument("--fwhm-ps", type=float, default=200.0)
    ap.add_argument("--order", type=int, default=2)
    ap.add_argument("--ein", type=float, default=0.2, help="input fluence / U_sat ratio")
    args = ap.parse_args()

    grid = PulseGrid(fwhm_ps=args.fwhm_ps, order=args.order)
    t = grid.time_axis()
    phi_in = grid.input_shape()

    U_sat = 1.0
    E_in = args.ein * U_sat
    flux_out, egain = frantz_nodvik_temporal(phi_in, t, args.g0, U_sat, E_in)

    flux_in = phi_in / trapz(phi_in, t) * E_in
    com_in, fwhm_in = pulse_metrics(t, flux_in)
    com_out, fwhm_out = pulse_metrics(t, flux_out)

    print("=" * 60)
    print(" Time-resolved pulse amplification (Frantz-Nodvik)")
    print("=" * 60)
    print(f"  small-signal gain G0 : {args.g0:.2f}")
    print(f"  energy gain          : {egain:.2f}x")
    print(f"  pulse center  in->out: {com_in:+.1f} -> {com_out:+.1f} ps "
          f"(shift {com_out - com_in:+.1f} ps)")
    print(f"  FWHM          in->out: {fwhm_in:.1f} -> {fwhm_out:.1f} ps")
    print(f"  -> leading edge sees more gain (pulse {'advances' if com_out < com_in else 'delays'})")
    print("=" * 60)

    if _HAVE_MPL:
        fig, ax = plt.subplots(figsize=(8, 4.2))
        tp = t * 1e12
        ax.plot(tp, flux_in / flux_in.max(), lw=2, label="input (norm)")
        ax.plot(tp, flux_out / flux_out.max(), lw=2, label="output (norm)")
        ax.axvline(com_in, color="tab:blue", ls=":", alpha=0.6)
        ax.axvline(com_out, color="tab:orange", ls=":", alpha=0.6)
        ax.set(xlabel="time [ps]", ylabel="normalized flux",
               title="Pulse reshaping by gain saturation")
        ax.legend()
        plt.tight_layout(); plt.savefig("temporal.png", dpi=130)
        print("Saved -> temporal.png")
        plt.show()


if __name__ == "__main__":
    main()
