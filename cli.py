#!/usr/bin/env python3
"""
================================================================================
cli.py  -  unified command-line entry point for the whole LASERSIM platform
================================================================================
One command to drive every engine:

    lasersim system                 # full seed->1.28 J pipeline (vs paper)
    lasersim oscillator --model cw  # rate-equation models
    lasersim amplifier              # Frantz-Nodvik chain
    lasersim spatial --module GM3   # 2D gain map
    lasersim thermal --power 200    # thermal lens + cavity
    lasersim beam --pinhole 110     # serrated aperture + spatial filter
    lasersim opcpa                  # OPCPA front-end
    lasersim sweep amplifier        # batch / GPU parameter sweep
    lasersim fit --demo             # import + fit measured data
    lasersim dashboard              # launch the Streamlit web UI
    lasersim info                   # platform summary

Install (editable):  pip install -e .   ->   then just run `lasersim ...`
================================================================================
"""
from __future__ import annotations

import argparse
import runpy
import sys
from typing import List, Optional

ENGINES = {
    "oscillator": "laser_platform",
    "amplifier": "amplifier",
    "spatial": "spatial_gain",
    "thermal": "thermal_abcd",
    "beam": "beam_shaping",
    "opcpa": "opcpa",
    "system": "full_system",
    "sweep": "sweep",
    "fit": "data_io",
}

BANNER = r"""
  _      _   ___ ___ ___ ___ ___ __  __
 | |    /_\ / __| __| _ \/ __|_ _|  \/  |   laser modeling platform
 | |__ / _ \\__ \ _||   /\__ \| || |\/| |   reproduces NILOP 1.28 J Nd:YAG
 |____/_/ \_\___/___|_|_\|___/___|_|  |_|   (Opt. Commun. 577 (2025) 131413)
"""


def _delegate(module: str, forwarded: List[str]) -> int:
    """Run a sub-module's main() by faking sys.argv and executing it."""
    sys.argv = [module] + forwarded
    try:
        runpy.run_module(module, run_name="__main__")
    except SystemExit as e:  # argparse in submodules may call sys.exit
        return int(e.code) if isinstance(e.code, int) else 0
    return 0


def cmd_dashboard(_: List[str]) -> int:
    import subprocess
    return subprocess.call(["streamlit", "run", "dashboard.py"])


def cmd_info(_: List[str]) -> int:
    print(BANNER)
    print("Engines:")
    for name, mod in ENGINES.items():
        print(f"  {name:<12} -> {mod}.py")
    print("  dashboard    -> dashboard.py (Streamlit)")
    print("\nTry:  lasersim system        (full pipeline vs the paper)")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(
        prog="lasersim",
        description="LASERSIM: unified laser modeling platform CLI",
        add_help=True,
    )
    ap.add_argument("command", nargs="?", default="info",
                    help="engine to run (see `lasersim info`)")
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
