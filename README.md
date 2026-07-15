# LASERSIM

[![CI](https://github.com/abdulbasit742/lasersim/actions/workflows/ci.yml/badge.svg)](https://github.com/abdulbasit742/lasersim/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![license](https://img.shields.io/badge/license-MIT-green)

LASERSIM is an extensible **laser modeling platform** in Python, built around a
published system: the all-diode-pumped **1.28 J, 200 ps Nd:YAG amplifier** from
Raza et al., *Optics Communications* 577 (2025) 131413 (NILOP College, PIEAS).

It models a broad high-energy picosecond laser signal chain with standalone
physics engines. Verification is evidence-graded: a literature reproduction,
a physical design bound, a mathematical/model invariant, and a smoke check are
reported separately rather than presented as equivalent forms of validation.
See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the signal-flow map and
[`docs/validation-evidence.md`](docs/validation-evidence.md) for the evidence
contract.

## What it covers

- **Gain dynamics:** oscillator rate equations, regenerative buildup,
  Frantz-Nodvik amplifier chains, in-pulse temporal reshaping, spatial gain,
  gain narrowing, and ASE/parasitic limits.
- **Pump and thermal:** 808 nm diode modeling, radial heat solutions, thermal
  lens and ABCD cavity behavior, coolant convection, repetition-rate limits,
  and depolarization.
- **Beam and propagation:** beam shaping, relay imaging, self-focusing,
  Raman effects, M²/brightness, wavefront/Strehl, adaptive optics, and pointing.
- **Nonlinear and harmonics:** Jones polarization, SHG, THG, OPCPA, and CPA.
- **Safety and diagnostics:** modeled LIDT margin, eye/skin hazard estimates,
  timing jitter, autocorrelation, pulse contrast, and efficiency budgets.
- **Applications and tooling:** ranging, micromachining, plasma/soft X-ray and
  dermatology models, config-driven chains, sweeps, tolerancing, reports, a
  Streamlit dashboard, and a unified CLI.

Safety outputs are engineering model estimates, not a certified laser safety
assessment or a substitute for a qualified laser safety officer.

## Quick start

```bash
python -m pip install -r requirements.txt
python -m pip install -e .

lasersim info
lasersim system
lasersim validate
lasersim examples
streamlit run dashboard.py
python -m pytest -q
```

Run an individual engine directly, for example:

```bash
lasersim amplifier
lasersim shg
lasersim ranging --range-km 1000
lasersim ablation --material steel
lasersim safety
```

## Core physics

```text
Oscillator : dN/dt = Rp - N/tau - c sigma N S ; dS/dt = c sigma N S - S/tau_c + beta N/tau
Amplifier  : F_out = F_sat ln(1 + G0 (e^{F_in/F_sat} - 1)) ; B = (2pi/lambda) integral n2 I dz
Thermal    : (1/r) d/dr(r k dT/dr) + Q(r) = 0
SHG        : eta = tanh^2(L sqrt(2 omega^2 deff^2 I / (n^3 eps0 c^3)))
Self-focus : dE/dz = (i/2k) lap_perp E + i k0 n2 |E|^2 E
```

## Evidence-graded verification

`lasersim validate` runs 20 checks and labels each result with its actual
evidence strength:

- **Literature (3):** compares a stated quantity or ordering with a published
  result or established material relation.
- **Physical bound (6):** checks a documented engineering or model limit.
- **Invariant (8):** checks monotonicity, ordering, sign, or another property
  that should hold inside the implemented model.
- **Smoke (3):** confirms an execution path returns a plausible finite result;
  this is not experimental validation.

Every check has a stable ID, quantity, unit, criterion, and reference. Registry
drift fails tests and CI.

Text report:

```bash
lasersim validate
```

Machine-readable report:

```bash
lasersim validate --format json --output validation-report.json
```

Reports refuse to overwrite an existing file unless `--overwrite` is supplied.
The JSON includes the Python/NumPy environment, per-level totals, enriched check
metadata, and explicit limitations. CI generates and validates this report on
Python 3.10, 3.11, and 3.12.

`pytest` covers the evidence registry and report contract in addition to the
physics suite. See [`BENCHMARKS.md`](BENCHMARKS.md) for the NILOP table
reproduction; passing an invariant or smoke check must not be described as a
literature or experimental validation.

## License

MIT (see `LICENSE`).
