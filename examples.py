#!/usr/bin/env python3
"""
================================================================================
examples.py  -  a guided, end-to-end tour of the LASERSIM platform
================================================================================
This is the on-ramp. Instead of 20 separate scripts, this walks through the
whole platform in the order an optical engineer would actually think about a
high-energy picosecond amplifier, printing a short, readable result at each
step and pointing at the engine that produced it.

It's the file you run first to understand what LASERSIM can do, and the file you
show someone when you want them to get it in 60 seconds.

Run:
    python examples.py            # full guided tour
    python examples.py --step 3   # run just one step
================================================================================
"""
from __future__ import annotations

import argparse


def step1_oscillator():
    print("\n[1] OSCILLATOR  (laser_platform.py)")
    print("    How the seed laser turns on: inversion builds, clamps at threshold,")
    print("    photon density rings down through relaxation oscillations.")
    from laser_platform import Cavity, FourLevelLaser
    cav = Cavity()
    N_ss, S_ss = FourLevelLaser(cav).steady_state()
    print(f"    -> pump ratio r = {cav.r:.1f}, relaxation freq "
          f"{cav.relaxation_freq_hz()/1e3:.1f} kHz")


def step2_amplifier():
    print("\n[2] AMPLIFIER CHAIN  (amplifier.py)")
    print("    Frantz-Nodvik extraction through AMP-1/2/3 -> 1.28 J.")
    from amplifier import build_nilop_amplifier
    for r in build_nilop_amplifier().run():
        print(f"    {r.name:<30} {r.e_out_mJ:>7.0f} mJ   B={r.b_integral:.2f}")


def step3_spatial():
    print("\n[3] SPATIAL GAIN  (spatial_gain.py)")
    print("    Non-uniform pump -> non-uniform gain imprinted on the beam.")
    from spatial_gain import MODULES, extract
    rod = MODULES["GM3"]
    E_in, E_out, _, _ = extract(rod, 0.15)
    print(f"    -> GM3 (petal pump) gain {E_out/E_in:.2f}x")


def step4_beam_relay():
    print("\n[4] BEAM SHAPING + RELAY  (beam_shaping.py, relay_imaging.py)")
    print("    Serrated aperture + spatial filter clean the beam; relays expand it.")
    from beam_shaping import run_pipeline
    *_, m = run_pipeline(pinhole_um=110.0)
    print(f"    -> ripple {m['ripple_in']:.2f} -> {m['ripple_out']:.2f}, "
          f"SA T={m['SA_transmission']*100:.0f}%")
    from relay_imaging import q_from_w, w_from_q, propagate, build_nilop_relays
    q = q_from_w(3e-3)
    for relay in build_nilop_relays():
        q, _ = propagate(q, relay.elements())
    print(f"    -> booster beam diameter {2*w_from_q(q)*1e3:.0f} mm (paper 16 mm)")


def step5_nonlinear_thermal():
    print("\n[5] SELF-FOCUSING + THERMAL  (propagation.py, thermal_fem.py)")
    print("    Kerr self-focusing risk and the rod's thermal lens / stress.")
    from thermal_fem import RodThermal, solve_radial_T, thermal_focal_length, peak_stress_MPa
    rod = RodThermal()
    r, T = solve_radial_T(rod, 200.0)
    print(f"    -> 200 W heat: center +{T.max()-rod.T_coolant:.0f} K, "
          f"f_th {thermal_focal_length(rod, r, T)*100:.0f} cm, "
          f"stress {peak_stress_MPa(rod, r, T):.0f} MPa")


def step6_safety():
    print("\n[6] SAFETY LIMITS  (ase.py, damage.py)")
    print("    What stops you pushing more energy: parasitics + optical damage.")
    from ase import ASERod
    from damage import audit_chain, headroom
    print(f"    -> parasitic loop gain @1.14 J: {ASERod(diameter_m=25e-3).parasitic_margin(1.14):.2f}")
    print(f"    -> tightest LIDT margin: {headroom(audit_chain()):.2f}x")


def step7_opcpa():
    print("\n[7] OPCPA FRONT-END  (opcpa.py)")
    print("    What this 1.28 J pump was built for: pumping a parametric amplifier.")
    from opcpa import OPACrystal, opa_gain_nondepleted
    c = OPACrystal(length_mm=15.0)
    g = c.kappa(5e9)
    print(f"    -> signal gain {opa_gain_nondepleted(g, 15.0):.1e}x, "
          f"idler {c.lam_idler_nm:.0f} nm")


def step8_validate():
    print("\n[8] VALIDATION  (validate.py)")
    print("    One scorecard: does the whole platform still match the paper?")
    from validate import CHECKS
    n = sum(fn().passed for fn in CHECKS)
    print(f"    -> {n}/{len(CHECKS)} cross-engine checks pass")


STEPS = [step1_oscillator, step2_amplifier, step3_spatial, step4_beam_relay,
         step5_nonlinear_thermal, step6_safety, step7_opcpa, step8_validate]


def main():
    ap = argparse.ArgumentParser(description="Guided tour of LASERSIM")
    ap.add_argument("--step", type=int, default=0, help="run only this step (1-8)")
    args = ap.parse_args()
    print("=" * 66)
    print(" LASERSIM guided tour  -  NILOP 1.28 J / 200 ps Nd:YAG, end to end")
    print("=" * 66)
    if args.step:
        STEPS[args.step - 1]()
    else:
        for s in STEPS:
            s()
    print("\n" + "=" * 66)
    print(" Done. See README.md for every engine, or run:  python validate.py")
    print("=" * 66)


if __name__ == "__main__":
    main()
