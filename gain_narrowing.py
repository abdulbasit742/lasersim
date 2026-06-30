#!/usr/bin/env python3
"""
================================================================================
gain_narrowing.py  -  spectral gain narrowing during amplification
================================================================================
Nd:YAG has a NARROW gain bandwidth (~0.6 nm, the paper explicitly notes this).
Every pass, the spectrum is multiplied by the gain lineshape, which is peaked at
line center. So the wings get less gain than the center and the spectrum NARROWS
with each pass. A narrower spectrum means a LONGER transform-limited pulse: gain
narrowing sets a floor on how short the recompressed pulse can be. This is the
physics that limits chirped-pulse / OPCPA-pump systems built on Nd:YAG, and no
other module covered it.

Model
-----
  Gain lineshape (Lorentzian, FWHM = delta_nu):
      g(nu) = g0 / (1 + (2 (nu - nu0) / delta_nu)^2)
  After n passes with small-signal gain G0 at line center:
      S_out(nu) = S_in(nu) * exp( n * ln(G0) * g(nu)/g0 )
  Transform-limited duration ~ time-bandwidth product / spectral FWHM.

Reports input vs output spectral width and the transform-limited pulse-duration
floor after the chain.

Run:
    python gain_narrowing.py
    python gain_narrowing.py --passes 5 --g0 5
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
TBP_GAUSS = 0.441   # time-bandwidth product for a Gaussian pulse


@dataclass
class GainLine:
    lam0_nm: float = 1064.0
    bandwidth_nm: float = 0.6     # Nd:YAG gain FWHM (paper)

    @property
    def nu0(self) -> float:
        return C0 / (self.lam0_nm * 1e-9)

    @property
    def delta_nu(self) -> float:
        """Gain FWHM in frequency [Hz] from the wavelength bandwidth."""
        lam0 = self.lam0_nm * 1e-9
        return C0 * (self.bandwidth_nm * 1e-9) / lam0 ** 2

    def lineshape(self, nu):
        """Normalized Lorentzian gain profile, peak = 1 at line center."""
        return 1.0 / (1.0 + (2.0 * (nu - self.nu0) / self.delta_nu) ** 2)


def spectral_fwhm(nu, S):
    """FWHM of a spectrum S(nu) [Hz]."""
    half = S.max() / 2.0
    above = np.where(S >= half)[0]
    return (nu[above[-1]] - nu[above[0]]) if len(above) > 1 else 0.0


def transform_limited_ps(fwhm_hz):
    """Transform-limited Gaussian duration [ps] for a spectral FWHM [Hz]."""
    return TBP_GAUSS / fwhm_hz * 1e12 if fwhm_hz > 0 else float("inf")


def amplify_spectrum(line: GainLine, S_in, nu, n_passes, g0):
    """Multiply the input spectrum by the gain lineshape over n passes."""
    g = line.lineshape(nu)
    log_gain = n_passes * np.log(g0) * g
    return S_in * np.exp(log_gain)


def main():
    ap = argparse.ArgumentParser(description="Spectral gain narrowing")
    ap.add_argument("--passes", type=int, default=5)
    ap.add_argument("--g0", type=float, default=5.0, help="line-center gain per pass")
    ap.add_argument("--input-nm", type=float, default=1.0,
                    help="input spectral FWHM [nm]")
    args = ap.parse_args()

    line = GainLine()
    # frequency grid around line center
    span = 5.0 * line.delta_nu
    nu = np.linspace(line.nu0 - span, line.nu0 + span, 8000)

    # input spectrum: Gaussian of the requested width
    lam0 = line.lam0_nm * 1e-9
    in_fwhm_hz = C0 * (args.input_nm * 1e-9) / lam0 ** 2
    sigma = in_fwhm_hz / 2.3548
    S_in = np.exp(-0.5 * ((nu - line.nu0) / sigma) ** 2)

    S_out = amplify_spectrum(line, S_in, nu, args.passes, args.g0)
    S_out /= S_out.max()

    fwhm_in = spectral_fwhm(nu, S_in)
    fwhm_out = spectral_fwhm(nu, S_out)
    nm_in = fwhm_in * lam0 ** 2 / C0 * 1e9
    nm_out = fwhm_out * lam0 ** 2 / C0 * 1e9

    print("=" * 64)
    print(" Spectral gain narrowing (Nd:YAG, 0.6 nm gain bandwidth)")
    print("=" * 64)
    print(f"  passes / line-center gain : {args.passes} x G0={args.g0}")
    print(f"  spectral FWHM in -> out   : {nm_in:.3f} -> {nm_out:.3f} nm")
    print(f"  TL duration  in -> out    : {transform_limited_ps(fwhm_in):.2f} "
          f"-> {transform_limited_ps(fwhm_out):.2f} ps")
    print(f"  -> gain narrowing widened the shortest possible pulse by "
          f"{transform_limited_ps(fwhm_out)/transform_limited_ps(fwhm_in):.2f}x")
    print("=" * 64)

    if _HAVE_MPL:
        dlam = (nu - line.nu0) * lam0 ** 2 / C0 * 1e9
        plt.figure(figsize=(8, 4.4))
        plt.plot(dlam, S_in / S_in.max(), lw=2, label="input spectrum")
        plt.plot(dlam, S_out, lw=2, label=f"after {args.passes} passes")
        plt.plot(dlam, line.lineshape(nu), lw=1, ls="--", color="gray",
                 label="gain lineshape")
        plt.xlabel("wavelength offset [nm]"); plt.ylabel("normalized")
        plt.title("Gain narrowing in Nd:YAG")
        plt.legend(); plt.tight_layout(); plt.savefig("gain_narrowing.png", dpi=130)
        print("Saved -> gain_narrowing.png")
        plt.show()


if __name__ == "__main__":
    main()
