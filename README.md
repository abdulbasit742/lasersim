# LASERSIM

A research-grade, extensible **laser modeling platform** in Python, built around
a real system: the all-diode-pumped **1.28 J, 200 ps Nd:YAG amplifier** from
Raza et al., *Optics Communications* 577 (2025) 131413 (NILOP College, PIEAS).

## Engines

| File | Engine | What it does |
|---|---|---|
| `laser_platform.py` | **Oscillator dynamics** | 9 rate-equation models: 3-/4-level, CW, active/passive Q-switch, gain-switched, multimode, mode-locked, thermal |
| `amplifier.py` | **Amplifier chain** | Frantz-Nodvik multi-pass, super-Gaussian fluence, B-integral; reproduces the paper's AMP-1/2/3 chain |
| `spatial_gain.py` | **Spatial gain** | 2D non-uniform pump -> gain map -> local extraction (paper Fig. 2) |
| `thermal_abcd.py` | **Thermal + cavity** | Thermal-lens focal length + ABCD cavity stability & TEM00 mode size |
| `beam_shaping.py` | **Beam shaping** | Serrated-aperture apodization + FFT Fourier spatial filter (paper Fig. 3) |
| `opcpa.py` | **OPCPA front-end** | Chirped-pulse stretch/compress + 3-wave OPA gain (this system as a pump) |
| `full_system.py` | **Orchestrator** | End-to-end seed->1.28 J pipeline tying all engines together |
| `sweep.py` | **Batch sweeps** | Vectorized, parallel, GPU-ready (CuPy) parameter sweeps + optimization |
| `dashboard.py` | **Web dashboard** | Streamlit UI with every engine behind live sliders |

## Quick start

```bash
pip install -r requirements.txt

streamlit run dashboard.py            # interactive web UI
python full_system.py                 # whole system, audit table vs the paper
python sweep.py amplifier --csv o.csv # batch optimization (set LASERSIM_XP=cupy for GPU)

python laser_platform.py              # oscillator dashboard
python amplifier.py                   # amplifier chain vs paper
python spatial_gain.py --module GM3   # 2D gain map
python thermal_abcd.py                # thermal lens + cavity sweep
python beam_shaping.py --pinhole 110  # serrated aperture + spatial filter
python opcpa.py                       # OPCPA front-end

pytest -q                             # full test suite
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
G0    = exp(F_store / F_sat)
B     = (2*pi/lambda) * integral( n2(z) * I(z) dz )    # circular pol: n2 *= 2/3
```

**Thermal lens (Koechner):**
```
1/f_th = (P_heat / (2*pi*K*A)) * ( dn/dT + stress-optic )
```

**OPA (3-wave):**
```
dA_s/dz = i*kappa*A_p*conj(A_i);  dA_i/dz = i*kappa*A_p*conj(A_s);  dA_p/dz = i*kappa*A_s*A_i
G = cosh^2(g L),  g = kappa*|A_p|
```

## Validation

`python full_system.py` prints modeled output energy + B-integral for every
stage next to the paper's measured values (Table 1 + Table 2). The chain lands
at ~1.28 J with B-integrals under the ~3 rad self-focusing safe limit. The
`pytest` suite locks this in, and GitHub Actions runs it on every push across
Python 3.10/3.11/3.12.

## Roadmap

- [x] Oscillator rate-equation models
- [x] Frantz-Nodvik amplifier chain
- [x] Spatial gain maps from non-uniform pump
- [x] Thermal lens + ABCD cavity solver
- [x] Serrated aperture + spatial filtering
- [x] OPCPA front-end
- [x] End-to-end system orchestrator
- [x] Batch / GPU parameter sweeps
- [x] Interactive web dashboard
- [x] Test suite + CI
- [ ] Real beam-profile / spectroscopic data import
- [ ] 3D thermal FEM coupling

## License

MIT (see LICENSE).
