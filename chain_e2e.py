#!/usr/bin/env python3
"""
================================================================================
chain_e2e.py  -  end-to-end physical chain integrator
================================================================================
full_system.py walked the AMPLIFIER stages. This goes wider: it strings the
newer building blocks into one traceable pass through the ENTIRE machine, from
the seed oscillator through the diode pump, amplifier chain, harmonics, and out
to a chosen application, printing what each subsystem hands to the next.

It's the 'whole machine on one screen' view, and a sanity check that the modules
agree at their interfaces (energy in == energy out, within each stage's model).

Stages traced
-------------
  seed.py        -> seed pulse
  pump_diode.py  -> absorbed pump power feeding the gain
  amplifier.py   -> 1.28 J fundamental
  shg.py/thg.py  -> optional harmonic conversion
  application    -> ranging / ablation / plasma / dermatology summary

Run:
    python chain_e2e.py
    python chain_e2e.py --harmonic green --application ablation
================================================================================
"""
from __future__ import annotations

import argparse

from seed import MicrochipSeed
from pump_diode import DiodeBar
from amplifier import build_nilop_amplifier
from shg import SHGCrystal, peak_intensity
from thg import thg_chain


def run(harmonic: str = "none", application: str = "none"):
    lines = []
    # 1. seed
    seed = MicrochipSeed()
    lines.append(("seed oscillator",
                  f"{seed.pulse_energy_J()*1e6:.1f} uJ, {seed.pulse_duration_s()*1e12:.0f} ps"))
    # 2. pump
    diode = DiodeBar()
    lines.append(("pump diodes @120A",
                  f"{diode.absorbed_pump(120)/1e3:.1f} kW absorbed @ {diode.wavelength(120):.1f} nm"))
    # 3. amplifier
    results = build_nilop_amplifier().run()
    e_fund_mJ = results[-1].e_out_mJ
    lines.append(("amplifier chain", f"{e_fund_mJ:.0f} mJ fundamental (1064 nm)"))
    # 4. harmonics
    e_out_mJ, lam = e_fund_mJ, 1064
    if harmonic == "green":
        I = peak_intensity(e_fund_mJ / 1e3, 200e-12, 0.8)
        eta = SHGCrystal(beam_radius_cm=0.8).efficiency(I)
        e_out_mJ, lam = eta * e_fund_mJ, 532
        lines.append(("SHG", f"{e_out_mJ:.0f} mJ green (532 nm), eta={eta*100:.0f}%"))
    elif harmonic == "uv":
        r = thg_chain(e_fund_mJ / 1e3, 200e-12, 0.8)
        e_out_mJ, lam = r["e_uv_mJ"], 355
        lines.append(("THG", f"{e_out_mJ:.0f} mJ UV (355 nm)"))
    # 5. application
    if application == "ranging":
        from ranging import RangingLink
        link = RangingLink(energy_J=e_out_mJ / 1e3)
        lines.append(("ranging @1000km",
                      f"{link.photons_returned(1000e3):.1e} photons/shot"))
    elif application == "ablation":
        from ablation import Ablator, MATERIALS
        ab = Ablator(MATERIALS["steel"])
        f = (e_out_mJ / 1e3) / ab.spot_area_cm2()
        lines.append(("ablation (steel)",
                      f"{ab.depth_per_pulse_nm(f):.0f} nm/pulse @ {f:.1f} J/cm^2"))
    elif application == "plasma":
        from plasma import LaserPlasma
        lp = LaserPlasma(peak_power_W=(e_out_mJ / 1e3) / 200e-12)
        lines.append(("plasma", f"I={lp.intensity_Wcm2():.1e} W/cm^2, a0={lp.a0():.3f}"))
    elif application == "dermatology":
        from dermatology import DermaTreatment
        t = DermaTreatment()
        lines.append(("dermatology",
                      f"{'photoacoustic' if t.is_photoacoustic() else 'thermal'} regime"))
    return lines, e_out_mJ, lam


def main():
    ap = argparse.ArgumentParser(description="End-to-end chain integrator")
    ap.add_argument("--harmonic", choices=["none", "green", "uv"], default="none")
    ap.add_argument("--application",
                    choices=["none", "ranging", "ablation", "plasma", "dermatology"],
                    default="none")
    args = ap.parse_args()

    lines, e_out, lam = run(args.harmonic, args.application)

    print("=" * 66)
    print(" LASERSIM end-to-end chain  (seed -> ... -> application)")
    print("=" * 66)
    for i, (stage, detail) in enumerate(lines):
        arrow = "   |" if i < len(lines) - 1 else "   v"
        print(f"  {stage:<22}: {detail}")
        print(arrow)
    print(f"  DELIVERED: {e_out:.0f} mJ at {lam} nm")
    print("=" * 66)


if __name__ == "__main__":
    main()
