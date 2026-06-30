#!/usr/bin/env python3
"""
================================================================================
amplifier.py  -  Frantz-Nodvik multi-pass laser amplifier engine
================================================================================
Models energy extraction, super-Gaussian beam fluence, peak intensity, and the
B-integral (self-focusing safety metric) for solid-state amplifier chains.

Ships with a built-in reproduction of:

  "An all-diode pumped 1.28-Joule, 200-picosecond Nd:YAG laser amplifier at
   10 Hz", K. Raza et al., Optics Communications 577 (2025) 131413
   (NILOP College, PIEAS, Islamabad).

Run directly to print the modeled chain next to the paper's measured values.

Core physics
------------
  Frantz-Nodvik (energy fluence form):
      F_out = F_sat * ln( 1 + G0 * (exp(F_in / F_sat) - 1) )
      G0    = exp(F_store / F_sat)          # small-signal gain

  Super-Gaussian beam of order n:
      I(x,y) = I0 * exp(-2 (x/wx)^n) * exp(-2 (y/wy)^n)
      F0     = 2^(2/n) * E / (pi * wx * wy)     # peak fluence
      I0     = 0.937 * F0 / tau_p                # peak intensity

  B-integral (per pass through a rod of length L):
      B = (2*pi/lambda) * n2 * I0 * L
  Circular polarization reduces n2 by a factor 2/3.
================================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

# --- constants ----------------------------------------------------------------
LAMBDA = 1064e-7          # wavelength [cm]  (1064 nm)
N2_LINEAR = 6.21e-16      # nonlinear index n2 of Nd:YAG [cm^2/W], linear pol.
CIRC_FACTOR = 2.0 / 3.0   # n2 reduction for circular polarization


# ==============================================================================
# BEAM
# ==============================================================================
@dataclass
class SuperGaussianBeam:
    """Round super-Gaussian beam. radius_cm is the 1/e^2 radius (w)."""
    energy_J: float
    radius_cm: float
    order_n: int = 2          # 2 = Gaussian, 4/6 = flatter top
    tau_p_s: float = 200e-12  # pulse duration (FWHM) [s]

    @property
    def area_cm2(self) -> float:
        return np.pi * self.radius_cm ** 2

    @property
    def avg_fluence(self) -> float:
        """Energy / area  [J/cm^2]."""
        return self.energy_J / self.area_cm2

    @property
    def peak_fluence(self) -> float:
        """Peak fluence F0 of an n-th order super-Gaussian [J/cm^2]."""
        wx = wy = self.radius_cm
        return (2.0 ** (2.0 / self.order_n)) * self.energy_J / (np.pi * wx * wy)

    @property
    def peak_intensity(self) -> float:
        """Peak intensity I0 [W/cm^2]."""
        return 0.937 * self.peak_fluence / self.tau_p_s


# ==============================================================================
# GAIN MODULE
# ==============================================================================
@dataclass
class GainModule:
    """A diode-pumped rod amplifier head."""
    name: str
    rod_diameter_cm: float
    rod_length_cm: float
    stored_energy_J: float        # E_store at operating current
    f_sat: float = 0.3            # saturation fluence [J/cm^2] (few-100 ps Nd:YAG)

    @property
    def rod_area_cm2(self) -> float:
        return np.pi * (self.rod_diameter_cm / 2.0) ** 2

    @property
    def stored_fluence(self) -> float:
        """F_store averaged over rod area [J/cm^2]."""
        return self.stored_energy_J / self.rod_area_cm2

    def small_signal_gain(self, f_store: Optional[float] = None) -> float:
        fs = self.stored_fluence if f_store is None else f_store
        return np.exp(fs / self.f_sat)


# ==============================================================================
# FRANTZ-NODVIK PASS
# ==============================================================================
def frantz_nodvik(f_in: float, g0: float, f_sat: float) -> float:
    """Output fluence [J/cm^2] for a single pass."""
    return f_sat * np.log(1.0 + g0 * (np.expm1(f_in / f_sat)))


def b_integral(peak_intensity: float, length_cm: float, circular: bool) -> float:
    n2 = N2_LINEAR * (CIRC_FACTOR if circular else 1.0)
    return (2.0 * np.pi / LAMBDA) * n2 * peak_intensity * length_cm


# ==============================================================================
# AMPLIFIER STAGE
# ==============================================================================
@dataclass
class StageResult:
    name: str
    e_in_mJ: float
    e_out_mJ: float
    gain: float
    peak_fluence: float
    b_integral: float


@dataclass
class AmplifierStage:
    """One amplifier (1 or 2 passes, possibly more than one module in series)."""
    name: str
    modules: List[GainModule]
    passes: int = 1
    beam_radius_cm: float = 0.35
    beam_order_n: int = 2
    circular_pol: bool = True
    tau_p_s: float = 200e-12

    def run(self, e_in_J: float) -> Tuple[float, StageResult]:
        f_sat = self.modules[0].f_sat
        f_store = self.modules[0].stored_fluence
        beam_area = np.pi * self.beam_radius_cm ** 2
        f = e_in_J / beam_area
        worst_B = 0.0
        # multiple modules in series, then multiple passes
        for _pass in range(self.passes):
            for m in self.modules:
                g0 = np.exp(f_store / f_sat)
                f_out = frantz_nodvik(f, g0, f_sat)
                # deplete stored fluence by what we extracted
                f_store = max(f_store - (f_out - f), 0.0)
                f = f_out
                beam = SuperGaussianBeam(f * beam_area, self.beam_radius_cm,
                                         self.beam_order_n, self.tau_p_s)
                worst_B = max(worst_B, b_integral(beam.peak_intensity,
                                                  m.rod_length_cm,
                                                  self.circular_pol))
        e_out_J = f * beam_area
        beam = SuperGaussianBeam(e_out_J, self.beam_radius_cm,
                                 self.beam_order_n, self.tau_p_s)
        res = StageResult(self.name, e_in_J * 1e3, e_out_J * 1e3,
                          e_out_J / e_in_J, beam.peak_fluence, worst_B)
        return e_out_J, res


@dataclass
class PassiveLoss:
    """A lossy element between stages (serrated aperture, spatial filter, etc.)."""
    name: str
    transmission: float   # 0..1

    def run(self, e_in_J: float) -> Tuple[float, StageResult]:
        e_out = e_in_J * self.transmission
        return e_out, StageResult(self.name, e_in_J * 1e3, e_out * 1e3,
                                  self.transmission, 0.0, 0.0)


# ==============================================================================
# AMPLIFIER CHAIN
# ==============================================================================
@dataclass
class AmplifierChain:
    name: str
    seed_energy_J: float
    elements: list = field(default_factory=list)

    def run(self) -> List[StageResult]:
        e = self.seed_energy_J
        out = []
        for el in self.elements:
            e, res = el.run(e)
            out.append(res)
        return out


# ==============================================================================
# BUILT-IN: NILOP 1.28 J, 200 ps Nd:YAG amplifier (Raza et al. 2025)
# ==============================================================================
def build_nilop_amplifier() -> AmplifierChain:
    # GM1/GM2: 15 mm dia, 130 mm, E_store = 1.622 J
    # GM3/GM4: 25 mm dia, 130 mm, E_store = 1.14 J
    gm1 = GainModule("GM1", 1.5, 13.0, 1.622)
    gm2 = GainModule("GM2", 1.5, 13.0, 1.622)
    gm3 = GainModule("GM3", 2.5, 13.0, 1.14)
    gm4 = GainModule("GM4", 2.5, 13.0, 1.14)

    return AmplifierChain(
        name="NILOP 1.28 J / 200 ps Nd:YAG",
        seed_energy_J=0.015,   # 15 mJ injected into AMP-1
        elements=[
            AmplifierStage("AMP-1 (GM1, 2-pass)", [gm1], passes=2,
                           beam_radius_cm=0.35, beam_order_n=2),
            PassiveLoss("Serrated aperture (SA)", 0.80),   # 20% clipped
            AmplifierStage("AMP-2 (GM2, 2-pass)", [gm2], passes=2,
                           beam_radius_cm=0.50, beam_order_n=4),
            PassiveLoss("Spatial filter SF2", 0.88),
            AmplifierStage("AMP-3 (GM3+GM4, 1-pass)", [gm3, gm4], passes=1,
                           beam_radius_cm=0.80, beam_order_n=4),
        ],
    )


# Paper's measured output energies for comparison [mJ], keyed by stage name
PAPER_MEASURED = {
    "AMP-1 (GM1, 2-pass)": 200.0,
    "Serrated aperture (SA)": 160.0,
    "AMP-2 (GM2, 2-pass)": 755.0,
    "Spatial filter SF2": None,
    "AMP-3 (GM3+GM4, 1-pass)": 1280.0,
}
PAPER_B = {"GM1": 1.55, "GM2": 1.94, "GM3": 1.0, "GM4": 1.28}


def main() -> None:
    chain = build_nilop_amplifier()
    results = chain.run()

    print("=" * 78)
    print(f" {chain.name}")
    print(f" seed = {chain.seed_energy_J*1e3:.0f} mJ   target = 1280 mJ @ 200 ps, 10 Hz")
    print("=" * 78)
    hdr = f"{'stage':<30}{'E_in':>9}{'E_out':>10}{'gain':>8}{'Fpk':>9}{'B':>7}"
    print(hdr)
    print("-" * 78)
    for r in results:
        meas = PAPER_MEASURED.get(r.name)
        print(f"{r.name:<30}{r.e_in_mJ:>9.0f}{r.e_out_mJ:>10.0f}"
              f"{r.gain:>8.2f}{r.peak_fluence:>9.2f}{r.b_integral:>7.2f}"
              + (f"   (paper: {meas:.0f} mJ)" if meas else ""))
    print("-" * 78)
    final = results[-1].e_out_mJ
    print(f" modeled final output: {final:.0f} mJ   (paper measured: 1280 mJ)")
    print(f" peak B-integral stays {'WITHIN' if max(r.b_integral for r in results) < 3 else 'ABOVE'}"
          f" the safe ~3 rad limit.")
    print("=" * 78)


if __name__ == "__main__":
    main()
