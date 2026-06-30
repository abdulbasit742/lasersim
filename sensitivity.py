#!/usr/bin/env python3
"""
================================================================================
sensitivity.py  -  Monte Carlo tolerancing & parameter sensitivity analysis
================================================================================
The paper reports 1.1% RMS energy stability. That number is set by how component
tolerances (stored energy jitter, beam-size drift, saturation-fluence spread,
seed-energy noise) propagate to the final output. This module answers two
engineering questions the other modules don't:

  1. TOLERANCING (Monte Carlo): given +/- tolerances on each input, what is the
     resulting RMS spread of the 1.28 J output? Does it meet the 1.1% spec?
  2. SENSITIVITY (one-at-a-time + variance share): which single parameter is the
     biggest lever on output energy? Where should you spend your stabilization
     budget?

This is the difference between "it works on paper" and "it works every shot."

Run:
    python sensitivity.py                 # Monte Carlo + sensitivity ranking
    python sensitivity.py --n 20000       # more samples
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


# ==============================================================================
# MODEL UNDER TEST: the NILOP chain output energy as a function of key params
# ==============================================================================
def chain_output_mJ(params: Dict[str, float]) -> float:
    """Run the amplifier chain with perturbed parameters, return final mJ."""
    from amplifier import GainModule, AmplifierStage, PassiveLoss, AmplifierChain
    e_store_small = params["e_store_small"]   # GM1/GM2 stored energy [J]
    e_store_big = params["e_store_big"]       # GM3/GM4 stored energy [J]
    f_sat = params["f_sat"]
    seed = params["seed_mJ"] / 1e3
    sa_T = params["sa_transmission"]
    sf_T = params["sf_transmission"]
    br1 = params["beam_r1"]
    br2 = params["beam_r2"]
    br3 = params["beam_r3"]

    gm1 = GainModule("GM1", 1.5, 13.0, e_store_small, f_sat)
    gm2 = GainModule("GM2", 1.5, 13.0, e_store_small, f_sat)
    gm3 = GainModule("GM3", 2.5, 13.0, e_store_big, f_sat)
    gm4 = GainModule("GM4", 2.5, 13.0, e_store_big, f_sat)
    chain = AmplifierChain("mc", seed, [
        AmplifierStage("AMP-1", [gm1], passes=2, beam_radius_cm=br1, beam_order_n=2),
        PassiveLoss("SA", sa_T),
        AmplifierStage("AMP-2", [gm2], passes=2, beam_radius_cm=br2, beam_order_n=4),
        PassiveLoss("SF", sf_T),
        AmplifierStage("AMP-3", [gm3, gm4], passes=1, beam_radius_cm=br3, beam_order_n=4),
    ])
    return chain.run()[-1].e_out_mJ


# ==============================================================================
# PARAMETER DEFINITIONS: nominal value + relative tolerance (1-sigma)
# ==============================================================================
@dataclass
class Param:
    name: str
    nominal: float
    rel_sigma: float        # 1-sigma relative tolerance (fraction)


def default_params() -> List[Param]:
    return [
        Param("e_store_small", 1.622, 0.010),   # diode current stability ~1%
        Param("e_store_big", 1.140, 0.010),
        Param("f_sat", 0.300, 0.020),
        Param("seed_mJ", 15.0, 0.010),
        Param("sa_transmission", 0.80, 0.005),
        Param("sf_transmission", 0.88, 0.005),
        Param("beam_r1", 0.35, 0.010),
        Param("beam_r2", 0.50, 0.010),
        Param("beam_r3", 0.80, 0.010),
    ]


def nominal_dict(params: List[Param]) -> Dict[str, float]:
    return {p.name: p.nominal for p in params}


# ==============================================================================
# MONTE CARLO TOLERANCING
# ==============================================================================
def monte_carlo(params: List[Param], n: int = 5000, seed: int = 0):
    rng = np.random.default_rng(seed)
    base = nominal_dict(params)
    outs = np.empty(n)
    samples = {p.name: rng.normal(p.nominal, abs(p.nominal) * p.rel_sigma, n)
               for p in params}
    for i in range(n):
        d = {name: samples[name][i] for name in base}
        outs[i] = chain_output_mJ(d)
    return outs


# ==============================================================================
# SENSITIVITY: variance share by freezing one parameter at a time
# ==============================================================================
def sensitivity_ranking(params: List[Param], n: int = 3000, seed: int = 1):
    """For each parameter, vary ONLY it (others fixed) and measure the output
    RMS it produces. Normalize to get each parameter's share of the spread."""
    rng = np.random.default_rng(seed)
    base = nominal_dict(params)
    contributions = {}
    for p in params:
        s = rng.normal(p.nominal, abs(p.nominal) * p.rel_sigma, n)
        outs = np.empty(n)
        for i in range(n):
            d = dict(base)
            d[p.name] = s[i]
            outs[i] = chain_output_mJ(d)
        contributions[p.name] = float(np.std(outs))
    total_var = sum(v ** 2 for v in contributions.values())
    shares = {k: (v ** 2 / total_var if total_var > 0 else 0.0)
              for k, v in contributions.items()}
    return contributions, shares


def main():
    ap = argparse.ArgumentParser(description="Monte Carlo tolerancing + sensitivity")
    ap.add_argument("--n", type=int, default=5000)
    args = ap.parse_args()

    params = default_params()
    nominal = chain_output_mJ(nominal_dict(params))

    outs = monte_carlo(params, n=args.n)
    mean, std = outs.mean(), outs.std()
    rms_pct = 100.0 * std / mean

    print("=" * 64)
    print(" Monte Carlo tolerancing  (NILOP 1.28 J chain)")
    print("=" * 64)
    print(f"  nominal output   : {nominal:.0f} mJ")
    print(f"  MC mean +/- std  : {mean:.0f} +/- {std:.0f} mJ")
    print(f"  RMS stability    : {rms_pct:.2f} %  "
          f"(paper spec: 1.1%)  {'MEETS' if rms_pct <= 1.1 else 'EXCEEDS'} spec")
    print(f"  5-95 percentile  : {np.percentile(outs,5):.0f} - {np.percentile(outs,95):.0f} mJ")
    print("=" * 64)

    _, shares = sensitivity_ranking(params, n=max(args.n // 2, 1000))
    print(" Sensitivity ranking (share of output variance)")
    print("-" * 64)
    for name, share in sorted(shares.items(), key=lambda kv: -kv[1]):
        bar = "#" * int(round(share * 40))
        print(f"  {name:<18} {share*100:5.1f}%  {bar}")
    print("=" * 64)
    top = max(shares, key=shares.get)
    print(f"  biggest lever: '{top}' -> stabilize this first.")
    print("=" * 64)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
        ax[0].hist(outs, bins=50, color="tab:blue", alpha=0.8)
        ax[0].axvline(nominal, color="r", ls="--", label="nominal")
        ax[0].set(title=f"Output distribution ({rms_pct:.2f}% RMS)",
                  xlabel="output energy [mJ]", ylabel="shots"); ax[0].legend()
        names = list(shares.keys()); vals = [shares[n] * 100 for n in names]
        order = np.argsort(vals)
        ax[1].barh([names[i] for i in order], [vals[i] for i in order],
                   color="tab:orange")
        ax[1].set(title="Sensitivity (variance share)", xlabel="% of variance")
        plt.tight_layout(); plt.savefig("sensitivity.png", dpi=130)
        print("Saved -> sensitivity.png")
        plt.show()


if __name__ == "__main__":
    main()
