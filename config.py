#!/usr/bin/env python3
"""
================================================================================
config.py  -  define a laser system as DATA, not code
================================================================================
Up to now the NILOP chain is hard-coded in amplifier.py. To make LASERSIM a real
platform (not just a one-system reproduction), this module lets you describe ANY
amplifier chain in a small JSON/YAML config and build it at runtime. Swap rod
sizes, stored energies, passes, and loss elements without touching Python.

Config schema (JSON or YAML)
----------------------------
  name: "My system"
  seed_mJ: 15
  stages:
    - {type: amp,  name: AMP-1, diameter_cm: 1.5, length_cm: 13,
       stored_J: 1.622, passes: 2, beam_radius_cm: 0.35, order: 2}
    - {type: loss, name: SA, transmission: 0.80}
    - {type: amp,  name: AMP-3, modules: 2, diameter_cm: 2.5, length_cm: 13,
       stored_J: 1.14, passes: 1, beam_radius_cm: 0.80, order: 4}

Run:
    python config.py --emit-nilop   # write the NILOP system as a config file
    python config.py mysystem.json  # build + run a chain from a config
================================================================================
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from amplifier import GainModule, AmplifierStage, PassiveLoss, AmplifierChain


def build_from_config(cfg: Dict[str, Any]) -> AmplifierChain:
    """Turn a config dict into a runnable AmplifierChain."""
    elements = []
    for s in cfg["stages"]:
        if s["type"] == "amp":
            n_modules = int(s.get("modules", 1))
            mods = [GainModule(s["name"], s["diameter_cm"], s["length_cm"],
                               s["stored_J"], s.get("f_sat", 0.3))
                    for _ in range(n_modules)]
            elements.append(AmplifierStage(
                s["name"], mods, passes=int(s.get("passes", 1)),
                beam_radius_cm=s.get("beam_radius_cm", 0.5),
                beam_order_n=int(s.get("order", 4)),
                circular_pol=bool(s.get("circular_pol", True))))
        elif s["type"] == "loss":
            elements.append(PassiveLoss(s["name"], s["transmission"]))
        else:
            raise ValueError(f"unknown stage type: {s['type']}")
    return AmplifierChain(cfg.get("name", "chain"),
                          cfg["seed_mJ"] / 1e3, elements)


def load_config(path: str) -> Dict[str, Any]:
    """Load JSON, or YAML if pyyaml is available."""
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except Exception:
            raise SystemExit("pip install pyyaml to load YAML configs")
        with open(path) as fh:
            return yaml.safe_load(fh)
    with open(path) as fh:
        return json.load(fh)


NILOP_CONFIG: Dict[str, Any] = {
    "name": "NILOP 1.28 J / 200 ps Nd:YAG",
    "seed_mJ": 15,
    "stages": [
        {"type": "amp", "name": "AMP-1", "diameter_cm": 1.5, "length_cm": 13,
         "stored_J": 1.622, "passes": 2, "beam_radius_cm": 0.35, "order": 2},
        {"type": "loss", "name": "Serrated aperture", "transmission": 0.80},
        {"type": "amp", "name": "AMP-2", "diameter_cm": 1.5, "length_cm": 13,
         "stored_J": 1.622, "passes": 2, "beam_radius_cm": 0.50, "order": 4},
        {"type": "loss", "name": "Spatial filter", "transmission": 0.88},
        {"type": "amp", "name": "AMP-3", "modules": 2, "diameter_cm": 2.5,
         "length_cm": 13, "stored_J": 1.14, "passes": 1,
         "beam_radius_cm": 0.80, "order": 4},
    ],
}


def main():
    ap = argparse.ArgumentParser(description="Config-driven chain builder")
    ap.add_argument("config", nargs="?", help="path to a JSON/YAML config")
    ap.add_argument("--emit-nilop", metavar="PATH", nargs="?",
                    const="nilop_system.json",
                    help="write the built-in NILOP config to a file")
    args = ap.parse_args()

    if args.emit_nilop:
        with open(args.emit_nilop, "w") as fh:
            json.dump(NILOP_CONFIG, fh, indent=2)
        print(f"Wrote {args.emit_nilop}")
        return

    cfg = load_config(args.config) if args.config else NILOP_CONFIG
    chain = build_from_config(cfg)
    results = chain.run()

    print("=" * 64)
    print(f" {cfg.get('name', 'chain')}  (from config)")
    print("=" * 64)
    for r in results:
        print(f"  {r.name:<28} {r.e_out_mJ:>7.0f} mJ   gain {r.gain:.2f}")
    print("-" * 64)
    print(f"  final output : {results[-1].e_out_mJ:.0f} mJ")
    print("=" * 64)


if __name__ == "__main__":
    main()
