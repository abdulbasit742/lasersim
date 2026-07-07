# AGPU Autonomous Research Loop Results

Generated: 2026-07-07 21:57:00  |  Iteration: 3

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
