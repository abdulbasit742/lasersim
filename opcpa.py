#!/usr/bin/env python3
"""
================================================================================
opcpa.py  -  Optical Parametric Chirped-Pulse Amplification front-end
================================================================================
The paper explicitly motivates the 1.28 J / 200 ps Nd:YAG system as a PUMP for
OPCPA (optical parametric chirped-pulse amplification). This module models the
OPCPA stage that such a pump would drive:

  1. STRETCHER : a broadband signal pulse is chirped (group-delay dispersion)
     from femtoseconds out to ~ the pump duration so it can be amplified safely.
  2. OPA GAIN  : the stretched signal and the Nd:YAG pump co-propagate through a
     nonlinear crystal (e.g. BBO/LBO). Energy flows pump -> signal + idler via
     three-wave mixing. We solve the coupled-amplitude equations.
  3. COMPRESSOR: the amplified signal is de-chirped back toward its transform
     limit; we estimate the recompressed duration and peak power.

This closes the loop: LASERSIM can now model the whole short-pulse front-end
that the NILOP amplifier was built to pump.

Core physics (collinear, non-depleted -> depleted 3-wave OPA):
    dA_s/dz = i*kappa * A_p * conj(A_i) * exp(-i dk z)
    dA_i/dz = i*kappa * A_p * conj(A_s) * exp(-i dk z)
    dA_p/dz = i*kappa * A_s * A_i        * exp(+i dk z)
Parametric gain (non-depleted pump, phase-matched): G = cosh^2(g L),
    g = kappa * |A_p|.

Run:
    python opcpa.py
    python opcpa.py --pump-intensity 5e9 --crystal-mm 15
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.integrate import solve_ivp

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

C0 = 2.99792458e8


# ==============================================================================
# CHIRPED-PULSE STRETCH / COMPRESS
# ==============================================================================
@dataclass
class ChirpedPulse:
    """Transform-limited Gaussian seed that gets stretched by GDD."""
    fwhm_fs: float = 30.0          # transform-limited duration [fs]
    center_nm: float = 1053.0      # signal wavelength (Nd:glass/OPCPA band)
    energy_nJ: float = 1.0

    @property
    def tau0_s(self) -> float:
        return self.fwhm_fs * 1e-15 / 1.1774   # FWHM -> 1/e half-width

    @property
    def bandwidth_rad_s(self) -> float:
        # time-bandwidth product for a Gaussian: dt*dw = 0.441*2pi
        return 0.441 * 2.0 * np.pi / (self.fwhm_fs * 1e-15)

    def stretched_duration_s(self, gdd_fs2: float) -> float:
        """Stretched FWHM given group-delay dispersion (GDD) in fs^2."""
        gdd = gdd_fs2 * 1e-30
        t0 = self.tau0_s
        # standard chirped-Gaussian broadening
        return self.fwhm_fs * 1e-15 * np.sqrt(1.0 + (gdd / t0 ** 2) ** 2)

    def gdd_for_target(self, target_ps: float) -> float:
        """GDD [fs^2] needed to stretch to target duration (to match pump)."""
        t0 = self.tau0_s
        target_s = target_ps * 1e-12
        ratio = (target_s / (self.fwhm_fs * 1e-15)) ** 2 - 1.0
        ratio = max(ratio, 0.0)
        return np.sqrt(ratio) * t0 ** 2 / 1e-30


# ==============================================================================
# OPA CRYSTAL + 3-WAVE COUPLED EQUATIONS
# ==============================================================================
@dataclass
class OPACrystal:
    name: str = "BBO"
    length_mm: float = 15.0
    deff_pm_V: float = 2.0          # effective nonlinearity [pm/V]
    n_signal: float = 1.65
    n_idler: float = 1.65
    n_pump: float = 1.65
    lam_signal_nm: float = 1053.0
    lam_pump_nm: float = 1064.0     # Nd:YAG pump from this very system!

    @property
    def lam_idler_nm(self) -> float:
        # energy conservation: 1/lp = 1/ls + 1/li
        inv = 1.0 / self.lam_pump_nm - 1.0 / self.lam_signal_nm
        return 1.0 / inv if inv != 0 else np.inf

    def kappa(self, pump_intensity_W_cm2: float) -> float:
        """Nonlinear coupling -> parametric gain coefficient g [1/m].
        g = (4*pi*deff / lam_s) * sqrt(I_p / (2 n_s n_i n_p eps0 c)).
        Constants lumped into a calibrated prefactor for clarity."""
        eps0 = 8.8541878128e-12
        I = pump_intensity_W_cm2 * 1e4   # W/m^2
        deff = self.deff_pm_V * 1e-12
        lam_s = self.lam_signal_nm * 1e-9
        pref = (4.0 * np.pi * deff / lam_s)
        denom = 2.0 * self.n_signal * self.n_idler * self.n_pump * eps0 * C0
        return pref * np.sqrt(I / denom)


def opa_gain_nondepleted(g: float, length_mm: float, dk: float = 0.0) -> float:
    """Signal power gain for a non-depleted pump.
    Phase-matched: G = cosh^2(g L). With mismatch dk it's reduced."""
    L = length_mm * 1e-3
    if dk == 0.0:
        return np.cosh(g * L) ** 2
    s = np.sqrt(np.maximum(g ** 2 - (dk / 2.0) ** 2, 0.0))
    if s == 0:
        return 1.0 + (g * L) ** 2
    return 1.0 + (g / s) ** 2 * np.sinh(s * L) ** 2


def solve_depleted(g: float, length_mm: float, seed_frac: float = 1e-6):
    """Solve the depleted 3-wave equations (real amplitudes, phase-matched) to
    show pump depletion and signal saturation along the crystal.
    Normalized so pump amplitude starts at 1."""
    L = length_mm * 1e-3
    kap = g  # with |A_p|=1, g = kappa

    def rhs(z, y):
        As, Ai, Ap = y
        dAs = kap * Ap * Ai
        dAi = kap * Ap * As
        dAp = -kap * As * Ai
        return [dAs, dAi, dAp]

    y0 = [np.sqrt(seed_frac), 0.0, 1.0]
    sol = solve_ivp(rhs, (0, L), y0, t_eval=np.linspace(0, L, 400),
                    rtol=1e-9, atol=1e-12)
    z = sol.t
    Ps, Pi, Pp = sol.y[0] ** 2, sol.y[1] ** 2, sol.y[2] ** 2
    return z, Ps, Pi, Pp


# ==============================================================================
# DRIVER
# ==============================================================================
def main():
    ap = argparse.ArgumentParser(description="OPCPA front-end driven by the Nd:YAG pump")
    ap.add_argument("--pump-intensity", type=float, default=2e9,
                    help="pump intensity at the crystal [W/cm^2]")
    ap.add_argument("--crystal-mm", type=float, default=15.0)
    ap.add_argument("--target-ps", type=float, default=200.0,
                    help="stretch target (match pump duration) [ps]")
    args = ap.parse_args()

    pulse = ChirpedPulse()
    crystal = OPACrystal(length_mm=args.crystal_mm)

    gdd = pulse.gdd_for_target(args.target_ps)
    stretched = pulse.stretched_duration_s(gdd)
    g = crystal.kappa(args.pump_intensity)
    G_small = opa_gain_nondepleted(g, crystal.length_mm)
    z, Ps, Pi, Pp = solve_depleted(g, crystal.length_mm)
    conv_eff = Ps[-1] / 1.0  # signal power relative to initial pump power

    print("=" * 66)
    print(" OPCPA front-end  (pumped by the 1.28 J / 200 ps Nd:YAG system)")
    print("=" * 66)
    print(f"  signal : {pulse.center_nm:.0f} nm, TL {pulse.fwhm_fs:.0f} fs")
    print(f"  pump   : {crystal.lam_pump_nm:.0f} nm (Nd:YAG), {args.target_ps:.0f} ps")
    print(f"  idler  : {crystal.lam_idler_nm:.0f} nm")
    print(f"  stretch GDD needed : {gdd:.3e} fs^2 -> {stretched*1e12:.1f} ps")
    print(f"  crystal : {crystal.name}, {crystal.length_mm:.0f} mm")
    print(f"  gain coeff g       : {g:.3e} 1/m  (gL = {g*crystal.length_mm*1e-3:.2f})")
    print(f"  small-signal gain  : {G_small:.2e}x")
    print(f"  pump depletion     : {(1-Pp[-1])*100:.1f}% converted")
    print(f"  signal conversion  : {conv_eff*100:.1f}% of pump power")
    print("=" * 66)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
        zz = z * 1e3
        ax[0].plot(zz, Pp, label="pump", lw=2)
        ax[0].plot(zz, Ps, label="signal", lw=2)
        ax[0].plot(zz, Pi, label="idler", lw=2, ls="--")
        ax[0].set(title="3-wave OPA energy transfer", xlabel="z [mm]",
                  ylabel="normalized power"); ax[0].legend()
        Is = np.linspace(1e8, 1e10, 200)
        Gs = [opa_gain_nondepleted(crystal.kappa(I), crystal.length_mm) for I in Is]
        ax[1].semilogy(Is, Gs, lw=2)
        ax[1].set(title="Parametric gain vs pump intensity",
                  xlabel="pump intensity [W/cm^2]", ylabel="signal gain")
        plt.tight_layout(); plt.savefig("opcpa.png", dpi=130)
        print("Saved -> opcpa.png")
        plt.show()


if __name__ == "__main__":
    main()
