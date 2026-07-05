# lasersim -- Novelty & Research Contributions

`lasersim` began as a broad, textbook-honest **forward** simulator of a
diode-pumped solid-state / CPA laser chain (Silfvast, *Laser Fundamentals*,
2e): saturated amplification, cavity modes, dispersion & pulse compression,
second/third-harmonic generation, thermal lensing, beam quality, damage, and
~60 coupled physics engines with a validation suite against analytic limits.

A forward simulator answers *"given this design, what does the laser do?"*
That is useful but not, by itself, novel. The contributions below turn the
platform into a **research instrument**.

## Contribution 1 -- Constraint-aware inverse design (`inverse_design.py`)

We invert the simulator. Given a **target output specification** (pulse
energy, duration, beam quality M^2, harmonic-conversion efficiency), the
engine automatically searches the physical design box (pump power, gain-medium
length, seed energy, residual GDD, doubling-crystal length) for the design
that best meets the target, **subject to the optical-damage fluence
constraint**.

- Objective: weighted squared *relative* error to target + damage penalty.
- Optimizer: SciPy differential evolution + Nelder-Mead polish when available;
  a self-contained numpy "CMA-lite" (annealed Gaussian coordinate descent with
  random restarts) otherwise, so it runs anywhere.
- Output: a recovered, manufacturable design plus a target-vs-achieved table.

This reframes laser system design as a solved inverse problem rather than
manual trial-and-error over the forward model.

## Contribution 2 -- Validated ML surrogate (`surrogate.py`)

Inverse design and sensitivity analysis call the forward model thousands of
times. We train a **data-driven surrogate** f_hat(design) ~= simulate(design)
from a sampled design-of-experiments:

- Model: scikit-learn MLP when available; otherwise numpy ridge regression on
  a quadratic (design + squares + pairwise) feature expansion.
- We report **held-out R^2 per metric** so fidelity is quantified and auditable.
- Measured wall-clock **speedup** of surrogate vs physics per evaluation is
  reported, enabling ~100-1000x faster design-space exploration.

The combination -- a learned surrogate that *accelerates constraint-aware
inverse design of a laser* -- is the core novelty.

## Contribution 3 -- Reproducible, one-command results (`make_results.py`)

A single command runs the whole story (baseline -> pump-power tradeoff sweep
-> surrogate training + R^2 + speedup -> headline inverse-design solve) and
writes `results/RESULTS.md`, CSVs, and figures. Every number is regenerable
and the reference model needs nothing beyond the standard library.

## Honesty statement

This is a **research / assistive design simulator**, not a validated
engineering sign-off tool. The reference forward model uses standard
closed-form laser physics chosen to be transparent and monotone; routing
`--full` through the complete `laser_platform` engine chain raises fidelity.
The inverse-design and surrogate layers are model-agnostic -- they wrap
whatever forward map is provided.

## Reproduce

```bash
pip install -r requirements.txt        # numpy; scipy/sklearn/matplotlib optional
python forward_model.py --smoke
python inverse_design.py --smoke
python surrogate.py --smoke
python make_results.py                 # writes results/RESULTS.md (+ CSV, PNG)
```
