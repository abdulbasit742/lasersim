# LASERSIM

A compact, extensible **laser modeling platform** in Python. Two engines:

1. **`laser_platform.py`** — single-mode **rate-equation** models for laser *oscillators*:
   3-level, 4-level, CW transient (relaxation oscillations), active + passive Q-switch,
   gain-switched, multimode (mode competition), mode-locked, and thermal-lensing models.
2. **`amplifier.py`** — **Frantz-Nodvik multi-pass amplifier** engine with super-Gaussian
   beam fluence, B-integral, and thermal/nonlinearity safety checks. Ships with a built-in
   model of the **all-diode-pumped 1.28 J, 200 ps Nd:YAG amplifier** (NILOP/PIEAS,
   *Optics Communications* 577 (2025) 131413) and reproduces its energy chain + B-integrals.

## Quick start

```bash
pip install -r requirements.txt

python laser_platform.py              # oscillator dashboard (all models)
python laser_platform.py --list       # list oscillator models
python laser_platform.py --model qswitch_active

python amplifier.py                    # run the NILOP 1.28 J amplifier chain + compare to paper
```

## Physics core (oscillator)

```
dN/dt = Rp - N/tau   - c*sigma*N*S
dS/dt = c*sigma*N*S  - S/tau_c + beta*N/tau
```

## Physics core (amplifier, Frantz-Nodvik)

```
F_out = F_sat * ln( 1 + G0 * (exp(F_in / F_sat) - 1) )
G0    = exp(F_store / F_sat)
B     = (2*pi/lambda) * integral( n2(z) * I(z) dz )
```

Circular polarization applies a 2/3 reduction to n2 (Schimpf et al., Opt. Express 2009).

## Roadmap (toward the platform)

- [ ] Spatial gain profiles (non-uniform pump, from the paper's Fig. 2)
- [ ] ABCD cavity + thermal-lens solver
- [ ] Serrated-aperture / spatial-filter beam-shaping simulation
- [ ] OPCPA pump front-end modeling
- [ ] GPU batch parameter sweeps + web dashboard
- [ ] Import real spectroscopic / beam-profile data

## License

MIT (see LICENSE).
