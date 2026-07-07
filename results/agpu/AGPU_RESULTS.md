# AGPU Autonomous Research Loop Results

Generated: 2026-07-07 21:57:07  |  Iteration: 5

This file is auto-updated by the AGPU research daemon each loop.

---

## Stage A: Pareto Front (Energy vs SHG Efficiency)
- Samples evaluated: 50,000
- Non-dominated designs: 4
- Best energy on front: **0.024 mJ**  SHG=1.3%
- Best SHG on front: **9.2%**  energy=0.023 mJ

## Stage B: Architecture Ablation
- Configs tested: 9
- Best: width=512, depth=6, params=1,318,917, mean R²=0.999869

## Stage C: Uncertainty Calibration Audit

- output_energy_j: physics CV=77.1%
- pulse_duration_fs: physics CV=0.0%
- m2: physics CV=4.4%
- shg_efficiency: physics CV=135.0%
- peak_power_w: physics CV=77.1%

## Stage D: Multi-Target Inverse Design

| Target | RMSE | Energy (µJ) | SHG% |
|--------|------|-------------|------|
| high_energy | 0.0223 | 5.03 | 1.0 |
| high_shg | 0.5711 | 2.02 | 0.8 |
| low_diverge | 0.4983 | 3.27 | 1.4 |
| high_power | 0.2523 | 7.03 | 3.0 |
| short_pulse | 12.2424 | 1.01 | 0.2 |

## Stage E: Sensitivity Analysis
- Knob ranking by output energy sensitivity: **seed_energy_nj > pump_power_w > crystal_length_cm > residual_gdd_fs2 > shg_length_mm**
