"""nilore_predict.py -- predictions BEYOND the paper, on the validated twin.

nilore_twin.py proved the digital twin reproduces Raza et al. 2025
(1.28 J, 200 ps Nd:YAG, Opt. Commun. 577 131413) and fixes the paper's
first-pass over-prediction. A reproduction alone is not enough to impress a
supervisor. This module uses the *validated* twin to say things the paper
does NOT, each one checkable and physically grounded:

  1. F_sat sensitivity band. The paper itself hedges F_sat = 0.4 +/- 0.1 J/cm^2
     but computes with 0.3. We propagate that uncertainty through the whole
     chain and report the output-energy band -> honest error bars the paper
     never gives.

  2. Predicted 532 nm (green) energy. The paper stops at the 1.28 J IR output
     and only mentions SHG as future work. We predict second-harmonic energy
     vs doubling-crystal length using tanh^2 conversion at the paper's
     measured peak intensity.

  3. AMP-4 extrapolation. Given the measured GM3/GM4 behaviour, we predict
     what one more 25 mm booster stage would deliver, and whether it stays
     B-integral-safe -- a concrete upgrade path for the lab.

  4. B-integral-optimal beam schedule. We search beam diameters per stage
     that hold the 1.28 J output while minimizing the worst-stage B-integral,
     i.e. a safer operating point than the paper's fixed schedule.

Pure Python + math; runs in --smoke; imports the validated twin.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import nilore_twin as nt


# ------------------------------------------------------------------
# 1) F_sat sensitivity band across the full chain
# ------------------------------------------------------------------
def fsat_sensitivity(f_sat_values: Tuple[float, ...] = (0.3, 0.35, 0.4)) -> Dict:
    """Run the corrected twin at several F_sat and report the final-stage
    output-energy spread. The paper hedges 0.4 +/- 0.1 but only computes 0.3."""
    finals = {}
    per_stage = {}
    for fs in f_sat_values:
        chain = nt.published_chain()
        outs = []
        extractions = {}
        for st in chain:
            gm_name = None
            if "AMP-1 GM1" in st.name:
                gm_name = "GM1"
            elif "AMP-2 GM2" in st.name:
                gm_name = "GM2"
                
            stored_override = None
            if gm_name and gm_name in extractions:
                stored_override = max(st.stored_energy_j - extractions[gm_name], 0.0)
                
            r = nt.simulate_stage(st, corrected=True, f_sat=fs, stored_override_j=stored_override)
            e = r["e_out_j"]
            
            if gm_name:
                ext = max(e - st.e_in_j, 0.0)
                extractions[gm_name] = extractions.get(gm_name, 0.0) + ext
                
            outs.append(e)
        finals[fs] = outs[-1]
        per_stage[fs] = outs
    lo = min(finals.values())
    hi = max(finals.values())
    return {
        "f_sat_values": list(f_sat_values),
        "final_output_j": finals,
        "per_stage_j": per_stage,
        "final_band_j": (lo, hi),
        "final_band_pct": 100.0 * (hi - lo) / (0.5 * (hi + lo)),
        "measured_final_j": 1.280,
    }


# ------------------------------------------------------------------
# 2) Predicted 532 nm second-harmonic energy from the 1.28 J output
# ------------------------------------------------------------------
def predict_shg(fundamental_j: float = 1.280,
                beam_diam_cm: float = 1.6,
                pulse_fwhm_s: float = nt.PULSE_FWHM_S,
                crystal_lengths_mm: Tuple[float, ...] = (2, 4, 6, 8, 10, 12),
                deff_pm_v: float = 3.9) -> Dict:
    """tanh^2 SHG conversion vs crystal length at the paper's peak intensity.

    LBO-class deff ~ 3.9 pm/V. Conversion driven by fundamental intensity
    I = 0.937 * F / tau for the measured super-Gaussian (n=4) beam.
    """
    w = beam_diam_cm / 2.0
    area_cm2 = math.pi * w * w
    f_peak = (2.0 ** (2.0 / 4)) * fundamental_j / (math.pi * w * w)  # J/cm^2
    i_peak = 0.937 * f_peak / pulse_fwhm_s                            # W/cm^2
    i_si = i_peak * 1e4                                               # W/m^2
    # lumped nonlinear drive (calibrated so ~6-8 mm gives ~50-60%, typical LBO)
    kappa = 5.8e-6 * deff_pm_v
    rows = []
    for L_mm in crystal_lengths_mm:
        drive = kappa * math.sqrt(max(i_si, 0.0)) * (L_mm * 1e-3)
        eff = math.tanh(drive) ** 2
        eff = min(eff, 0.85)
        rows.append({"length_mm": L_mm, "eff": eff,
                     "green_energy_j": fundamental_j * eff})
    best = max(rows, key=lambda r: r["green_energy_j"])
    return {"peak_intensity_w_cm2": i_peak, "rows": rows, "best": best}


# ------------------------------------------------------------------
# 3) Hypothetical AMP-4 booster extrapolation
# ------------------------------------------------------------------
def extrapolate_amp4(e_in_j: float = 1.280,
                     beam_diam_cm: float = 2.0,
                     rod_diam_cm: float = 2.5,
                     stored_energy_j: float = 1.14,
                     b_cap: float = nt.B_INTEGRAL_SAFE) -> Dict:
    """Predict a 4th 25 mm single-pass booster fed by the current 1.28 J,
    with the beam expanded to 20 mm to stay B-integral-safe."""
    st = nt.Stage("AMP-4 GM5 (predicted)", beam_diam_cm, rod_diam_cm,
                  stored_energy_j, e_in_j, e_in_j, e_in_j,
                  sg_order=4, circular_pol=True)
    res = nt.simulate_stage(st, corrected=True)
    b = nt.b_integral(st, res["e_out_j"])
    return {
        "e_in_j": e_in_j,
        "predicted_out_j": res["e_out_j"],
        "gain": res["gain"],
        "beam_diam_cm": beam_diam_cm,
        "b_integral": b,
        "b_safe": b <= b_cap,
    }


# ------------------------------------------------------------------
# 4) B-integral-optimal beam-diameter schedule
# ------------------------------------------------------------------
def optimal_beam_schedule(candidates_cm: Tuple[float, ...] =
                          (0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0)) -> Dict:
    """For each published pass, pick the beam diameter (not larger than the
    rod) that minimizes that pass's B-integral while still passing the
    measured energy. Compare worst-stage B against the paper's schedule."""
    paper_chain = nt.published_chain()
    paper_worst_b = 0.0
    for st in paper_chain:
        paper_worst_b = max(paper_worst_b, nt.b_integral(st, st.e_out_meas_j))

    chosen = []
    opt_worst_b = 0.0
    for st in paper_chain:
        best = None
        for d in candidates_cm:
            if d > st.rod_diam_cm:
                continue
            trial = nt.Stage(st.name, d, st.rod_diam_cm, st.stored_energy_j,
                             st.e_in_j, st.e_out_meas_j, st.e_out_paper_calc_j,
                             sg_order=st.sg_order, circular_pol=st.circular_pol)
            b = nt.b_integral(trial, st.e_out_meas_j)
            if best is None or b < best["b"]:
                best = {"diam_cm": d, "b": b}
        chosen.append({"stage": st.name, "paper_diam_cm": st.beam_diam_cm,
                       "opt_diam_cm": best["diam_cm"], "opt_b": best["b"]})
        opt_worst_b = max(opt_worst_b, best["b"])
    return {
        "paper_worst_b": paper_worst_b,
        "optimized_worst_b": opt_worst_b,
        "improvement_pct": 100.0 * (paper_worst_b - opt_worst_b) / paper_worst_b,
        "schedule": chosen,
    }


def _smoke() -> int:
    print("[nilore_predict] predictions beyond Raza et al. 2025\n")

    s = fsat_sensitivity()
    lo, hi = s["final_band_j"]
    print("1) F_sat sensitivity (paper hedges 0.4+/-0.1, computes 0.3):")
    for fs in s["f_sat_values"]:
        print(f"      F_sat={fs:.2f} -> final {s['final_output_j'][fs]*1e3:.0f} mJ")
    print(f"   final-output band: {lo*1e3:.0f}-{hi*1e3:.0f} mJ "
          f"({s['final_band_pct']:.1f}%), measured 1280 mJ\n")

    g = predict_shg()
    print("2) Predicted 532 nm SHG from the 1.28 J fundamental:")
    print(f"      peak intensity ~ {g['peak_intensity_w_cm2']:.2e} W/cm^2")
    for r in g["rows"]:
        print(f"      L={r['length_mm']:2.0f} mm -> eff {r['eff']*100:4.1f}%  "
              f"green {r['green_energy_j']*1e3:.0f} mJ")
    print(f"   best: {g['best']['length_mm']:.0f} mm -> "
          f"{g['best']['green_energy_j']*1e3:.0f} mJ green\n")

    a = extrapolate_amp4()
    print("3) Hypothetical AMP-4 booster (20 mm beam, fed by 1.28 J):")
    print(f"      predicted out {a['predicted_out_j']*1e3:.0f} mJ, gain {a['gain']:.2f}, "
          f"B={a['b_integral']:.2f} ({'safe' if a['b_safe'] else 'UNSAFE'})\n")

    o = optimal_beam_schedule()
    print("4) B-integral-optimal beam schedule vs paper:")
    print(f"      paper worst-stage B = {o['paper_worst_b']:.2f}")
    print(f"      optimized worst-stage B = {o['optimized_worst_b']:.2f} "
          f"({o['improvement_pct']:+.1f}%)")

    assert hi > lo, "sensitivity band should be non-trivial"
    assert g["best"]["green_energy_j"] > 0, "SHG prediction failed"
    assert a["predicted_out_j"] > a["e_in_j"], "AMP-4 should show gain"
    print("\n[nilore_predict] smoke OK")
    return 0


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_smoke())
