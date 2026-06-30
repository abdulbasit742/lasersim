#!/usr/bin/env python3
"""
================================================================================
autocorrelation.py  -  intensity autocorrelation pulse diagnostic
================================================================================
How do you actually MEASURE a 200 ps pulse? No electronic detector is fast
enough. The standard answer is an intensity autocorrelator: split the pulse,
delay one copy, overlap both in an SHG crystal, and record the second-harmonic
signal vs delay. The autocorrelation trace is wider than the pulse by a known
'deconvolution factor' that depends on the pulse shape, so you divide it out to
get the real duration. The paper quotes <200 ps FWHM; this is the tool behind
that number.

Model
-----
  Intensity autocorrelation: A(tau) = integral I(t) I(t - tau) dt.
  Deconvolution factors (AC FWHM / pulse FWHM):
      Gaussian   : 1.414
      sech^2     : 1.543
      Lorentzian : 2.000

Reports the autocorrelation FWHM, the inferred pulse duration for an assumed
shape, and how shape assumption changes the answer.

Run:
    python autocorrelation.py
    python autocorrelation.py --pulse-ps 200 --shape sech2
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

DECONV = {"gaussian": 1.414, "sech2": 1.543, "lorentzian": 2.000}


@dataclass
class Autocorrelator:
    pulse_fwhm_ps: float = 200.0
    shape: str = "gaussian"
    window_ps: float = 1200.0
    npts: int = 6000

    def time_axis(self):
        return np.linspace(-self.window_ps / 2, self.window_ps / 2, self.npts)

    def pulse(self, t):
        if self.shape == "gaussian":
            w = self.pulse_fwhm_ps / 1.6651
            return np.exp(-(t / w) ** 2)
        if self.shape == "sech2":
            w = self.pulse_fwhm_ps / 1.7627
            return 1.0 / np.cosh(t / w) ** 2
        if self.shape == "lorentzian":
            w = self.pulse_fwhm_ps / 2.0
            return 1.0 / (1.0 + (t / w) ** 2)
        raise ValueError(f"unknown shape '{self.shape}'")

    def trace(self):
        """Numeric intensity autocorrelation via FFT correlation."""
        t = self.time_axis()
        I = self.pulse(t)
        ac = np.correlate(I, I, mode="same")
        return t, ac / ac.max()

    @staticmethod
    def fwhm(t, y):
        half = y.max() / 2
        above = np.where(y >= half)[0]
        return (t[above[-1]] - t[above[0]]) if len(above) > 1 else 0.0

    def measured_duration(self):
        """Recover pulse FWHM from the AC trace using the shape's deconv factor."""
        t, ac = self.trace()
        ac_fwhm = self.fwhm(t, ac)
        return ac_fwhm / DECONV[self.shape]


def main():
    ap = argparse.ArgumentParser(description="Intensity autocorrelation diagnostic")
    ap.add_argument("--pulse-ps", type=float, default=200.0)
    ap.add_argument("--shape", choices=list(DECONV), default="gaussian")
    args = ap.parse_args()

    ac = Autocorrelator(pulse_fwhm_ps=args.pulse_ps, shape=args.shape)
    t, trace = ac.trace()
    ac_fwhm = ac.fwhm(t, trace)
    recovered = ac.measured_duration()

    print("=" * 60)
    print(" Intensity autocorrelation diagnostic")
    print("=" * 60)
    print(f"  true pulse FWHM     : {args.pulse_ps:.1f} ps ({args.shape})")
    print(f"  autocorrelation FWHM: {ac_fwhm:.1f} ps")
    print(f"  deconvolution factor: {DECONV[args.shape]:.3f}")
    print(f"  recovered duration  : {recovered:.1f} ps")
    print("-" * 60)
    print("  if shape is mis-assumed, the recovered duration shifts:")
    for s, f in DECONV.items():
        print(f"    assume {s:<10}: {ac_fwhm / f:.1f} ps")
    print("=" * 60)

    if _HAVE_MPL:
        plt.figure(figsize=(8, 4.2))
        plt.plot(t, ac.pulse(t) / ac.pulse(t).max(), lw=2, label="pulse I(t)")
        plt.plot(t, trace, lw=2, label="autocorrelation")
        plt.xlabel("time / delay [ps]"); plt.ylabel("normalized")
        plt.title(f"Pulse vs its autocorrelation ({args.shape})")
        plt.legend(); plt.tight_layout(); plt.savefig("autocorrelation.png", dpi=130)
        print("Saved -> autocorrelation.png")
        plt.show()


if __name__ == "__main__":
    main()
