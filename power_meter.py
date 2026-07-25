#!/usr/bin/env python3
"""
================================================================================
power_meter.py  -  optical power meter: heads, response, calibration, uncertainty
================================================================================
detectors.py answers "is my photodiode saturated?". This module answers the next
question every lab actually argues about: *how much do I trust the number on the
power meter?* A reading is only as good as (a) the head you used, (b) the
wavelength correction you forgot to apply, and (c) the uncertainty budget nobody
writes down.

Two heads are modelled:

  Thermopile (thermal) head
      Broadband, absorbs the beam and reads a temperature gradient. Slow:
      first-order thermal response with time constant tau,
          V(t) = R * P * (1 - exp(-t / tau))
      so a 1.2 s head needs ~4.6 tau to settle to 99 %. Limited by total power
      and by power *density* (W/cm^2) at the absorber, which is the number that
      actually burns heads.

  Photodiode head
      Fast and sensitive but strongly wavelength dependent:
          R(lambda) = eta q lambda / (h c)     [A/W]
      Meters are calibrated at one wavelength (1064 nm here), so using the head
      at another wavelength needs the correction factor
          k(lambda) = R(lambda_cal) / R(lambda)
      Saturates hard, so the linear ceiling matters.

Pulse trains: a thermal head reports *average* power only, so pulse energy is
recovered from the rep rate,
      E = P_avg / f_rep
which is how a 1.28 J, 10 Hz Nd:YAG shows up as 12.8 W on a thermopile.

Uncertainty: relative components are combined in quadrature (GUM style),
      u_c = sqrt(sum u_i^2),      U = k * u_c   (k = 2, ~95 %)

Run:
    python power_meter.py
    python power_meter.py --power-W 12.8 --lam-nm 532 --rep-rate-Hz 10
================================================================================
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field
from typing import Dict

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

H = 6.62607015e-34
C0 = 2.99792458e8
Q_E = 1.602176634e-19


# ------------------------------------------------------------------ heads
@dataclass
class ThermopileHead:
    """Broadband thermal head: slow, robust, density-limited."""

    responsivity_V_per_W: float = 0.25
    time_constant_s: float = 1.2
    max_power_W: float = 30.0
    max_density_W_per_cm2: float = 12.0
    noise_floor_W: float = 1e-3

    def signal_V(self, power_W: float, t_s: float | None = None) -> float:
        """Steady-state signal, or the transient at time t after the beam opens."""
        steady = self.responsivity_V_per_W * power_W
        if t_s is None:
            return steady
        if t_s <= 0.0:
            return 0.0
        return steady * (1.0 - math.exp(-t_s / self.time_constant_s))

    def settling_time_s(self, fraction: float = 0.99) -> float:
        """Time to reach `fraction` of the final reading (0 < fraction < 1)."""
        if not 0.0 < fraction < 1.0:
            raise ValueError("fraction must be in (0, 1)")
        return -self.time_constant_s * math.log(1.0 - fraction)

    def power_density_W_per_cm2(self, power_W: float, beam_diameter_mm: float) -> float:
        if beam_diameter_mm <= 0.0:
            raise ValueError("beam diameter must be > 0")
        radius_cm = 0.05 * beam_diameter_mm      # mm -> cm, then /2
        return power_W / (math.pi * radius_cm ** 2)

    def is_within_range(self, power_W: float) -> bool:
        return self.noise_floor_W < power_W <= self.max_power_W

    def is_density_safe(self, power_W: float, beam_diameter_mm: float) -> bool:
        return self.power_density_W_per_cm2(power_W, beam_diameter_mm) <= self.max_density_W_per_cm2


@dataclass
class PhotodiodeHead:
    """Fast, sensitive, wavelength-hungry head."""

    quantum_efficiency: float = 0.75
    calibration_lam_nm: float = 1064.0
    max_power_W: float = 50e-3
    noise_floor_W: float = 1e-9

    def responsivity_A_per_W(self, lam_nm: float) -> float:
        return self.quantum_efficiency * Q_E * (lam_nm * 1e-9) / (H * C0)

    def wavelength_correction(self, lam_nm: float) -> float:
        """Multiply a raw reading by this when off the calibration wavelength."""
        return self.responsivity_A_per_W(self.calibration_lam_nm) / self.responsivity_A_per_W(lam_nm)

    def current_A(self, power_W: float, lam_nm: float) -> float:
        return self.responsivity_A_per_W(lam_nm) * min(power_W, self.max_power_W)

    def is_saturated(self, power_W: float) -> bool:
        return power_W > self.max_power_W


# ------------------------------------------------------- uncertainty budget
@dataclass
class UncertaintyBudget:
    """Relative (fractional) standard uncertainties, combined in quadrature."""

    components: Dict[str, float] = field(default_factory=lambda: {
        "calibration transfer": 0.020,
        "wavelength correction": 0.010,
        "nonlinearity": 0.005,
        "spatial non-uniformity": 0.015,
        "noise & drift": 0.003,
    })
    coverage_factor: float = 2.0

    def combined_relative(self) -> float:
        return math.sqrt(sum(u * u for u in self.components.values()))

    def expanded_relative(self) -> float:
        return self.coverage_factor * self.combined_relative()

    def interval_W(self, reading_W: float) -> tuple[float, float]:
        half = reading_W * self.expanded_relative()
        return (reading_W - half, reading_W + half)

    def dominant(self) -> str:
        return max(self.components, key=lambda k: self.components[k])


# ------------------------------------------------------------- pulse trains
def pulse_energy_J(avg_power_W: float, rep_rate_Hz: float) -> float:
    if rep_rate_Hz <= 0.0:
        raise ValueError("rep rate must be > 0")
    return avg_power_W / rep_rate_Hz


def average_power_W(pulse_energy_J: float, rep_rate_Hz: float) -> float:
    return pulse_energy_J * rep_rate_Hz


# -------------------------------------------------------------------- report
def main():
    ap = argparse.ArgumentParser(description="Optical power meter: response, calibration, uncertainty")
    ap.add_argument("--power-W", type=float, default=12.8, help="incident average power")
    ap.add_argument("--lam-nm", type=float, default=1064.0)
    ap.add_argument("--rep-rate-Hz", type=float, default=10.0)
    ap.add_argument("--beam-mm", type=float, default=8.0, help="beam diameter at the head")
    args = ap.parse_args()

    th = ThermopileHead()
    pdh = PhotodiodeHead()
    ub = UncertaintyBudget()

    density = th.power_density_W_per_cm2(args.power_W, args.beam_mm)
    lo, hi = ub.interval_W(args.power_W)
    k = pdh.wavelength_correction(args.lam_nm)

    print("=" * 66)
    print(" Optical power meter")
    print("=" * 66)
    print(f"  incident            : {args.power_W:.3f} W @ {args.lam_nm:.0f} nm, {args.beam_mm:.1f} mm beam")
    print("  thermopile head")
    print(f"    steady signal     : {th.signal_V(args.power_W):.3f} V")
    print(f"    at t = tau        : {th.signal_V(args.power_W, th.time_constant_s):.3f} V (63 %)")
    print(f"    settles to 99 %   : {th.settling_time_s(0.99):.2f} s")
    print(f"    power density     : {density:.2f} W/cm^2 (limit {th.max_density_W_per_cm2:.1f})")
    print(f"    in range          : {'YES' if th.is_within_range(args.power_W) else 'OUT OF RANGE'}")
    print(f"    density safe      : {'YES' if th.is_density_safe(args.power_W, args.beam_mm) else 'RISK OF DAMAGE'}")
    print("  photodiode head")
    print(f"    responsivity      : {pdh.responsivity_A_per_W(args.lam_nm):.3f} A/W")
    print(f"    lambda correction : x{k:.3f} (cal @ {pdh.calibration_lam_nm:.0f} nm)")
    print(f"    saturated         : {'YES - attenuate' if pdh.is_saturated(args.power_W) else 'no'}")
    print("  pulse train")
    print(f"    pulse energy      : {pulse_energy_J(args.power_W, args.rep_rate_Hz):.4f} J @ {args.rep_rate_Hz:.0f} Hz")
    print("  uncertainty")
    for name, u in ub.components.items():
        print(f"    {name:<22}: {u * 100:.2f} %")
    print(f"    combined (u_c)    : {ub.combined_relative() * 100:.2f} %")
    print(f"    expanded (k=2)    : {ub.expanded_relative() * 100:.2f} %")
    print(f"    reading           : {args.power_W:.3f} W  [{lo:.3f}, {hi:.3f}] W")
    print(f"    dominant term     : {ub.dominant()}")
    print("=" * 66)

    if _HAVE_MPL:
        t = np.linspace(0.0, 6.0 * th.time_constant_s, 400)
        v = [th.signal_V(args.power_W, ti) for ti in t]
        plt.figure(figsize=(8, 4.2))
        plt.plot(t, v, lw=2, label="thermopile reading")
        plt.axhline(th.signal_V(args.power_W), ls="--", lw=1, color="k", label="true power")
        plt.axvline(th.settling_time_s(0.99), ls=":", color="r", label="99 % settled")
        plt.xlabel("time after shutter opens [s]")
        plt.ylabel("head signal [V]")
        plt.title("Thermal head step response (read too early, read too low)")
        plt.legend()
        plt.tight_layout()
        plt.savefig("power_meter.png", dpi=130)
        print("Saved -> power_meter.png")
        plt.show()


if __name__ == "__main__":
    main()
