# Python runtime diagnostics

LASERSIM now includes a zero-dependency diagnostics helper at `environment_report.py` to make Python-version triage reproducible across laptops and CI runners.

## Why this exists

The active follow-up in issue #3 is a Python 3.11 matrix failure that only appears on code-bearing pull requests. This helper captures the exact interpreter, platform, dependency metadata, and import health for a representative slice of LASERSIM modules without requiring optional packages to import successfully first.

## Usage

```bash
python environment_report.py --summary
python environment_report.py --output diagnostics/runtime-report.json
python environment_report.py --module thermal_abcd --module thermal_fem --package numpy --package scipy
```

## Recommended triage flow

1. Run the helper locally on the affected interpreter (for example Python 3.11).
2. Save the JSON artifact when a CI job fails.
3. Compare import failures, missing dependency metadata, and executable paths between green and red environments.
4. Attach the sanitized report to the issue or pull request discussion.

## Safety notes

- The helper only reports package names, versions, interpreter details, and module import errors.
- It does **not** read environment-variable values or dump process secrets.
- It uses only Python's standard library so it remains runnable even when the failing environment cannot install all scientific dependencies.
