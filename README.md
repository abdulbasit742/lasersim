# LASERSIM

A research-grade, extensible **laser modeling platform** in Python, built around
a real system: the all-diode-pumped **1.28 J, 200 ps Nd:YAG amplifier** from
Raza et al., *Optics Communications* 577 (2025) 131413 (NILOP College, PIEAS).

Every engine is grounded in, and validated against, that paper.

## Engines

| File | Engine | What it does |
|---|---|---|
| `laser_platform.py` | **Oscillator dynamics** | 9 rate-equation models: 3-/4-level, CW, active/passive Q-switch, gain-switched, multimode, mode-locked, thermal |
| `amplifier.py` | **Amplifier chain** | Frantz-Nodvik multi-pass, super-Gaussian fluence, B-integral; reproduces AMP-1/2/3 |
| `spatial_gain.py` | **Spatial gain** | 2D non-uniform pump -> gain map -> local extraction (Fig. 2) |
| `thermal_abcd.py` | **Thermal + cavity** | Lumped thermal-lens + ABCD cavity stability & TEM00 mode size |
| `thermal_fem.py` | **Radial thermal** | First-principles radial heat solve: T(r), stress, fracture limit |
| `beam_shaping.py` | **Beam shaping** | Serrated-aperture apodization + FFT spatial filter (Fig. 3) |
| `relay_imaging.py` | **Relay imaging** | Gaussian q-parameter propagation through relay telescopes (6->16 mm) |
| `propagation.py` | **Self-focusing** | Split-step NLSE beam propagation + Bespalov-Talanov instability |
| `temporal.py` | **Pulse dynamics** | Time-resolved Frantz-Nodvik: gain saturation + pulse reshaping |
| `polarization.py` | **Polarization** | Jones calculus: waveplates, TFP, Faraday; circular-pol n2 mitigation |
| `ase.py` | **ASE / parasitics** | Transverse parasitic-oscillation limit, max storable energy |
| `damage.py` | **Damage auditor** | LIDT pulse-scaling + per-stage fluence safety margin |
| `opcpa.py` | **OPCPA front-end** | Chirped-pulse stretch/compress + 3-wave OPA gain |
| `full_system.py` | **Orchestrator** | End-to-end seed->1.28 J pipeline tying engines together |
| `sweep.py` | **Batch sweeps** | Vectorized, parallel, GPU-ready (CuPy) parameter sweeps |
| `data_io.py` | **Data import** | Import + super-Gaussian fit of measured beam/energy data |
| `report.py` | **Reports** | Auto-generate a paper-style HTML/PDF report of a full run |
| `dashboard.py` | **Web dashboard** | Streamlit UI with every engine behind live sliders |
| `validate.py` | **Validation** | Cross-engine pass/fail scorecard vs the paper (CI-friendly) |
| `cli.py` | **CLI** | Unified `lasersim` command for every engine |

## Quick start

```bash
pip install -r requirements.txt
pip install -e .                      # installs the `lasersim` command

lasersim system                       # whole system, audit table vs the paper
python validate.py                    # cross-engine pass/fail scorecard
streamlit run dashboard.py            # interactive web UI
pytest -q                             # full test suite
```

Individual engines:

```bash
python laser_platform.py --model qswitch_active
python amplifier.py
python spatial_gain.py --module GM3
python thermal_fem.py --profile petal --power 200
python relay_imaging.py
python propagation.py --B 2.5
python temporal.py --g0 3.0
python polarization.py --demo waveplate-sweep
python ase.py --diameter-mm 25
python damage.py --safety 1.5
python opcpa.py
python report.py --pdf
```

## Physics core

**Oscillator (rate equations):**
```
dN/dt = Rp - N/tau   - c*sigma*N*S
dS/dt = c*sigma*N*S  - S/tau_c + beta*N/tau
```

**Amplifier (Frantz-Nodvik):**
```
F_out = F_sat * ln( 1 + G0 * (exp(F_in / F_sat) - 1) )
B     = (2*pi/lambda) * integral( n2(z) * I(z) dz )    # circular pol: n2 *= 2/3
```

**Self-focusing (NLSE, split-step):**
```
dE/dz = (i/2k) lap_perp(E) + i k0 n2 |E|^2 E
```

**Thermal (radial heat equation):**
```
(1/r) d/dr( r k dT/dr ) + Q(r) = 0,   T(R) = T_coolant
```

## Validation

`python validate.py` runs every engine on the NILOP system and prints a single
pass/fail scorecard (energy, B-integral, polarization, thermal, relay, ASE,
damage, oscillator). The `pytest` suite and GitHub Actions CI run it on every
push across Python 3.10/3.11/3.12.

## License

MIT (see LICENSE).
