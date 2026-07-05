#!/usr/bin/env python3
"""
LASERSIM : single-file laser rate-equation simulation platform.
Models: ThreeLevel, FourLevel, CW, QSwitchActive, QSwitchPassive,
GainSwitched, MultiMode, ModeLocked, Thermal.

Usage:
  python laser_platform.py            # full dashboard
  python laser_platform.py --list     # list models
  python laser_platform.py --model qswitch_active
  python laser_platform.py --sweep    # L-I threshold sweep
"""
from __future__ import annotations
import argparse, sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional, Sequence, Tuple
import numpy as np
trapz = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
from scipy.integrate import solve_ivp
try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

C0 = 2.99792458e8
H = 6.62607015e-34
KB = 1.380649e-23
Q_E = 1.602176634e-19


@dataclass
class Cavity:
    sigma: float = 2.8e-23
    tau: float = 230e-6
    n: float = 1.82
    lam: float = 1064e-9
    N_total: float = 1.38e26
    L_cav: float = 0.10
    L_gain: float = 0.05
    A_mode: float = 1.0e-6
    R1: float = 1.00
    R2: float = 0.95
    loss_i: float = 0.01
    Rp: float = 5.0e29
    beta: float = 1e-6
    c: float = field(init=False)
    tau_c: float = field(init=False)
    V_mode: float = field(init=False)
    nu: float = field(init=False)
    photon_E: float = field(init=False)

    def __post_init__(self):
        self.c = C0 / self.n
        loss_rt = -np.log(self.R1 * self.R2) + 2.0 * self.loss_i
        t_rt = 2.0 * self.L_cav / self.c
        self.tau_c = t_rt / loss_rt
        self.V_mode = self.A_mode * self.L_gain
        self.nu = C0 / self.lam
        self.photon_E = H * self.nu

    @property
    def N_threshold(self):
        return 1.0 / (self.c * self.sigma * self.tau_c)

    @property
    def Rp_threshold(self):
        return self.N_threshold / self.tau

    @property
    def r(self):
        return self.Rp / self.Rp_threshold

    def relaxation_freq_hz(self):
        if self.r <= 1.0:
            return 0.0
        w = np.sqrt((self.r - 1.0) / (self.tau * self.tau_c))
        return w / (2.0 * np.pi)

    def output_power(self, S):
        T2 = 1.0 - self.R2
        photons = S * self.V_mode
        rate_out = photons * (self.c / (2.0 * self.L_cav)) * T2
        return rate_out * self.photon_E


@dataclass
class SimResult:
    t: np.ndarray
    y: np.ndarray
    labels: Sequence[str]
    model: str
    extra: Dict[str, float] = field(default_factory=dict)

    def series(self, name):
        return self.y[list(self.labels).index(name)]


class LaserModel(ABC):
    name = "base"
    state_labels: Sequence[str] = ()
    t_end = 2e-3
    n_pts = 20000
    method = "LSODA"
    rtol = 1e-8
    atol = 1e-3
    max_step = None

    def __init__(self, cav=None, **kw):
        self.cav = cav or Cavity()
        self.opts = kw

    @abstractmethod
    def rhs(self, t, y): ...

    @abstractmethod
    def initial_state(self): ...

    def simulate(self):
        t_eval = np.linspace(0.0, self.t_end, self.n_pts)
        kwargs = dict(rtol=self.rtol, atol=self.atol, method=self.method)
        if self.max_step:
            kwargs["max_step"] = self.max_step
        sol = solve_ivp(self.rhs, (0.0, self.t_end), list(self.initial_state()),
                        t_eval=t_eval, **kwargs)
        if not sol.success:
            raise RuntimeError(f"[{self.name}] integration failed: {sol.message}")
        return SimResult(sol.t, sol.y, self.state_labels, self.name, extra=self.metrics(sol))

    def metrics(self, sol):
        return {}


class ThreeLevelLaser(LaserModel):
    name = "three_level"
    state_labels = ("N", "S")
    t_end = 3e-3

    def rhs(self, t, y):
        p = self.cav
        N, S = y
        N2 = 0.5 * (p.N_total + N)
        stim = p.c * p.sigma * N * S
        dN = 2.0 * (p.Rp - N2 / p.tau) - 2.0 * stim
        dS = stim - S / p.tau_c + p.beta * N2 / p.tau
        return [dN, dS]

    def initial_state(self):
        return [-self.cav.N_total, 1.0]


class FourLevelLaser(LaserModel):
    name = "four_level"
    state_labels = ("N", "S")
    t_end = 2e-3

    def rhs(self, t, y):
        p = self.cav
        N, S = y
        stim = p.c * p.sigma * N * S
        dN = p.Rp - N / p.tau - stim
        dS = stim - S / p.tau_c + p.beta * N / p.tau
        return [dN, dS]

    def initial_state(self):
        return [0.0, 1.0]

    def steady_state(self):
        p = self.cav
        N_ss = p.N_threshold
        S_ss = p.tau_c * (p.Rp - N_ss / p.tau)
        return N_ss, max(S_ss, 0.0)

    def metrics(self, sol):
        N_ss, S_ss = self.steady_state()
        return {"N_ss": N_ss, "S_ss": S_ss, "P_out_W": self.cav.output_power(S_ss),
                "f_relax_kHz": self.cav.relaxation_freq_hz() / 1e3}


class CWLaser(FourLevelLaser):
    name = "cw"


class QSwitchActive(FourLevelLaser):
    name = "qswitch_active"
    t_end = 1.05e-3
    rtol = 1e-9
    atol = 1e-2

    def __init__(self, cav=None, t_open=1e-3, hold_factor=1e-3, switch_width=1e-9, **kw):
        super().__init__(cav, **kw)
        self.t_open = t_open
        self.tau_lo = self.cav.tau_c * hold_factor
        self.tau_hi = self.cav.tau_c
        self.switch_width = switch_width
        self.max_step = min(1e-9, (self.t_end - t_open) / 5000)

    def tau_c_of_t(self, t):
        x = (t - self.t_open) / self.switch_width
        s = 0.5 * (1.0 + np.tanh(x))
        return self.tau_lo + (self.tau_hi - self.tau_lo) * s

    def rhs(self, t, y):
        p = self.cav
        N, S = y
        stim = p.c * p.sigma * N * S
        dN = p.Rp - N / p.tau - stim
        dS = stim - S / self.tau_c_of_t(t) + p.beta * N / p.tau
        return [dN, dS]

    def metrics(self, sol):
        S = sol.y[1]; t = sol.t
        P = np.array([self.cav.output_power(s) for s in S])
        i_pk = int(np.argmax(P)); peak = P[i_pk]
        energy = trapz(P, t)
        half = peak / 2.0
        above = np.where(P >= half)[0]
        fwhm = (t[above[-1]] - t[above[0]]) if len(above) > 1 else 0.0
        return {"peak_power_W": peak, "pulse_energy_J": energy,
                "fwhm_ns": fwhm * 1e9, "t_peak_us": t[i_pk] * 1e6}


class QSwitchPassive(LaserModel):
    name = "qswitch_passive"
    state_labels = ("N", "Na", "S")
    t_end = 2e-3
    rtol = 1e-9
    atol = 1e-2

    def __init__(self, cav=None, sigma_a=5e-22, Na0=2e22, tau_a=1e-6, **kw):
        super().__init__(cav, **kw)
        self.sigma_a = sigma_a; self.Na0 = Na0; self.tau_a = tau_a
        self.max_step = 5e-9

    def rhs(self, t, y):
        p = self.cav
        N, Na, S = y
        gain = p.c * p.sigma * N * S
        absn = p.c * self.sigma_a * Na * S
        dN = p.Rp - N / p.tau - gain
        dNa = (self.Na0 - Na) / self.tau_a - absn
        dS = gain - absn - S / p.tau_c + p.beta * N / p.tau
        return [dN, dNa, dS]

    def initial_state(self):
        return [0.0, self.Na0, 1.0]


class GainSwitchedLaser(FourLevelLaser):
    name = "gain_switched"
    t_end = 50e-6
    n_pts = 40000

    def __init__(self, cav=None, pump_peak=None, t0=10e-6, width=2e-6, **kw):
        super().__init__(cav, **kw)
        self.pump_peak = pump_peak or (50.0 * self.cav.Rp_threshold)
        self.t0 = t0; self.width = width; self.max_step = 5e-9

    def pump(self, t):
        return self.pump_peak * np.exp(-0.5 * ((t - self.t0) / self.width) ** 2)

    def rhs(self, t, y):
        p = self.cav
        N, S = y
        stim = p.c * p.sigma * N * S
        dN = self.pump(t) - N / p.tau - stim
        dS = stim - S / p.tau_c + p.beta * N / p.tau
        return [dN, dS]


class MultiModeLaser(LaserModel):
    name = "multimode"
    t_end = 1.5e-3
    n_pts = 30000

    def __init__(self, cav=None, n_modes=5, spread=0.15, **kw):
        super().__init__(cav, **kw)
        self.M = n_modes
        idx = np.arange(self.M) - (self.M - 1) / 2.0
        self.sig = self.cav.sigma * np.exp(-0.5 * (idx * spread) ** 2)
        self.state_labels = ["N"] + [f"S{i}" for i in range(self.M)]

    def rhs(self, t, y):
        p = self.cav
        N = y[0]; S = np.asarray(y[1:])
        stim = p.c * self.sig * N * S
        dN = p.Rp - N / p.tau - np.sum(stim)
        dS = stim - S / p.tau_c + p.beta * N / p.tau
        return [dN, *dS]

    def initial_state(self):
        return [0.0] + [1.0] * self.M

    def metrics(self, sol):
        finalS = sol.y[1:, -1]
        winner = int(np.argmax(finalS))
        return {"winning_mode": winner,
                "winner_fraction": float(finalS[winner] / (finalS.sum() + 1e-30))}


class ModeLockedLaser(LaserModel):
    name = "mode_locked"
    state_labels = ("g", "E")
    t_end = 5e-6
    n_pts = 40000

    def __init__(self, cav=None, g0=0.5, Esat=1e-9, l0=0.1, q0=0.2, Psat=1e3, tau_g=200e-6, **kw):
        super().__init__(cav, **kw)
        self.g0 = g0; self.Esat = Esat; self.l0 = l0; self.q0 = q0
        self.Psat = Psat; self.tau_g = tau_g
        self.t_rt = 2.0 * self.cav.L_cav / self.cav.c

    def rhs(self, t, y):
        g, E = y
        P = E / self.t_rt
        q = self.q0 / (1.0 + P / self.Psat)
        net_gain = g - self.l0 - q
        dE = net_gain * E / self.t_rt
        dg = (self.g0 - g) / self.tau_g - g * E / (self.Esat * self.tau_g)
        return [dg, dE]

    def initial_state(self):
        return [self.g0, 1e-12]


class ThermalLaser(FourLevelLaser):
    name = "thermal"
    state_labels = ("N", "S", "T")
    t_end = 5e-3
    n_pts = 30000

    def __init__(self, cav=None, heat_frac=0.3, C_th=1.0, R_th=50.0, alpha_loss=2e-3, T_amb=300.0, **kw):
        super().__init__(cav, **kw)
        self.heat_frac = heat_frac; self.C_th = C_th; self.R_th = R_th
        self.alpha_loss = alpha_loss; self.T_amb = T_amb; self.max_step = 1e-7

    def rhs(self, t, y):
        p = self.cav
        N, S, T = y
        dT_excess = T - self.T_amb
        tau_c_eff = p.tau_c / (1.0 + self.alpha_loss * max(dT_excess, 0.0))
        stim = p.c * p.sigma * N * S
        dN = p.Rp - N / p.tau - stim
        dS = stim - S / tau_c_eff + p.beta * N / p.tau
        heat_in = self.heat_frac * p.Rp * p.photon_E * p.V_mode
        dT = (heat_in - dT_excess / self.R_th) / self.C_th
        return [dN, dS, dT]

    def initial_state(self):
        return [0.0, 1.0, self.T_amb]


def li_curve(base, r_max=5.0, n=80):
    rs = np.linspace(0.05, r_max, n); P = []
    for r in rs:
        cav = replace(base, Rp=r * base.Rp_threshold)
        _, S_ss = FourLevelLaser(cav).steady_state()
        P.append(cav.output_power(S_ss))
    return rs, np.asarray(P)


def slope_efficiency(rs, P):
    mask = rs > 1.2
    if mask.sum() < 2:
        return 0.0
    A = np.vstack([rs[mask], np.ones(mask.sum())]).T
    slope, _ = np.linalg.lstsq(A, P[mask], rcond=None)[0]
    return slope


MODEL_REGISTRY = {
    "three_level": ThreeLevelLaser,
    "four_level": FourLevelLaser,
    "cw": CWLaser,
    "qswitch_active": QSwitchActive,
    "qswitch_passive": QSwitchPassive,
    "gain_switched": GainSwitchedLaser,
    "multimode": MultiModeLaser,
    "mode_locked": ModeLockedLaser,
    "thermal": ThermalLaser,
}


def print_header(cav):
    print("=" * 70)
    print(" LASERSIM - laser rate-equation simulation platform")
    print("=" * 70)
    print(f"  wavelength            : {cav.lam*1e9:.1f} nm")
    print(f"  cavity photon lifetime: {cav.tau_c*1e9:.2f} ns")
    print(f"  threshold inversion   : {cav.N_threshold:.3e} 1/m^3")
    print(f"  threshold pump        : {cav.Rp_threshold:.3e} 1/(m^3 s)")
    print(f"  pump ratio r          : {cav.r:.2f}")
    print(f"  relaxation osc freq   : {cav.relaxation_freq_hz()/1e3:.1f} kHz")
    print("=" * 70)


def run_dashboard(save="laser_platform.png"):
    cav = Cavity()
    print_header(cav)
    if not _HAVE_MPL:
        for key in ("four_level", "qswitch_active", "multimode"):
            res = MODEL_REGISTRY[key]().simulate()
            print(f"[{key}] metrics: {res.extra}")
        return
    fig, ax = plt.subplots(2, 3, figsize=(16, 9))
    cw = CWLaser(cav).simulate()
    ax[0, 0].plot(cw.t * 1e6, cw.series("S"), lw=1)
    ax[0, 0].set(title="CW turn-on", xlabel="t [us]", ylabel="S")
    ax[0, 1].plot(cw.t * 1e6, cw.series("N"), color="tab:green", lw=1)
    ax[0, 1].axhline(cav.N_threshold, color="r", ls="--")
    ax[0, 1].set(title="Inversion clamp", xlabel="t [us]", ylabel="N")
    rs, P = li_curve(cav)
    ax[0, 2].plot(rs, P * 1e3, lw=2); ax[0, 2].axvline(1.0, color="r", ls="--")
    ax[0, 2].set(title="L-I curve", xlabel="r", ylabel="P_out [mW]")
    qs = QSwitchActive(replace(cav, Rp=5e29)).simulate()
    ax[1, 0].plot((qs.t - 1e-3) * 1e9, qs.series("S"), color="tab:purple", lw=1.2)
    ax[1, 0].set(title=f"Q-switch FWHM={qs.extra['fwhm_ns']:.1f}ns", xlabel="t [ns]", ylabel="S")
    mm = MultiModeLaser(cav, n_modes=5).simulate()
    for i in range(5):
        ax[1, 1].plot(mm.t * 1e6, mm.series(f"S{i}"), lw=1, label=f"mode {i}")
    ax[1, 1].set(title=f"Mode competition win={mm.extra['winning_mode']}", xlabel="t [us]", ylabel="S")
    ax[1, 1].legend(fontsize=7)
    gs = GainSwitchedLaser(cav).simulate()
    ax[1, 2].plot(gs.t * 1e6, gs.series("S"), color="tab:orange", lw=1)
    ax[1, 2].set(title="Gain-switched", xlabel="t [us]", ylabel="S")
    plt.tight_layout(); plt.savefig(save, dpi=130)
    print(f"Saved dashboard -> {save}")
    plt.show()


def run_single(name):
    cav = Cavity(); print_header(cav)
    res = MODEL_REGISTRY[name](cav).simulate()
    print(f"[{name}] states: {list(res.labels)}")
    for k, v in res.extra.items():
        print(f"    {k:>16s} = {v:.6g}")
    if _HAVE_MPL:
        plt.figure(figsize=(9, 5))
        for lab in res.labels:
            y = res.series(lab)
            plt.plot(res.t * 1e6, y / (np.max(np.abs(y)) + 1e-30), lw=1, label=lab)
        plt.title(f"{name} (normalized)"); plt.xlabel("t [us]")
        plt.legend(); plt.tight_layout(); plt.show()


def main(argv=None):
    ap = argparse.ArgumentParser(description="LASERSIM laser-modeling platform")
    ap.add_argument("--model", choices=sorted(MODEL_REGISTRY))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args(argv)
    if args.list:
        for k in sorted(MODEL_REGISTRY):
            print(f"  - {k}")
        return 0
    if args.sweep:
        cav = Cavity(); print_header(cav)
        rs, P = li_curve(cav)
        print(f"slope efficiency ~ {slope_efficiency(rs, P)*1e3:.3f} mW per unit r")
        return 0
    if args.model:
        run_single(args.model); return 0
    run_dashboard(); return 0


if __name__ == "__main__":
    sys.exit(main())
