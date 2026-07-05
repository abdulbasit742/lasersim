# NILORE Nd:YAG Digital-Twin Validation

This document contains the validation results for the digital twin model of the paper:
> **Raza et al., An all-diode pumped 1.28-J 200-ps Nd:YAG amplifier at 10 Hz, Optics Communications 577 (2025) 131413**

## Per-Stage Validation Table

| Stage | E_in (mJ) | Measured (mJ) | Paper-calc (mJ) | Twin (mJ) | Paper Err % | Twin Err % | B-integral (rad) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| AMP-1 GM1 p1 | 15.0 | 70.0 | 122.0 | 69.3 | +74.3% | -1.0% | 0.80 |
| AMP-1 GM1 p2 | 70.0 | 200.0 | 216.0 | 171.4 | +8.0% | -14.3% | 1.99 |
| AMP-2 GM2 p1 | 140.0 | 470.0 | 561.0 | 502.5 | +19.4% | +6.9% | 2.02 |
| AMP-2 GM2 p2 | 470.0 | 755.0 | 838.0 | 871.6 | +11.0% | +15.4% | 3.51 |
| AMP-3 GM3 | 720.0 | 980.0 | 1006.0 | 950.8 | +2.7% | -3.0% | 1.00 |
| AMP-3 GM4 | 980.0 | 1280.0 | 1286.0 | 1220.1 | +0.5% | -4.7% | 1.28 |

## Mean Absolute Error (MAE) Comparison

- **Paper Frantz-Nodvik Model MAE**: 19.29%
- **Corrected Twin Model MAE**: 7.55%

✓ **Status**: The corrected digital twin successfully beats the paper's model on mean error by incorporating the beam-fill-factor gain-access correction.

## Inverse Design for 1.28 J Output

- **Target Output Energy**: 1.28 J
- **Required AMP-3 Stored Energy / Rod**: 1.428 J
- **Achieved Output Energy**: 1280.0 mJ
- **AMP-3 B-integral (worst rod/pass)**: 1.34 rad
- **Safety Status**: SAFE (B < 5.0 rad)

## F_sat Sensitivity Analysis

Propagation of the paper's F_sat uncertainty (0.4 ± 0.1 J/cm²) through the digital twin model:

| F_sat (J/cm²) | Predicted Final Energy (mJ) |
| :---: | :---: |
| 0.30 | 1185.4 |
| 0.35 | 1173.0 |
| 0.40 | 1161.3 |

- **Final-Output Band**: 1161.3 - 1185.4 mJ (2.1% spread) vs. Measured 1280 mJ

## Predicted 532 nm (Green) SHG Conversion

Second-harmonic generation predictions based on the 1.28 J fundamental output at a peak intensity of 4.22e+09 W/cm²:

| Crystal Length (mm) | Conversion Efficiency (%) | Green Energy (mJ) |
| :---: | :---: | :---: |
| 2 | 8.2% | 104.4 |
| 4 | 27.9% | 357.1 |
| 6 | 50.0% | 640.1 |
| 8 | 68.2% | 873.2 |
| 10 | 80.9% | 1035.4 |
| 12 | 85.0% | 1088.0 |

- **Optimum Crystal Length**: 12 mm yielding **1088.0 mJ** of 532 nm green energy (conversion efficiency of 85.0%)

## AMP-4 Extrapolation (Hypothetical Booster Stage)

Performance prediction of adding a 4th single-pass booster stage (AMP-4 GM5) using a 2.5 cm rod with 1.14 J stored energy, assuming the beam is expanded to 2.0 cm:

- **Predicted Output Energy**: **1572.5 mJ** (injected: 1280 mJ, Gain: 1.23)
- **B-integral (worst-case)**: 1.05 rad (SAFE)

## B-integral-Optimal Beam Schedule

Comparison of the paper's beam diameter schedule vs. an optimized schedule designed to minimize worst-stage B-integral while maintaining the measured per-stage energies:

| Stage | Paper Beam Diam (cm) | Optimized Beam Diam (cm) | Optimized B-integral (rad) |
| :--- | :---: | :---: | :---: |
| AMP-1 GM1 p1 | 0.7 | 1.4 | 0.20 |
| AMP-1 GM1 p2 | 0.7 | 1.4 | 0.58 |
| AMP-2 GM2 p1 | 1.0 | 1.4 | 0.96 |
| AMP-2 GM2 p2 | 1.0 | 1.4 | 1.55 |
| AMP-3 GM3 | 1.6 | 2.0 | 0.66 |
| AMP-3 GM4 | 1.6 | 2.0 | 0.86 |

- **Paper Worst-Stage B-integral**: 3.04 rad
- **Optimized Worst-Stage B-integral**: 1.55 rad (**+49.0% improvement**)

