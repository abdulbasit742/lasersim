# LASERSIM Architecture

How the ~50 engines fit together, following the physical signal flow of a
high-energy picosecond laser system from wall socket to application.

```
  WALL SOCKET
      |  efficiency.py        (electrical -> optical budget)
      v
  PUMP DIODES --- pump_diode.py     (808 nm, current -> absorbed power)
      |
      v
  GAIN MEDIUM --- materials.py      (Nd:YAG / Yb:YAG / ... properties)
      |           laser_platform.py (oscillator rate-equation dynamics)
      |           spatial_gain.py   (2D non-uniform pump -> gain map)
      |           ase.py            (parasitic storage ceiling)
      v
  FRONT END  --- regen.py           (regenerative pre-amp buildup)
      |           cpa.py            (chirped-pulse stretch)
      v
  AMPLIFIER  --- amplifier.py       (Frantz-Nodvik multi-pass chain)
  CHAIN          temporal.py        (in-pulse gain saturation/reshaping)
      |           gain_narrowing.py  (spectral narrowing -> TL floor)
      |           polarization.py   (circular-pol n2 mitigation)
      |           depolarization.py (thermal birefringence loss)
      v
  THERMAL    --- thermal_abcd.py    (lumped thermal lens + cavity)
  MANAGEMENT     thermal_fem.py     (radial heat solve, stress)
      |           cooling.py         (coolant convective removal)
      |           reprate.py         (average-power / rep-rate limit)
      v
  BEAM       --- beam_shaping.py    (serrated aperture + spatial filter)
  TRANSPORT      relay_imaging.py   (Gaussian q relay telescopes)
      |           propagation.py     (self-focusing / NLSE)
      |           raman.py           (stimulated Raman loss)
      |           beam_quality.py    (M^2, BPP, brightness)
      |           wavefront.py       (Zernike aberrations, Strehl)
      |           adaptive_optics.py (deformable-mirror correction)
      |           pointing.py        (far-field pointing stability)
      v
  HARMONICS  --- shg.py             (1064 -> 532)
      |           thg.py             (1064 -> 355)
      |           opcpa.py           (parametric amplification)
      v
  SAFETY     --- damage.py          (LIDT fluence margin)
  & DIAGNOSTICS  safety.py          (eye/skin hazard, NOHD)
      |           jitter.py          (pump-seed timing -> energy stability)
      |           autocorrelation.py (pulse-duration measurement)
      |           contrast.py        (ASE pedestal / pre-pulse)
      v
  APPLICATIONS - ranging.py         (satellite/lunar laser ranging)
                 ablation.py        (material micromachining)
                 plasma.py          (soft X-ray / plasma)
                 dermatology.py     (tattoo/pigment removal)
```

## Cross-cutting tooling

| File | Role |
|---|---|
| `config.py` | define any chain as JSON/YAML data |
| `full_system.py` | run the whole NILOP pipeline, audit vs paper |
| `sweep.py` | batch / GPU parameter sweeps |
| `sensitivity.py` | Monte Carlo tolerancing vs the 1.1% RMS spec |
| `landscape.py` | benchmark vs published ps Nd:YAG systems |
| `data_io.py` | import + fit measured lab data |
| `report.py` | paper-style HTML/PDF report |
| `dashboard.py` | interactive Streamlit UI |
| `validate.py` | cross-engine pass/fail scorecard |
| `examples.py` | guided end-to-end tour |
| `cli.py` | unified `lasersim <engine>` entry point |

## Design rules

1. **One physics concept per file.** Each engine stands alone and is runnable.
2. **Every engine has a `tests/test_*.py`** asserting against a paper number or
   a physical bound.
3. **Data, not hard-code.** `materials.py` and `config.py` hold the swappable
   inputs so the platform isn't locked to one system.
4. **Grounded in the paper.** Defaults reproduce Raza et al., Opt. Commun. 577
   (2025) 131413; `validate.py` keeps them honest.
