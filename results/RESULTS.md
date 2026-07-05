# lasersim -- Results

_Generated 2026-07-05 04:53 UTC | mode=full-chain | wall clock 8.47s_

## 1. Baseline operating point

| metric | value |
|---|---|
| output_energy_j | 3.8256e-06 |
| output_fluence_j_cm2 | 5.41212e-05 |
| pulse_duration_fs | 3330.76 |
| peak_power_w | 1.07965e+06 |
| m2 | 1.08389 |
| shg_efficiency | 4.20889e-17 |
| green_energy_j | 1.61015e-22 |
| small_signal_gain | 1.53023 |
| damage_margin_j_cm2 | 9.99995 |
| damage_safe | 1 |

## 2. Pump-power sweep

Data: `sweep_pump.csv` (40 points). Figure: `sweep_pump.png`.

Shows the core engineering tradeoff: pushing pump power buys output energy but degrades beam quality (M^2) via thermal load.

## 3. ML surrogate (novelty #2)

Engine: **sklearn-mlp**, trained on 900 samples, tested on 300.

| metric | held-out R^2 |
|---|---|
| output_energy_j | 0.9915 |
| pulse_duration_fs | 0.9972 |
| m2 | 0.9973 |
| shg_efficiency | 0.9798 |

Wall-clock per evaluation: physics = 3.64 us, surrogate = 1015.86 us  ->  **0x speedup**.

## 4. Inverse design (novelty #1, headline)

Optimizer: **scipy-de+nm**, final cost 1.342e-05, damage-constrained.

Recovered design:

| knob | value |
|---|---|
| pump_power_w | 400 |
| crystal_length_cm | 7.88591 |
| seed_energy_nj | 4966.91 |
| residual_gdd_fs2 | 56629 |
| shg_length_mm | 4.85704 |

Target vs achieved:

| metric | target | achieved | rel. error |
|---|---|---|---|
| output_energy_j | 2.5e-05 | 2.5e-05 | -0.0% |
| pulse_duration_fs | 3331 | 3331 | +0.0% |
| m2 | 1.17 | 1.166 | -0.4% |
| shg_efficiency | 0 | 6.488e-17 | +0.0% |

---

See `NOVELTY.md` for the research framing. Reproduce with `python make_results.py` (add `--full` to route the numbers through the full engine chain).
