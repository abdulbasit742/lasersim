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
