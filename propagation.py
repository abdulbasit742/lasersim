#!/usr/bin/env python3
"""
================================================================================
propagation.py  -  split-step nonlinear beam propagation (self-focusing)
================================================================================
The single biggest threat in a high-energy picosecond chain is small-scale
self-focusing: tiny intensity ripples on the beam grow exponentially through the
Kerr nonlinearity (n2) and can collapse into filaments that damage the glass.
The paper controls this by keeping the B-integral low, enlarging the beam, and
spatial filtering. This module SIMULATES that physics directly.

It propagates a 2D optical field through a Kerr medium using the split-step
Fourier method on the nonlinear Schrodinger equation:

    dE/dz = (i / 2k) * laplacian_perp(E)        # diffraction
            + i * k0 * n2 * |E|^2 * E            # Kerr self-focusing

and reports:
  * accumulated B-integral,
  * peak-intensity growth (the self-focusing signature),
  * Bespalov-Talanov most-unstable ripple spatial frequency,
  * whether a seeded ripple grows (filamentation risk) or is benign.

Run:
    python propagation.py                 # propagate a beam + ripple, plot
    python propagation.py --B 2.5         # target accumulated B-integral
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class Medium:
    n0: float = 1.82            # linear index (Nd:YAG)
    n2: float = 6.21e-20        # nonlinear index [m^2/W] (=6.21e-16 cm^2/W)
    lam: float = 1064e-9        # wavelength [m]
    length_m: float = 0.13      # propagation length

    @property
    def k0(self) -> float:
        return 2.0 * np.pi / self.lam

    @property
    def k(self) -> float:
        return self.n0 * self.k0


@dataclass
class Window:
    size_m: float = 0.02        # transverse window (2 cm)
    npix: int = 256

    def grid(self):
        x = np.linspace(-self.size_m / 2, self.size_m / 2, self.npix)
        X, Y = np.meshgrid(x, x)
        return X, Y, x

    def kgrid(self):
        dk = 2.0 * np.pi * np.fft.fftfreq(self.npix, d=self.size_m / self.npix)
        KX, KY = np.meshgrid(dk, dk)
        return KX, KY


def initial_field(win: Window, w_m=5e-3, order=4, I0=1e13,
                  ripple_amp=0.05, ripple_cycles=20):
    """Super-Gaussian beam with a small sinusoidal intensity ripple seeded on
    top (the seed for small-scale self-focusing)."""
    X, Y, x = win.grid()
    R2 = (X ** 2 + Y ** 2)
    w = w_m
    env = np.exp(-((R2 / w ** 2)) ** (order / 2))
    ripple = 1.0 + ripple_amp * np.cos(2 * np.pi * ripple_cycles * X / win.size_m)
    amp = np.sqrt(I0) * np.sqrt(np.clip(env * ripple, 0, None))
    return amp.astype(complex)


def split_step(E, med: Medium, win: Window, n_steps=200):
    """Propagate E over med.length_m using symmetric split-step Fourier.
    Returns (E_out, B_integral, peak_intensity_history)."""
    dz = med.length_m / n_steps
    KX, KY = win.kgrid()
    K2 = KX ** 2 + KY ** 2
    # half-step diffraction operator in Fourier space
    diff_half = np.exp(-1j * (K2 / (2.0 * med.k)) * (dz / 2.0))

    B = 0.0
    peaks = []
    for _ in range(n_steps):
        # half diffraction
        E = np.fft.ifft2(np.fft.fft2(E) * diff_half)
        # full nonlinear (Kerr) step
        I = np.abs(E) ** 2
        phi_nl = med.k0 * med.n2 * I * dz
        E = E * np.exp(1j * phi_nl)
        # half diffraction
        E = np.fft.ifft2(np.fft.fft2(E) * diff_half)
        # accumulate B-integral on axis (peak)
        B += med.k0 * med.n2 * I.max() * dz
        peaks.append(I.max())
    return E, B, np.array(peaks)


def bespalov_talanov_kmax(med: Medium, I0: float) -> float:
    """Most-unstable transverse spatial frequency for small-scale self-focusing
    [1/m]: k_perp_max = k0 * sqrt(2 n2 I0 / n0)."""
    return med.k0 * np.sqrt(max(2.0 * med.n2 * I0 / med.n0, 0.0))


def gain_factor(med: Medium, I0: float, k_perp: float) -> float:
    """Exponential power gain exp(2 g L) of a ripple at k_perp (B-T theory)."""
    g2 = (k_perp ** 2 / (2 * med.k)) * (2 * med.k0 * med.n2 * I0 - k_perp ** 2 / (2 * med.k))
    g = np.sqrt(g2) if g2 > 0 else 0.0
    return float(np.exp(2.0 * g * med.length_m))


def main():
    ap = argparse.ArgumentParser(description="Split-step self-focusing propagation")
    ap.add_argument("--I0", type=float, default=1e13, help="peak intensity [W/m^2]")
    ap.add_argument("--B", type=float, default=None,
                    help="scale I0 to hit this accumulated B-integral")
    args = ap.parse_args()

    med = Medium()
    win = Window()

    I0 = args.I0
    if args.B is not None:
        # B ~ k0 n2 I0 L  -> solve for I0
        I0 = args.B / (med.k0 * med.n2 * med.length_m)

    E0 = initial_field(win, I0=I0)
    E_out, B, peaks = split_step(E0, med, win)

    k_bt = bespalov_talanov_kmax(med, I0)
    growth = peaks[-1] / peaks[0]

    print("=" * 60)
    print(" Split-step self-focusing propagation (Nd:YAG rod)")
    print("=" * 60)
    print(f"  peak intensity I0   : {I0:.3e} W/m^2")
    print(f"  accumulated B       : {B:.2f} rad  "
          f"({'SAFE' if B < 3 else 'RISK of filamentation'})")
    print(f"  peak-intensity growth: {growth:.2f}x over the rod")
    print(f"  B-T most-unstable freq: {k_bt:.1f} 1/m "
          f"(ripple period ~ {2*np.pi/k_bt*1e3:.2f} mm)" if k_bt > 0 else "  no instability")
    print("=" * 60)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
        ax[0].imshow(np.abs(E0) ** 2, cmap="turbo"); ax[0].set_title("input intensity")
        ax[0].axis("off")
        ax[1].imshow(np.abs(E_out) ** 2, cmap="turbo")
        ax[1].set_title(f"after rod (B={B:.2f})"); ax[1].axis("off")
        ax[2].plot(np.linspace(0, med.length_m * 100, len(peaks)), peaks / peaks[0], lw=2)
        ax[2].set(title="peak intensity growth", xlabel="z [cm]", ylabel="I_peak / I0")
        plt.tight_layout(); plt.savefig("propagation.png", dpi=130)
        print("Saved -> propagation.png")
        plt.show()


if __name__ == "__main__":
    main()
