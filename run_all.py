#!/usr/bin/env python3
"""
================================================================================
run_all.py  -  whole-platform smoke harness
================================================================================
The single most valuable thing for a 60+ file platform is PROOF that it all
actually runs. This harness imports every engine module and exercises one
representative call from each, then prints a green/red report. If any module has
a syntax error, a broken import, or a runtime bug, it shows up here immediately,
in one command, instead of being discovered later.

This is the "does the whole thing work?" button.

Run:
    python run_all.py
    python run_all.py --verbose
================================================================================
"""
from __future__ import annotations

import argparse
import importlib
import traceback
from typing import Callable, Dict, Tuple

# (module, callable that exercises it returning something truthy-ish)
SMOKE: Dict[str, Callable] = {}


def _reg(name):
    def deco(fn):
        SMOKE[name] = fn
        return fn
    return deco


@_reg("laser_platform")
def _s():
    from laser_platform import Cavity, FourLevelLaser
    return FourLevelLaser(Cavity()).steady_state()


@_reg("amplifier")
def _s():
    from amplifier import build_nilop_amplifier
    return build_nilop_amplifier().run()[-1].e_out_mJ


@_reg("shg")
def _s():
    from shg import SHGCrystal
    return SHGCrystal().efficiency(5e13)


@_reg("thg")
def _s():
    from thg import thg_chain
    return thg_chain(1.28, 200e-12, 0.8)["e_uv_mJ"]


@_reg("opcpa")
def _s():
    from opcpa import OPACrystal, opa_gain_nondepleted
    c = OPACrystal()
    return opa_gain_nondepleted(c.kappa(2e9), c.length_mm)


@_reg("cpa")
def _s():
    from cpa import GratingPair, separation_for_target
    return separation_for_target(GratingPair(), 100.0, 200.0)


@_reg("thermal_fem")
def _s():
    from thermal_fem import RodThermal, solve_radial_T
    return solve_radial_T(RodThermal(), 200.0)[1].max()


@_reg("thermal_abcd")
def _s():
    from thermal_abcd import ThermalRod
    return ThermalRod().focal_length(200.0)


@_reg("cooling")
def _s():
    from cooling import CoolingChannel
    return CoolingChannel().wall_rise(8, 200)


@_reg("reprate")
def _s():
    from reprate import RepRateThermal
    return RepRateThermal().max_rep_rate()


@_reg("depolarization")
def _s():
    from depolarization import DepolRod
    return DepolRod().depol_fraction(200)


@_reg("spatial_gain")
def _s():
    from spatial_gain import MODULES, extract
    return extract(MODULES["GM3"], 0.15)[1]


@_reg("beam_shaping")
def _s():
    from beam_shaping import run_pipeline
    return run_pipeline(110.0)[-1]


@_reg("relay_imaging")
def _s():
    from relay_imaging import q_from_w, w_from_q
    return w_from_q(q_from_w(3e-3))


@_reg("propagation")
def _s():
    from propagation import Medium, Window, initial_field, split_step
    return split_step(initial_field(Window(npix=64), I0=1e12), Medium(), Window(npix=64), 30)[1]


@_reg("temporal")
def _s():
    from temporal import PulseGrid, frantz_nodvik_temporal
    g = PulseGrid()
    return frantz_nodvik_temporal(g.input_shape(), g.time_axis(), 3.0, 1.0, 0.2)[1]


@_reg("gain_narrowing")
def _s():
    from gain_narrowing import GainLine
    return GainLine().delta_nu


@_reg("polarization")
def _s():
    from polarization import qwp, H, ellipticity
    return ellipticity(qwp(0.7853981634) @ H)


@_reg("ase")
def _s():
    from ase import ASERod
    return ASERod().max_storable_energy()


@_reg("damage")
def _s():
    from damage import audit_chain, headroom
    return headroom(audit_chain())


@_reg("safety")
def _s():
    from safety import BeamHazard
    return BeamHazard().nohd_m()


@_reg("jitter")
def _s():
    from jitter import SyncModel
    return SyncModel().energy_rms(20)


@_reg("autocorrelation")
def _s():
    from autocorrelation import Autocorrelator
    return Autocorrelator().measured_duration()


@_reg("contrast")
def _s():
    from contrast import PulseContrast
    return PulseContrast().contrast_at(-5.0)


@_reg("frog")
def _s():
    from frog import FROG
    return FROG(npts=48).trace_tilt()


@_reg("efficiency")
def _s():
    from efficiency import default_budget
    return default_budget().total_eta


@_reg("beam_quality")
def _s():
    from beam_quality import BeamQuality
    return BeamQuality(m2=1.8).bpp


@_reg("wavefront")
def _s():
    from wavefront import Wavefront
    return Wavefront({"defocus": 0.1}).strehl()


@_reg("adaptive_optics")
def _s():
    from wavefront import Wavefront
    from adaptive_optics import DeformableMirror
    return DeformableMirror().correct(Wavefront({"defocus": 0.1})).strehl()


@_reg("pointing")
def _s():
    from pointing import Pointing
    return Pointing().hit_probability(1000, 0.1)


@_reg("ranging")
def _s():
    from ranging import RangingLink
    return RangingLink().photons_returned(1000e3)


@_reg("ablation")
def _s():
    from ablation import Ablator, MATERIALS
    return Ablator(MATERIALS["steel"]).depth_per_pulse_nm(2.0)


@_reg("plasma")
def _s():
    from plasma import LaserPlasma
    return LaserPlasma().intensity_Wcm2()


@_reg("dermatology")
def _s():
    from dermatology import DermaTreatment
    return DermaTreatment().thermal_relaxation_s()


@_reg("raman")
def _s():
    from raman import SRS, MEDIA
    return SRS(MEDIA["air"]).gain_exponent(5e13, 2)


@_reg("regen")
def _s():
    from regen import Regen
    return Regen().optimum_dump()[1]


@_reg("seed")
def _s():
    from seed import MicrochipSeed
    return MicrochipSeed().pulse_duration_s()


@_reg("pump_diode")
def _s():
    from pump_diode import DiodeBar
    return DiodeBar().absorbed_pump(120)


@_reg("pump_absorption")
def _s():
    from pump_absorption import PumpAbsorption
    return PumpAbsorption().absorbed_fraction()


@_reg("materials")
def _s():
    from materials import get
    return get("Nd:YAG").quantum_defect


@_reg("dispersion")
def _s():
    from dispersion import MATERIALS
    return MATERIALS["YAG"].n(1064.0)


@_reg("storage")
def _s():
    from storage import Storage
    return Storage().efficiency(200)


@_reg("cavity_modes")
def _s():
    from cavity_modes import CavityModes
    return CavityModes().mode_count()


@_reg("walkoff")
def _s():
    from walkoff import WalkOff
    return WalkOff().overlap_fraction()


@_reg("phase_matching")
def _s():
    from phase_matching import PhaseMatch
    return PhaseMatch().angular_acceptance_mrad()


@_reg("pockels")
def _s():
    from pockels import PockelsCell
    return PockelsCell().half_wave_voltage()


@_reg("isolator")
def _s():
    from isolator import FaradayIsolator
    iso = FaradayIsolator()
    iso.field_T = iso.field_for_45deg()
    return iso.isolation_dB()


@_reg("breakdown")
def _s():
    from breakdown import FocusBreakdown
    return FocusBreakdown().max_safe_pressure_mbar()


@_reg("coatings")
def _s():
    from coatings import reflectivity, hr_stack
    return reflectivity(hr_stack(1064, 2.3, 1.45, 15), 1064, n_substrate=1.52)


@_reg("detectors")
def _s():
    from detectors import Photodiode
    return Photodiode().responsivity(1064)


@_reg("noise")
def _s():
    from noise import NoiseModel
    return NoiseModel().peak_amplification_dB()


@_reg("prism_compressor")
def _s():
    from prism_compressor import PrismCompressor
    return PrismCompressor().net_gdd_fs2(50)


@_reg("beam_combining")
def _s():
    from beam_combining import BeamCombiner
    return BeamCombiner().combined_energy_J(8)


@_reg("sensitivity")
def _s():
    from sensitivity import default_params, monte_carlo
    return monte_carlo(default_params(), n=200).mean()


@_reg("landscape")
def _s():
    from landscape import published_systems
    return len(published_systems())


@_reg("config")
def _s():
    from config import build_from_config, NILOP_CONFIG
    return build_from_config(NILOP_CONFIG).run()[-1].e_out_mJ


@_reg("full_system")
def _s():
    from full_system import run_full_system
    return run_full_system()[-1].e_out_mJ


@_reg("chain_e2e")
def _s():
    from chain_e2e import run
    return run("green", "ranging")[1]


def main():
    ap = argparse.ArgumentParser(description="Whole-platform smoke harness")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print("=" * 64)
    print(f" LASERSIM smoke harness  ({len(SMOKE)} engines)")
    print("=" * 64)
    ok, fail = 0, 0
    for name, fn in SMOKE.items():
        try:
            result = fn()
            ok += 1
            mark = "OK  "
            detail = f" -> {result}" if args.verbose else ""
        except Exception as e:
            fail += 1
            mark = "FAIL"
            detail = f"  {type(e).__name__}: {e}"
            if args.verbose:
                detail += "\n" + traceback.format_exc()
        print(f"  [{mark}] {name}{detail}")
    print("-" * 64)
    print(f"  {ok}/{ok+fail} engines ran clean")
    print("=" * 64)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
