"""forward_model.py -- unified design -> metrics forward map for lasersim.

This is the *contract layer* the novelty engines (inverse_design.py,
surrogate.py) sit on top of. It exposes a single clean function:

    simulate(design: dict) -> metrics: dict

where `design` is a handful of physical knobs a laser engineer actually
turns, and `metrics` are the numbers a professor / spec sheet cares about.

The physics here is deliberately textbook-honest (Silfvast, Laser
Fundamentals 2e): Frantz-Nodvik saturated amplification, gain-narrowed
transform-limited duration with residual-GDD broadening, thermally driven
beam-quality (M^2) degradation, and tanh^2 second-harmonic conversion. It
runs standalone on pure numpy so it always works in --smoke.

If the full lasersim engine chain is importable and --full is requested,
simulate() will (best-effort) route through laser_platform for the
high-fidelity numbers; otherwise it uses the reference model below. Either
way the design->metrics *interface* is identical, which is what makes the
inverse-design and surrogate layers general.

All SI unless a name says otherwise.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from typing import Dict

# ------------------------------------------------------------------
# Physical constants
# ------------------------------------------------------------------
H_PLANCK = 6.62607015e-34      # J s
C_LIGHT = 2.99792458e8         # m / s

# ------------------------------------------------------------------
# Design space -- the knobs an operator actually turns.
# Bounds are physically sane for a diode-pumped Nd:YAG-class CPA front end.
# ------------------------------------------------------------------
DESIGN_BOUNDS: Dict[str, tuple] = {
    "pump_power_w":       (5.0,   400.0),   # diode pump power [W]
    "crystal_length_cm":  (0.2,    8.0),    # gain medium length [cm]
    "seed_energy_nj":     (0.1,  5000.0),   # injected seed pulse energy [nJ]
    "residual_gdd_fs2":   (0.0, 60000.0),   # uncompensated GDD after compressor [fs^2]
    "shg_length_mm":      (0.0,   20.0),    # doubling-crystal length [mm]; 0 = no SHG
}

# ------------------------------------------------------------------
# Fixed system parameters (the bench you didn't get to choose).
# ------------------------------------------------------------------
@dataclass
class SystemParams:
    wavelength_nm: float = 1064.0          # Nd:YAG fundamental
    sigma_em_cm2: float = 2.8e-19          # stimulated-emission cross section
    tau_upper_us: float = 230.0            # upper-state lifetime
    beam_radius_mm: float = 1.5            # 1/e^2 radius in the rod
    tl_bandwidth_nm: float = 0.5           # gain-narrowed emission bandwidth
    rod_conductivity: float = 14.0         # W/(m K), YAG thermal conductivity
    eta_pump: float = 0.42                 # pump -> upper-state storage efficiency
    rep_rate_hz: float = 1000.0            # amplifier rep rate
    damage_fluence_j_cm2: float = 10.0     # coating/bulk damage threshold
    shg_deff_pm_v: float = 8.3             # effective nonlinear coeff (LBO-ish)
    shg_phase_mismatch: float = 0.0        # dk*L/2 residual (0 = perfectly matched)


def _clip(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def clamp_design(design: Dict[str, float]) -> Dict[str, float]:
    """Project a (possibly out-of-bounds) design into the legal box."""
    out = {}
    for k, (lo, hi) in DESIGN_BOUNDS.items():
        out[k] = float(_clip(float(design.get(k, 0.5 * (lo + hi))), lo, hi))
    return out


def default_design() -> Dict[str, float]:
    """A reasonable mid-box starting design."""
    return {k: 0.5 * (lo + hi) for k, (lo, hi) in DESIGN_BOUNDS.items()}


# ------------------------------------------------------------------
# Reference (pure-numpy-free) forward model
# ------------------------------------------------------------------
def _simulate_reference(design: Dict[str, float], sp: SystemParams) -> Dict[str, float]:
    d = clamp_design(design)
    pump = d["pump_power_w"]
    L_cm = d["crystal_length_cm"]
    seed_J = d["seed_energy_nj"] * 1e-9
    residual_gdd = d["residual_gdd_fs2"]
    shg_mm = d["shg_length_mm"]

    # --- effective area & saturation fluence (Frantz-Nodvik) ---
    w = sp.beam_radius_mm * 1e-3               # m
    area_cm2 = math.pi * (w * 100.0) ** 2      # cm^2 (mode area)
    nu = C_LIGHT / (sp.wavelength_nm * 1e-9)   # Hz
    F_sat = (H_PLANCK * nu) / sp.sigma_em_cm2  # J/cm^2 saturation fluence
    E_sat = F_sat * area_cm2                    # J saturation energy

    # --- stored energy -> small-signal gain ---
    # Energy stored in the upper state during one pump interval, capped by lifetime.
    t_store = min(1.0 / sp.rep_rate_hz, sp.tau_upper_us * 1e-6)
    E_store = sp.eta_pump * pump * t_store      # J available
    # small-signal gain grows with stored energy density and length
    g0L = (E_store / E_sat) * (L_cm / 4.0)
    g0L = _clip(g0L, 0.0, 30.0)
    G0 = math.exp(g0L)

    # --- Frantz-Nodvik saturated extraction ---
    # E_out = E_sat * ln(1 + G0 (exp(E_in/E_sat) - 1))
    x = _clip(seed_J / E_sat, 0.0, 50.0)
    E_out = E_sat * math.log1p(G0 * (math.expm1(x)))
    # can't extract more than stored + seed
    E_out = min(E_out, E_store + seed_J)
    out_fluence = E_out / area_cm2

    # --- pulse duration: transform limit * residual-GDD broadening ---
    dnu = (C_LIGHT * sp.tl_bandwidth_nm * 1e-9) / (sp.wavelength_nm * 1e-9) ** 2  # Hz
    tau_tl_s = 0.441 / dnu                       # Gaussian TL duration [s]
    tau_tl_fs = tau_tl_s * 1e15
    broaden = math.sqrt(1.0 + (4.0 * math.log(2.0) * residual_gdd / (tau_tl_fs ** 2)) ** 2)
    tau_fs = tau_tl_fs * broaden
    tau_s = tau_fs * 1e-15
    peak_power_w = 0.94 * E_out / tau_s          # Gaussian peak power

    # --- beam quality: thermal lensing degrades M^2 with heat load ---
    heat_load_w = (1.0 - sp.eta_pump) * pump     # fraction dumped as heat
    thermal_index = heat_load_w / (sp.rod_conductivity * (w) * 1e3)
    M2 = 1.0 + 0.015 * thermal_index
    M2 = _clip(M2, 1.0, 25.0)

    # --- SHG: tanh^2 conversion driven by fundamental intensity ---
    shg_eff = 0.0
    if shg_mm > 1e-6 and peak_power_w > 0:
        I_fund = peak_power_w / (area_cm2 * 1e-4)          # W/m^2
        kappa = 2.0e-6 * sp.shg_deff_pm_v                 # lumped nonlinear drive
        drive = kappa * math.sqrt(max(I_fund, 0.0)) * (shg_mm * 1e-3)
        mism = 1.0 / (1.0 + sp.shg_phase_mismatch ** 2)
        shg_eff = (math.tanh(drive) ** 2) * mism
    shg_eff = _clip(shg_eff, 0.0, 0.85)

    # --- damage constraint ---
    damage_margin = sp.damage_fluence_j_cm2 - out_fluence   # >0 == safe
    safe = damage_margin > 0.0

    return {
        "output_energy_j": E_out,
        "output_fluence_j_cm2": out_fluence,
        "pulse_duration_fs": tau_fs,
        "peak_power_w": peak_power_w if safe else peak_power_w,
        "m2": M2,
        "shg_efficiency": shg_eff,
        "green_energy_j": E_out * shg_eff,
        "small_signal_gain": G0,
        "damage_margin_j_cm2": damage_margin,
        "damage_safe": 1.0 if safe else 0.0,
    }


def _simulate_full(design: Dict[str, float], sp: SystemParams):
    """Best-effort route through the full engine chain. Returns None if the
    platform API isn't importable/compatible, so callers fall back cleanly."""
    try:
        import laser_platform  # noqa: F401
    except Exception:
        return None
    # The full chain has its own config surface which we don't hard-couple to
    # here; if a compatible entrypoint exists, use it. Kept defensive on
    # purpose so this module never breaks the standalone --smoke path.
    fn = getattr(laser_platform, "simulate_design", None)
    if callable(fn):
        try:
            return dict(fn(clamp_design(design)))
        except Exception:
            return None
    return None


def simulate(design: Dict[str, float], sp: SystemParams | None = None,
             full: bool = False) -> Dict[str, float]:
    """Map a design dict to a metrics dict. See module docstring."""
    sp = sp or SystemParams()
    if full:
        res = _simulate_full(design, sp)
        if res is not None:
            return res
    return _simulate_reference(design, sp)


# ------------------------------------------------------------------
# Smoke test
# ------------------------------------------------------------------
def _smoke() -> int:
    print("[forward_model] smoke: design -> metrics")
    d = default_design()
    m = simulate(d)
    for k, v in m.items():
        print(f"    {k:24s} = {v:.6g}")
    # sanity: more pump must not reduce output energy (monotone gain)
    d2 = dict(d); d2["pump_power_w"] = DESIGN_BOUNDS["pump_power_w"][1]
    m2 = simulate(d2)
    assert m2["output_energy_j"] >= m["output_energy_j"] - 1e-12, "gain not monotone in pump"
    # sanity: zero SHG length -> zero green
    d3 = dict(d); d3["shg_length_mm"] = 0.0
    assert simulate(d3)["shg_efficiency"] == 0.0, "SHG should vanish at zero length"
    # sanity: more residual GDD -> longer pulse
    d4 = dict(d); d4["residual_gdd_fs2"] = DESIGN_BOUNDS["residual_gdd_fs2"][1]
    assert simulate(d4)["pulse_duration_fs"] >= m["pulse_duration_fs"], "GDD should broaden"
    print("[forward_model] smoke OK")
    return 0


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_smoke())
