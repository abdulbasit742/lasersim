# LASERSIM quickstart and workflow map

This playbook gives contributors a fast path from a fresh checkout to the main runtime, validation, and reporting flows.

## 1. Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Why these steps matter:
- `requirements.txt` installs the scientific runtime stack used by the standalone scripts.
- `pip install -e .` installs the `lasersim` command so contributors can exercise engines from one entry point.

## 2. Fast validation ladder

Start with the lightest checks and only move deeper when the previous step passes.

```bash
lasersim info
lasersim system
lasersim validate
lasersim examples
python run_all.py
python report.py
pytest -q
```

What each command is for:
- `lasersim info` lists the available engines and confirms the editable install is working.
- `lasersim system` exercises the whole NILOP pipeline against the paper-oriented workflow.
- `lasersim validate` runs the cross-engine pass/fail scorecard.
- `lasersim examples` provides the guided end-to-end tour used for onboarding.
- `python run_all.py` runs the whole-platform smoke harness.
- `python report.py` generates the paper-style HTML report and can also emit a PDF when optional report tooling is present.
- `pytest -q` is the broad regression gate for pull requests.

## 3. Makefile shortcuts

Use the Make targets when you want a shorter command surface:

```bash
make install
make test
make smoke
make validate
```

These currently map to the same core installation, pytest, smoke-harness, and validation flows used elsewhere in the repository.

## 4. Interactive and analysis workflows

Two high-signal workflows are easy to miss during review:
- `streamlit run dashboard.py` opens the interactive dashboard for exploratory analysis.
- `python report.py --pdf` extends the HTML report flow with PDF output when the optional report dependency is available.

## 5. How to use this during pull requests

Recommended review order:
1. Confirm installation still works on a clean environment.
2. Run the validation ladder up to the deepest step that matches the risk of the change.
3. For code-bearing pull requests, make sure the full Python matrix is green before merge.
4. Re-check `SECURITY.md` whenever dependencies, CI workflows, file IO, or shell execution paths change.

## 6. Security reminders for contributors

- Do not commit datasets with sensitive information, API keys, or local notebook outputs.
- Keep generated artifacts out of commits unless they are intentionally versioned documentation.
- Treat workflow edits and dependency bumps as security-sensitive changes and review them with the same discipline as runtime code.

## 7. Related references

- `ARCHITECTURE.md` for the module-by-module map.
- `BENCHMARKS.md` for benchmark and reproduction-oriented commands.
- `CONTRIBUTING.md` for the contributor checklist.
- `SECURITY.md` for the active audit log and reporting policy.
