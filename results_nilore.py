#!/usr/bin/env python3
import os
from nilore_twin import validate, design_for_energy

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
    
    md_content = "\n".join(md) + "\n"
    
    with open("results/NILORE_VALIDATION.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("Successfully generated results/NILORE_VALIDATION.md")

if __name__ == "__main__":
    main()
