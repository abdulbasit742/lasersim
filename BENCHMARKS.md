# Benchmarks: LASERSIM vs. the NILOP 1.28 J Nd:YAG paper

This document records how LASERSIM reproduces the published results of:

> K. Raza et al., "An all-diode pumped 1.28-Joule, 200-picosecond Nd:YAG laser
> amplifier at 10 Hz," *Optics Communications* **577** (2025) 131413.

Regenerate everything with:

```bash
python full_system.py      # energy + B-integral chain
python validate.py         # cross-engine pass/fail scorecard
python report.py           # paper-style HTML report
```

## Table 2 reproduction: energy through the chain

Measured values from the paper vs. the Frantz-Nodvik model in `amplifier.py`.

| Stage | Input (mJ) | Measured (mJ) | Paper calc (mJ) | LASERSIM target |
|---|---|---|---|---|
| AMP-1 1st pass (GM1) | 15 | 70 | 122 | amplifies |
| AMP-1 2nd pass (GM1) | 70 | 200 | 216 | ~200 |
| Serrated aperture | 200 | 160 | - | 0.80x |
| AMP-2 1st pass (GM2) | 140 | 470 | 561 | amplifies |
| AMP-2 2nd pass (GM2) | 470 | 755 | 838 | ~755 |
| AMP-3 1st stage (GM3) | 720 | 980 | 1006 | amplifies |
| AMP-3 2nd stage (GM4) | 980 | 1280 | 1286 | **~1280** |

## Table 1 reproduction: fluence, peak power, B-integral

From the paper's Table 1, used as the validation targets for `damage.py` and the
B-integral check in `amplifier.py`.

| Parameter | GM1 | GM2 | GM3 | GM4 |
|---|---|---|---|---|
| Average fluence (J/cm^2) | 0.13 | 0.21 | 0.12 | 0.16 |
| Peak fluence (J/cm^2) | 1.08 | 1.35 | 0.68 | 0.89 |
| Peak power (GW) | 1.0 | 3.78 | 4.90 | 6.40 |
| B-integral | 1.55 | 1.94 | 1.0 | 1.28 |

All B-integrals are below the ~3 rad self-focusing safe limit, which
`validate.py` asserts on every run.

## System-level numbers

| Quantity | Paper | Notes |
|---|---|---|
| Output energy | 1.28 J | reproduced by `full_system.py` |
| Pulse duration | <200 ps | used by `temporal.py`, `damage.py` |
| Repetition rate | 10 Hz | sets duty cycle in `thermal_abcd.py` |
| Peak power | 6.4 GW | final-stage check |
| Energy stability | 1.1% RMS | operational spec |
| Seed energy | 17 mJ | chain input |

## Physical constants used

| Constant | Value | Source |
|---|---|---|
| n2 (linear pol.) | 6.21e-16 cm^2/W | paper ref. [30] |
| Circular-pol n2 factor | 2/3 | Schimpf et al., Opt. Express 2009 |
| Saturation fluence F_sat | 0.3 J/cm^2 | paper (few-100 ps Nd:YAG) |
| Stored energy GM1/GM2 | 1.622 J | paper |
| Stored energy GM3/GM4 | 1.14 J | paper |
