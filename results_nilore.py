#!/usr/bin/env python3
import os
import json
from nilore_twin import validate, design_for_energy
from nilore_predict import fsat_sensitivity, predict_shg, extrapolate_amp4, optimal_beam_schedule

def main():
    # Make results directory
    os.makedirs("results", exist_ok=True)
    
    # Run validations
    res_twin = validate(corrected=True)
    res_paper = validate(corrected=False)
    
    mae_twin = res_twin["mae_twin_pct"]
    mae_paper = res_twin["mae_paper_pct"]
    
    # Run inverse design for 1.28 J
    design = design_for_energy(1.28)
    
    # Run predictions from nilore_predict.py
    sens = fsat_sensitivity()
    shg = predict_shg()
    amp4 = extrapolate_amp4()
    opt_beam = optimal_beam_schedule()
    
    # Load PyTorch surrogate net results if present
    surr_info = None
    if os.path.exists("results/surrogate_net.json"):
        try:
            with open("results/surrogate_net.json", "r") as fh:
                surr_info = json.load(fh)
        except Exception as e:
            print(f"Warning: Could not read surrogate_net.json: {e}")
            
    # Load PyTorch neural inverse design results if present
    inv_info = None
    if os.path.exists("results/neural_inverse.json"):
        try:
            with open("results/neural_inverse.json", "r") as fh:
                inv_info = json.load(fh)
        except Exception as e:
            print(f"Warning: Could not read neural_inverse.json: {e}")
            
    # Generate markdown content
    md = []
    md.append("# NILORE Nd:YAG Digital-Twin Validation")
    md.append("")
    md.append("This document contains the validation results for the digital twin model of the paper:")
    md.append("> **Raza et al., An all-diode pumped 1.28-J 200-ps Nd:YAG amplifier at 10 Hz, Optics Communications 577 (2025) 131413**")
    md.append("")
    md.append("## Per-Stage Validation Table")
    md.append("")
    md.append("| Stage | E_in (mJ) | Measured (mJ) | Paper-calc (mJ) | Twin (mJ) | Paper Err % | Twin Err % | B-integral (rad) |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for rt, rp in zip(res_twin["rows"], res_paper["rows"]):
        md.append(f"| {rt['stage']} | {rt['e_in_mj']:.1f} | {rt['meas_mj']:.1f} | {rt['paper_mj']:.1f} | {rt['twin_mj']:.1f} | {rt['paper_err_pct']:+.1f}% | {rt['twin_err_pct']:+.1f}% | {rt['b_integral']:.2f} |")
        
    md.append("")
    md.append("## Mean Absolute Error (MAE) Comparison")
    md.append("")
    md.append(f"- **Paper Frantz-Nodvik Model MAE**: {mae_paper:.2f}%")
    md.append(f"- **Corrected Twin Model MAE**: {mae_twin:.2f}%")
    md.append("")
    if mae_twin < mae_paper:
        md.append("✓ **Status**: The corrected digital twin successfully beats the paper's model on mean error by incorporating the beam-fill-factor gain-access correction.")
    else:
        md.append("✗ **Status**: The twin model does not outperform the paper model. Needs tuning.")
        
    md.append("")
    md.append("## Inverse Design for 1.28 J Output")
    md.append("")
    md.append(f"- **Target Output Energy**: 1.28 J")
    md.append(f"- **Required AMP-3 Stored Energy / Rod**: {design['required_stored_energy_j']:.3f} J")
    md.append(f"- **Achieved Output Energy**: {design['achieved_out_j']*1e3:.1f} mJ")
    md.append(f"- **AMP-3 B-integral (worst rod/pass)**: {design['b_integral']:.2f} rad")
    md.append(f"- **Safety Status**: {'SAFE (B < 5.0 rad)' if design['b_safe'] else 'UNSAFE (B >= 5.0 rad)'}")
    md.append("")
    
    # 1) F_sat sensitivity band
    md.append("## F_sat Sensitivity Analysis")
    md.append("")
    md.append("Propagation of the paper's F_sat uncertainty (0.4 ± 0.1 J/cm²) through the digital twin model:")
    md.append("")
    md.append("| F_sat (J/cm²) | Predicted Final Energy (mJ) |")
    md.append("| :---: | :---: |")
    for fs in sens["f_sat_values"]:
        md.append(f"| {fs:.2f} | {sens['final_output_j'][fs]*1e3:.1f} |")
    md.append("")
    lo_mj, hi_mj = sens["final_band_j"]
    md.append(f"- **Final-Output Band**: {lo_mj*1e3:.1f} - {hi_mj*1e3:.1f} mJ ({sens['final_band_pct']:.1f}% spread) vs. Measured 1280 mJ")
    md.append("")

    # 2) Predicted 532 nm SHG table
    md.append("## Predicted 532 nm (Green) SHG Conversion")
    md.append("")
    md.append(f"Second-harmonic generation predictions based on the 1.28 J fundamental output at a peak intensity of {shg['peak_intensity_w_cm2']:.2e} W/cm²:")
    md.append("")
    md.append("| Crystal Length (mm) | Conversion Efficiency (%) | Green Energy (mJ) |")
    md.append("| :---: | :---: | :---: |")
    for row in shg["rows"]:
        md.append(f"| {row['length_mm']} | {row['eff']*100:.1f}% | {row['green_energy_j']*1e3:.1f} |")
    md.append("")
    best_len = shg["best"]["length_mm"]
    best_green = shg["best"]["green_energy_j"]
    md.append(f"- **Optimum Crystal Length**: {best_len} mm yielding **{best_green*1e3:.1f} mJ** of 532 nm green energy (conversion efficiency of {shg['best']['eff']*100:.1f}%)")
    md.append("")

    # 3) AMP-4 extrapolation
    md.append("## AMP-4 Extrapolation (Hypothetical Booster Stage)")
    md.append("")
    md.append("Performance prediction of adding a 4th single-pass booster stage (AMP-4 GM5) using a 2.5 cm rod with 1.14 J stored energy, assuming the beam is expanded to 2.0 cm:")
    md.append("")
    safety_str = "SAFE" if amp4["b_safe"] else "UNSAFE"
    md.append(f"- **Predicted Output Energy**: **{amp4['predicted_out_j']*1e3:.1f} mJ** (injected: {amp4['e_in_j']*1e3:.0f} mJ, Gain: {amp4['gain']:.2f})")
    md.append(f"- **B-integral (worst-case)**: {amp4['b_integral']:.2f} rad ({safety_str})")
    md.append("")

    # 4) B-integral-optimal beam schedule
    md.append("## B-integral-Optimal Beam Schedule")
    md.append("")
    md.append("Comparison of the paper's beam diameter schedule vs. an optimized schedule designed to minimize worst-stage B-integral while maintaining the measured per-stage energies:")
    md.append("")
    md.append("| Stage | Paper Beam Diam (cm) | Optimized Beam Diam (cm) | Optimized B-integral (rad) |")
    md.append("| :--- | :---: | :---: | :---: |")
    for row in opt_beam["schedule"]:
        md.append(f"| {row['stage']} | {row['paper_diam_cm']:.1f} | {row['opt_diam_cm']:.1f} | {row['opt_b']:.2f} |")
    md.append("")
    md.append(f"- **Paper Worst-Stage B-integral**: {opt_beam['paper_worst_b']:.2f} rad")
    md.append(f"- **Optimized Worst-Stage B-integral**: {opt_beam['optimized_worst_b']:.2f} rad (**{opt_beam['improvement_pct']:+.1f}% improvement**)")
    md.append("")

    # 5) PyTorch surrogate net results
    if surr_info:
        md.append("## Neural Surrogate Network Training")
        md.append("")
        md.append("A deep residual Multi-Layer Perceptron (MLP) trained to act as a fast neural surrogate for the laser chain physics:")
        md.append("")
        md.append(f"- **Training Device**: {surr_info['device']}")
        md.append(f"- **Training Dataset**: {surr_info['samples']:,} samples generated from the physics model")
        md.append(f"- **Epochs Trained**: {surr_info['epochs_run']} epochs (with early stopping)")
        md.append(f"- **Training Time**: {surr_info['seconds']:.1f} seconds")
        md.append(f"- **Model Size**: {surr_info['params_m']:.2f}M parameters")
        md.append("")
        md.append("| Target Metric | R² Score | Mean Absolute Error (MAE) |")
        md.append("| :--- | :---: | :---: |")
        for key in surr_info["r2"].keys():
            r2_val = surr_info["r2"][key]
            mae_val = surr_info["mae"][key]
            if key == "output_energy_j":
                metric_name = "Output Energy (J)"
                mae_str = f"{mae_val:.4e} J"
            elif key == "pulse_duration_fs":
                metric_name = "Pulse Duration (fs)"
                mae_str = f"{mae_val:.4f} fs"
            elif key == "m2":
                metric_name = "M² Beam Quality"
                mae_str = f"{mae_val:.6f}"
            elif key == "shg_efficiency":
                metric_name = "SHG Efficiency"
                mae_str = f"{mae_val*100:.4f}%"
            elif key == "peak_power_w":
                metric_name = "Peak Power (W)"
                mae_str = f"{mae_val:.1f} W"
            else:
                metric_name = key
                mae_str = f"{mae_val:.4g}"
            md.append(f"| {metric_name} | {r2_val:.6f} | {mae_str} |")
        md.append("")

    # 6) Differentiable inverse design (GPU)
    if inv_info:
        md.append("## Differentiable Inverse Design (GPU)")
        md.append("")
        md.append("Results of gradient-based parallel inverse design optimization using autograd backpropagation through an ensemble of trained neural surrogates:")
        md.append("")
        md.append(f"- **Execution Device**: {inv_info['device']}")
        md.append(f"- **Ensemble Size**: {inv_info['ensemble_size']} neural models")
        md.append(f"- **Population Size**: {inv_info['population']:,} parallel candidates")
        md.append(f"- **Optimization Time**: {inv_info['opt_time_s']:.1f} seconds")
        md.append("")
        md.append("### Optimized Design Parameters")
        md.append("")
        md.append("| Parameter | Optimized Value | Bound Range |")
        md.append("| :--- | :---: | :---: |")
        for key, val in inv_info["best_design"].items():
            if key == "pump_power_w":
                name = "Pump Power (W)"
                bound = "5.0 - 400.0"
                val_str = f"{val:.2f} W"
            elif key == "crystal_length_cm":
                name = "Crystal Length (cm)"
                bound = "0.2 - 8.0"
                val_str = f"{val:.3f} cm"
            elif key == "seed_energy_nj":
                name = "Seed Energy (nJ)"
                bound = "0.1 - 5000.0"
                val_str = f"{val:.2f} nJ"
            elif key == "residual_gdd_fs2":
                name = "Residual GDD (fs²)"
                bound = "0.0 - 60000.0"
                val_str = f"{val:.1f} fs²"
            elif key == "shg_length_mm":
                name = "SHG Crystal Length (mm)"
                bound = "0.0 - 20.0"
                val_str = f"{val:.3f} mm"
            else:
                name = key
                bound = ""
                val_str = f"{val:.4g}"
            md.append(f"| {name} | {val_str} | {bound} |")
        md.append("")
        md.append("### Target vs. Ensemble Predictions vs. Physics Check")
        md.append("")
        md.append("| Metric | Target Spec | Ensemble Surrogate Prediction | Physics Verification |")
        md.append("| :--- | :---: | :---: | :---: |")
        for key, stats in inv_info["metrics"].items():
            t = stats["target"]
            mean = stats["surrogate_mean"]
            std = stats["surrogate_std"]
            phys = stats["physics_check"]
            
            if key == "output_energy_j":
                name = "Output Energy (J)"
                t_str = f"{t*1e6:.1f} µJ"
                s_str = f"{mean*1e6:.2f} ± {std*1e6:.2f} µJ"
                p_str = f"{phys*1e6:.2f} µJ"
            elif key == "pulse_duration_fs":
                name = "Pulse Duration (fs)"
                t_str = f"{t:.1f} fs"
                s_str = f"{mean:.1f} ± {std:.3f} fs"
                p_str = f"{phys:.1f} fs"
            elif key == "m2":
                name = "M² Beam Quality"
                t_str = f"{t:.2f}"
                s_str = f"{mean:.3f} ± {std:.4f}"
                p_str = f"{phys:.3f}"
            elif key == "shg_efficiency":
                name = "SHG Efficiency"
                t_str = f"{t*100:.1f}%"
                s_str = f"{mean*100:.2f} ± {std*100:.3f}%"
                p_str = f"{phys*100:.2f}%"
            elif key == "peak_power_w":
                name = "Peak Power (W)"
                t_str = f"{t/1e6:.1f} MW"
                s_str = f"{mean/1e6:.2f} ± {std/1e6:.2f} MW"
                p_str = f"{phys/1e6:.2f} MW"
            else:
                name = key
                t_str = f"{t:.4g}"
                s_str = f"{mean:.4g} ± {std:.4g}"
                p_str = f"{phys:.4g}"
            md.append(f"| {name} | {t_str} | {s_str} | {p_str} |")
        md.append("")
    
    md_content = "\n".join(md) + "\n"
    
    with open("results/NILORE_VALIDATION.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("Successfully generated results/NILORE_VALIDATION.md with surrogate neural network & neural inverse stats")

if __name__ == "__main__":
    main()
