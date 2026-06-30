#!/usr/bin/env python3
"""
================================================================================
frog.py  -  frequency-resolved optical gating (FROG)
================================================================================
autocorrelation.py gives only the pulse WIDTH (and needs a shape assumption).
FROG goes further: it measures the full pulse, AMPLITUDE and PHASE, by recording
a 2D spectrogram, the spectrum of the autocorrelation signal vs delay. From that
trace you can retrieve chirp and confirm a clean recompression (critical after
the CPA/OPCPA stages). This module generates the SHG-FROG trace for a chirped
pulse so you can see how chirp tilts/broadens the trace.

Model (SHG-FROG)
----------------
  Field:   E(t) = exp(-t^2/2 tau^2) * exp(i a t^2)        (a = chirp)
  Signal:  E_sig(t, delay) = E(t) E(t - delay)
  Trace:   I(omega, delay) = | FT_t[ E_sig(t, delay) ] |^2
A transform-limited pulse gives a round, untilted trace; chirp tilts and
stretches it.

Run:
    python frog.py
    python frog.py --chirp 0.5
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
class FROG:
    fwhm_ps: float = 200.0
    chirp: float = 0.0          # quadratic spectral-phase parameter
    npts: int = 256

    @property
    def tau(self):
        return (self.fwhm_ps) / 1.6651

    def field(self, t):
        return np.exp(-t ** 2 / (2 * self.tau ** 2)) * np.exp(1j * self.chirp * t ** 2)

    def trace(self):
        """SHG-FROG spectrogram: |FT_t[ E(t)E(t-delay) ]|^2."""
        span = 6 * self.tau
        t = np.linspace(-span, span, self.npts)
        delays = np.linspace(-span, span, self.npts)
        E = self.field(t)
        trace = np.empty((self.npts, self.npts))
        for i, d in enumerate(delays):
            Ed = np.interp(t - d, t, E.real) + 1j * np.interp(t - d, t, E.imag)
            sig = E * Ed
            spec = np.abs(np.fft.fftshift(np.fft.fft(sig))) ** 2
            trace[:, i] = spec
        return t, delays, trace / trace.max()

    def trace_tilt(self):
        """Correlation between frequency centroid and delay = chirp signature."""
        t, delays, trace = self.trace()
        freqs = np.arange(self.npts) - self.npts / 2
        centroids = [(freqs * trace[:, i]).sum() / (trace[:, i].sum() + 1e-12)
                     for i in range(self.npts)]
        return float(np.polyfit(delays, centroids, 1)[0])


def main():
    ap = argparse.ArgumentParser(description="SHG-FROG pulse characterization")
    ap.add_argument("--chirp", type=float, default=0.0)
    ap.add_argument("--fwhm-ps", type=float, default=200.0)
    args = ap.parse_args()

    frog = FROG(fwhm_ps=args.fwhm_ps, chirp=args.chirp)
    tilt = frog.trace_tilt()

    print("=" * 60)
    print(" SHG-FROG pulse characterization")
    print("=" * 60)
    print(f"  pulse FWHM          : {args.fwhm_ps:.0f} ps")
    print(f"  chirp parameter     : {args.chirp:.3f}")
    print(f"  trace tilt          : {tilt:+.3f} (0 = transform-limited)")
    print(f"  diagnosis           : {'CHIRPED (recompress further)' if abs(tilt) > 0.05 else 'clean / transform-limited'}")
    print("=" * 60)

    if _HAVE_MPL:
        t, delays, trace = frog.trace()
        plt.figure(figsize=(5.6, 4.8))
        plt.imshow(trace, cmap="inferno", aspect="auto",
                   extent=[delays[0], delays[-1], -frog.npts/2, frog.npts/2])
        plt.xlabel("delay [ps]"); plt.ylabel("frequency [arb]")
        plt.title(f"SHG-FROG trace (chirp={args.chirp})")
        plt.colorbar(label="intensity")
        plt.tight_layout(); plt.savefig("frog.png", dpi=130)
        print("Saved -> frog.png")
        plt.show()


if __name__ == "__main__":
    main()
