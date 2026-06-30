# LASERSIM

A compact, extensible **laser modeling platform** in Python, built around a real
world system: the all-diode-pumped **1.28 J, 200 ps Nd:YAG amplifier** from
Raza et al., *Optics Communications* 577 (2025) 131413 (NILOP College, PIEAS).

Five engines, one platform:

| File | Engine | What it does |
|---|---|---|
| `laser_platform.py` | **Oscillator dynamics** | 9 rate-equation models: 3-/4-level, CW, active/passive Q-switch, gain-switched, multimode, mode-locked, thermal |
| `amplifier.py` | **Amplifier chain** | Frantz-Nodvik multi-pass extraction, super-Gaussian fluence, B-integral; reproduces the paper's AMP-1/2/3 chain |
| `spatial_gain.py` | **Spatial gain** | 2D non-uniform pump -> gain map -> local extraction (paper Fig. 2) |
| `thermal_abcd.py` | **Thermal + cavity** | Thermal-lens focal length + ABCD cavity stability & TEM00 mode size |
| `beam_shaping.py` | **Beam shaping** | Serrated-aperture apodization + FFT Fourier spatial filter (paper Fig. 3) |
| `full_system.py` | **Orchestrator** | End-to-end seed->1.28 J pipeline tying all engines together |

## Quick start

```bash
pip install -r requirements.txt

python full_system.py                 # whole system, audit table vs the paper
python full_system.py --json          # machine-readable

python laser_platform.py              # oscillator dashboard (all models)
python laser_platform.py --model qswitch_active
python amplifier.py                   # amplifier chain vs paper
python spatial_gain.py --module GM3   # 2D gain map
python thermal_abcd.py                # thermal lens + cavity sweep
python beam_shaping.py --pinhole 110  # SA + spatial filter
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

## Validation against the paper

`python full_system.py` prints modeled output energy and B-integral for every
stage next to the paper's measured values (Table 1 + Table 2). The chain lands
at ~1.28 J with B-integrals under the ~3 rad self-focusing safe limit.

## Roadmap

- [x] Oscillator rate-equation models
- [x] Frantz-Nodvik amplifier chain
- [x] Spatial gain maps from non-uniform pump
- [x] Thermal lens + ABCD cavity solver
- [x] Serrated aperture + spatial filtering
- [x] End-to-end system orchestrator
- [ ] OPCPA pump front-end modeling
- [ ] GPU batch parameter sweeps
- [ ] Web dashboard + real data import
- [ ] Test suite + CI

## License

MIT (see LICENSE).
