#!/usr/bin/env python3
"""
================================================================================
cli.py  -  unified command-line entry point for the whole LASERSIM platform
================================================================================
One command to drive every engine. Install with `pip install -e .` then run
`lasersim <engine> [args]`. See `lasersim info` for the full list.

Every runnable module in the repo root must appear in ENGINES - if it is missing
here it is dead code from the user's point of view.
================================================================================
"""
from __future__ import annotations

import argparse
import runpy
import subprocess
import sys
from typing import List, Optional

ENGINES = {
    # gain dynamics
    "oscillator": "laser_platform",
    "amplifier": "amplifier",
    "regen": "regen",
    "spatial": "spatial_gain",
    "temporal": "temporal",
    "gain-narrowing": "gain_narrowing",
    "storage": "storage",
    "seed": "seed",
    "cavity-modes": "cavity_modes",
    # pump / thermal
    "pump": "pump_diode",
    "pump-absorption": "pump_absorption",
    "thermal": "thermal_abcd",
    "thermal-fem": "thermal_fem",
    "cooling": "cooling",
    "reprate": "reprate",
    "depolarization": "depolarization",
    # beam / propagation
    "beam": "beam_shaping",
    "beam-combining": "beam_combining",
    "relay": "relay_imaging",
    "propagation": "propagation",
    "beam-quality": "beam_quality",
    "wavefront": "wavefront",
    "adaptive-optics": "adaptive_optics",
    "pointing": "pointing",
    # polarization / nonlinear / harmonics
    "polarization": "polarization",
    "shg": "shg",
    "thg": "thg",
    "opcpa": "opcpa",
    "cpa": "cpa",
    "phase-matching": "phase_matching",
    "walkoff": "walkoff",
    "raman": "raman",
    "nonlinear-absorption": "nonlinear_absorption",
    "dispersion": "dispersion",
    "prism-compressor": "prism_compressor",
    "pockels": "pockels",
    "isolator": "isolator",
    "coatings": "coatings",
    # limits / safety / diagnostics
    "ase": "ase",
    "damage": "damage",
    "breakdown": "breakdown",
    "safety": "safety",
    "jitter": "jitter",
    "noise": "noise",
    "contrast": "contrast",
    "autocorrelation": "autocorrelation",
    "frog": "frog",
    "detectors": "detectors",
    "power-meter": "power_meter",
    "efficiency": "efficiency",
    # applications
    "ablation": "ablation",
    "dermatology": "dermatology",
    "ranging": "ranging",
    "plasma": "plasma",
    # system / tooling
    "system": "full_system",
    "chain": "chain_e2e",
    "config": "config",
    "sweep": "sweep",
    "sensitivity": "sensitivity",
    "landscape": "landscape",
    "materials": "materials",
    "fit": "data_io",
    "report": "report",
    "validate": "validate",
    "examples": "examples",
}

BANNER = r"""
  _      _   ___ ___ ___ ___ ___ __  __
 | |    /_\ / __| __| _ \/ __|_ _|  \/  |   laser modeling platform
 | |__ / _ \\__ \ _||   /\__ \| || |\/| |   reproduces NILOP 1.28 J Nd:YAG
 |____/_/ \_\___/___|_|_\|___/___|_|  |_|   (Opt. Commun. 577 (2025) 131413)
"""


def _delegate(module: str, forwarded: List[str]) -> int:
    sys.argv = [module] + forwarded
    try:
        runpy.run_module(module, run_name="__main__")
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 0
    return 0


def cmd_dashboard(_: List[str]) -> int:
    return subprocess.call(["streamlit", "run", "dashboard.py"])


def cmd_info(_: List[str]) -> int:
    print(BANNER)
    print(f"{len(ENGINES)} engines available:\n")
    for name, mod in ENGINES.items():
        print(f"  {name:<22} -> {mod}.py")
    print("  dashboard              -> dashboard.py (Streamlit)")
    print("\nTry:  lasersim system     |     lasersim validate     |     lasersim power-meter")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(prog="lasersim", add_help=True,
                                 description="LASERSIM unified platform CLI")
    ap.add_argument("command", nargs="?", default="info")
    ns, forwarded = ap.parse_known_args(argv)
    cmd = ns.command
    if cmd in ("info", "-h", "--help"):
        return cmd_info(forwarded)
    if cmd == "dashboard":
        return cmd_dashboard(forwarded)
    if cmd in ENGINES:
        return _delegate(ENGINES[cmd], forwarded)
    print(f"unknown command: {cmd!r}\n")
    return cmd_info([])


if __name__ == "__main__":
    sys.exit(main())
