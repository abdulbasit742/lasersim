# AGPU Autonomous Research Loop Results

Generated: 2026-07-07 21:55:45  |  Iteration: 4

This file is auto-updated by the AGPU research daemon each loop.

---

## Stage A: Pareto Front (Energy vs SHG Efficiency)
- Samples evaluated: 50,000
- Non-dominated designs: 4
- Best energy on front: **0.024 mJ**  SHG=1.3%
- Best SHG on front: **9.2%**  energy=0.023 mJ

## Stage B: Architecture Ablation
- Configs tested: 9
- Best: width=512, depth=4, params=793,605, mean R²=0.999888

## Stage C: Uncertainty Calibration Audit

- output_energy_j: physics CV=77.1%
- pulse_duration_fs: physics CV=0.0%
- m2: physics CV=4.4%
- shg_efficiency: physics CV=135.0%
- peak_power_w: physics CV=77.1%

## Stage D: Multi-Target Inverse Design

| Target | RMSE | Energy (µJ) | SHG% |
|--------|------|-------------|------|
| high_energy | 0.0289 | 5.04 | 1.0 |
| high_shg | 0.5709 | 2.04 | 0.9 |
| low_diverge | 0.4979 | 3.37 | 1.5 |
| high_power | 0.2489 | 6.96 | 3.0 |
| short_pulse | 12.2424 | 1.00 | 0.0 |
