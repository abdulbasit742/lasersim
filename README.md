# LASERSIM

[![CI](https://github.com/abdulbasit742/lasersim/actions/workflows/ci.yml/badge.svg)](https://github.com/abdulbasit742/lasersim/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A research-grade, extensible **laser modeling platform** in Python, built around
a real system: the all-diode-pumped **1.28 J, 200 ps Nd:YAG amplifier** from
Raza et al., *Optics Communications* 577 (2025) 131413 (NILOP College, PIEAS).

LASERSIM models the **entire signal chain** of a high-energy picosecond laser,
from wall socket to delivered application, with ~40 standalone physics engines,
each validated against the paper or a known physical bound. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the full signal-flow map.

## What it covers

- **Gain dynamics:** oscillator rate equations (9 models), regen buildup,
  Frantz-Nodvik amplifier chain, in-pulse temporal reshaping, spatial gain,
  gain narrowing, ASE / parasitic limits.
- **Pump & thermal:** 808 nm diode model, radial heat solve, thermal lens +
  ABCD cavity, coolant convection, rep-rate limit, depolarization.
- **Beam & propagation:** serrated-aperture + spatial-filter shaping, relay
  imaging, self-focusing (NLSE), Raman, M^2 / brightness, wavefront + Strehl,
  adaptive optics, pointing stability.
- **Nonlinear & harmonics:** polarization (Jones), SHG (532), THG (355),
  OPCPA, CPA stretch/compress.
- **Safety & diagnostics:** LIDT damage auditor, eye/skin hazard, timing
  jitter, autocorrelation, pulse contrast, efficiency budget.
- **Applications:** laser ranging, micromachining, plasma / soft X-ray,
  dermatology.
- **Tooling:** config-driven chains, full-system orchestrator, batch/GPU
  sweeps, Monte Carlo tolerancing, literature benchmark, data import,
  HTML/PDF report, Streamlit dashboard, unified CLI, validation scorecard.

## Quick start

```bash
pip install -r requirements.txt
pip install -e .                  # installs the `lasersim` command

lasersim info                     # list every engine
lasersim system                   # whole NILOP pipeline vs the paper
lasersim validate                 # cross-engine pass/fail scorecard
lasersim examples                 # guided tour
streamlit run dashboard.py        # interactive web UI
pytest -q                         # full test suite
```

Run any engine directly, e.g.:

```bash
lasersim amplifier
lasersim shg
lasersim ranging --range-km 1000
lasersim ablation --material steel
lasersim safety
```

## Core physics

```
Oscillator : dN/dt = Rp - N/tau - c sigma N S ;  dS/dt = c sigma N S - S/tau_c + beta N/tau
Amplifier  : F_out = F_sat ln(1 + G0 (e^{F_in/F_sat} - 1)) ;  B = (2pi/lambda) integral n2 I dz
Thermal    : (1/r) d/dr(r k dT/dr) + Q(r) = 0
SHG        : eta = tanh^2( L sqrt(2 omega^2 deff^2 I / (n^3 eps0 c^3)) )
Self-focus : dE/dz = (i/2k) lap_perp E + i k0 n2 |E|^2 E
```

## Validation

`lasersim validate` runs every major engine on the NILOP system and prints one
pass/fail scorecard. The `pytest` suite and GitHub Actions CI run on every push
across Python 3.10/3.11/3.12. See [`BENCHMARKS.md`](BENCHMARKS.md) for the full
Table 1 / Table 2 reproduction.

## License

MIT (see LICENSE).
