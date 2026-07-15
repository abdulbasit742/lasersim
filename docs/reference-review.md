# Reference review

Reviewed on 2026-07-15 before implementing the evidence-graded validation report.

## openmc-dev/validation

Adopted:

- benchmark cases should identify the reference problem rather than rely on a generic “validated” label;
- reproducible comparisons belong in version-controlled test inputs and reports;
- a benchmark result is scoped to the quantity and case being compared.

Not adopted:

- OpenMC-specific benchmark models, nuclear data, or execution tooling.

## astropy/astropy

Adopted:

- scientific quantities should carry explicit units or be labelled dimensionless;
- machine-readable scientific outputs should preserve metadata needed for interpretation;
- tests should reject ambiguity at quantity boundaries.

Not adopted:

- the Astropy units package or a project-wide units migration. Existing LASERSIM APIs remain unchanged; the validation layer records units explicitly.

## PlasmaPy/PlasmaPy

Adopted:

- scientific software should distinguish input/model validation from empirical validation;
- physical assumptions and limitations should be visible alongside results;
- regression tests should enforce scientific metadata contracts.

Not adopted:

- PlasmaPy's package architecture, decorators, or domain-specific particle/plasma models.

## Resulting decision

The highest-value change was not another laser engine. It was making the existing scorecard honest and auditable. LASERSIM now separates literature comparisons, physical bounds, model invariants, and smoke checks; records quantity, unit, criterion, and reference; and emits the same contract as text or JSON.
