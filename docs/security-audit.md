# Validation trust-boundary audit — 2026-07-15

## Changed-area risks addressed

- **Evidence inflation:** literature comparisons, physical bounds, invariants, and smoke checks were previously displayed as one undifferentiated validation score. Each check now declares its evidence grade and limitations.
- **Registry drift:** executable checks and evidence metadata are bound by stable IDs. Missing, orphaned, duplicated, or incomplete entries fail closed.
- **Failure-path report crash:** exceptions are now recorded under the registered check ID, so a failed subsystem still produces a complete machine-readable report.
- **Ambiguous quantities:** every check records a quantity, unit, criterion, and reference/basis.
- **Report clobbering:** output files are not replaced unless `--overwrite` is supplied.
- **Unverifiable CI summary:** CI parses the generated JSON and verifies schema version, check count, zero failures, allowed grades, and required metadata.
- **Overstated documentation:** project and README wording now distinguishes modeling, verification, literature reproduction, and safety certification.

## Data and side effects

The validation command reads model code and parameters, executes local numerical calculations, and optionally writes one report selected by the operator. It performs no network requests, account changes, hardware control, or external messaging.

The JSON report contains tool/runtime versions and scientific results; it is not designed for secrets, patient data, or proprietary experimental data.

## Residual risks

- Evidence metadata is human-authored and still requires scientific peer review.
- Several references describe accepted relations or project design bounds rather than full bibliographic citations with uncertainty budgets.
- A literature-grade check covers only its named quantity and tolerance, not every equation or operating regime in the corresponding engine.
- Floating lower dependency bounds can produce numerical variation across environments; the report records Python and NumPy versions but does not capture the complete installed dependency graph.
- Safety and dermatology engines remain simulations and must not be used as certified safety, clinical, or treatment decisions.
- The package manifest still lists only a subset of the repository's many standalone modules; this change ensures the validation command and metadata are packaged but does not redesign the whole packaging layout.

## Review gate

Before citing LASERSIM results in a publication or design decision, archive the input parameters, software commit, dependency environment, evidence-graded JSON report, numerical resolution, calibration/measurement data where applicable, and an uncertainty analysis reviewed by a domain expert.
