# Validation evidence contract

LASERSIM uses the word **verification** for the full automated scorecard. Each check then declares a narrower evidence grade. These grades are not interchangeable.

## Grades

### Literature

A computed quantity or ordering is compared with a cited publication or established material relation. The check covers only the named quantity, operating point, and tolerance; it does not validate the whole engine.

### Physical bound

A result is compared with a documented engineering or model limit, such as positive damage headroom or a maximum nonlinear phase. Passing the bound does not prove agreement with an experiment.

### Invariant

The implementation is checked against a sign, ordering, monotonicity, or conservation-like property expected inside the model. This is useful for regression detection but is not experimental validation.

### Smoke

An end-to-end path is executed and checked for a bounded, plausible result. Smoke checks show that a path runs; they do not establish scientific accuracy.

## Required metadata

Every executable check has a stable ID and an entry in `validation_evidence.py` containing:

- evidence level;
- physical quantity or modeled behavior;
- unit, including `dimensionless` where appropriate;
- exact criterion;
- reference or explicit basis.

`validate_registry()` fails when executable IDs and evidence metadata diverge, when IDs are duplicated, or when required metadata is empty.

## Reports

```bash
lasersim validate
lasersim validate --format json --output validation-report.json
```

The JSON schema version is currently `1`. It includes environment versions, per-grade totals, each check's metadata and result, and limitations. Report files are not overwritten unless `--overwrite` is explicitly supplied.

## Adding a check

1. Add a `CheckSpec` with a stable ID in `validate.py`.
2. Return a `Check` with exactly the same ID.
3. Add complete evidence metadata in `validation_evidence.py`.
4. Add or update focused tests.
5. Cite the precise source or explain the model invariant/bound.
6. Do not upgrade an invariant or smoke check to `literature` without a direct, documented comparison.

## Interpretation limits

- A green scorecard is not a certification of an optical design.
- Safety outputs require review by qualified laser-safety personnel.
- Input assumptions, material data, numerical resolution, and operating regimes remain part of the uncertainty.
- Experimental validation needs traceable measurements, calibration, uncertainty analysis, and an appropriate comparison protocol outside this automated suite.
