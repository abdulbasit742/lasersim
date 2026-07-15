# AGENTS.md

## Scope

These instructions apply to the entire `abdulbasit742/lasersim` repository. More specific `AGENTS.md` or `AGENTS.override.md` files may refine them.

Project: **LASERSIM**, a Python laser-modeling platform with evidence-graded scientific verification.

## Working method

1. Read `README.md`, `docs/validation-evidence.md`, the relevant model, and nearby tests before editing.
2. Preserve unrelated user changes and make the smallest coherent scientific change.
3. State physical assumptions, operating regime, quantity, and units at model boundaries.
4. Do not hand-edit generated reports, vendored code, dependency directories, model outputs, or datasets unless the task explicitly targets them.
5. Update tests and documentation when formulas, defaults, units, validation criteria, public APIs, or setup commands change.

## Commands

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
lasersim validate
lasersim validate --format json --output validation-report.json
```

Use `--overwrite` only when deliberately replacing a validation report.

## Scientific verification rules

- Do not use “validated” without naming the evidence grade and quantity being checked.
- New scorecard checks require a stable `CheckSpec` ID plus matching metadata in `validation_evidence.py`.
- Evidence levels are exactly: `literature`, `physical_bound`, `invariant`, and `smoke`.
- Record a meaningful quantity, unit (or `dimensionless`), criterion, and precise reference/basis.
- A smoke or invariant check must never be described as experimental or literature validation.
- Preserve reproducibility: record parameters, seeds, numerical resolution, software commit, and relevant dependency versions.
- Treat safety and dermatology outputs as model estimates requiring qualified professional review.

## Verification

- Run the narrowest relevant tests first, then the full available suite and evidence report.
- Confirm JSON report schema, check count, evidence metadata, and exit status for validation changes.
- Test exception paths, registry drift, unit/criterion metadata, and report-file overwrite behavior.
- Never report a check as passed unless it was actually run. State unavailable checks and the concrete reason.

## Security and side effects

- Never commit secrets, credentials, private keys, personal/clinical data, or populated environment files.
- Treat experiments, hardware control, deployments, external network calls, destructive operations, and large generated datasets as side effects requiring explicit authorization.
- Avoid logging proprietary measurements or raw data that may identify people or facilities.
- Validation reports should contain scientific outputs and runtime metadata only.

## Completion checklist

- Relevant tests and `lasersim validate` pass, or unavailable checks are documented.
- Executable check IDs and evidence metadata remain one-to-one.
- Changed claims accurately distinguish literature comparisons, bounds, invariants, and smoke tests.
- No secrets, generated reports, large outputs, or unrelated formatting churn are introduced.
