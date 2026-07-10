# Python 3.11 CI triage playbook

This note turns open issue #3 into an explicit investigation workflow so the next code-bearing pull request can restore confidence in the full matrix instead of rediscovering the same unknowns.

## Problem statement

Documentation and governance work can move independently, but code-bearing pull requests still need a reliable Python 3.11 path. The current gap is not the policy; it is the lack of a short, repeatable reproduction flow.

## Target outcome

Before closing the follow-up issue, a contributor should be able to answer all of the following:
- Does the failure reproduce on a minimal code-bearing branch?
- Which exact step fails: install, import, smoke, validate, or pytest?
- Is the breakage specific to Python 3.11, or is 3.11 simply where an existing assumption becomes visible?
- Can the fix preserve support for 3.10, 3.11, and 3.12?

## Recommended investigation order

1. Start from a branch with a tiny runtime change so the full CI path is exercised.
2. Reproduce locally with a clean virtual environment on Python 3.10, 3.11, and 3.12.
3. Run the same command ladder in each interpreter:
   - `pip install -r requirements.txt`
   - `pip install -e .`
   - `lasersim info`
   - `python run_all.py`
   - `python validate.py`
   - `pytest -q`
4. Record the first failing command rather than only the final failed job.
5. If imports fail, inspect packaging and dependency resolution first.
6. If numerical tests fail, compare tolerances and any interpreter-dependent behavior before changing expected values.
7. If only CI fails, compare the workflow environment, cache behavior, and optional dependency availability against the successful local run.

## Evidence to capture in the fix PR

A follow-up fix branch should include:
- the failing command and its scope,
- the smallest code or workflow change that resolves it,
- regression coverage for the exact failure class,
- green evidence for the repaired Python versions,
- an update to `SECURITY.md` if the root cause involves dependencies, workflow permissions, or unsafe execution behavior.

## Security-sensitive checkpoints

Review these areas before concluding the issue is only a compatibility problem:
- dependency pins and abandoned packages,
- shell commands in CI workflows,
- file-system assumptions in report generation or dashboard flows,
- any use of subprocess calls in the CLI entry point,
- accidental secret exposure in logs or cached artifacts.

## Exit criteria

This playbook is complete only when a future PR can point to a specific repaired failure path and show green matrix evidence, not just a narrowed workflow trigger.
