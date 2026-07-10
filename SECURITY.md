# Security

## Security policy

LASERSIM is a local-first scientific simulation project with a comparatively small network-facing attack surface. The main practical risks are accidental secret commits, compromised dependencies, and unsafe CI defaults.

Please report suspected vulnerabilities privately to the repository owner and avoid public disclosure until a fix is available.

## Baseline audit — Fri Jul 10, 2026

### Scope

- Branch: `world-class-polish`
- Repository surfaces reviewed in this pass:
  - current tracked repository tree
  - GitHub Actions workflow configuration added in this branch
  - dependency hygiene automation for Python packages
  - secret-regression protections for future pull requests

### Evidence collected

- Added a least-privilege GitHub Actions workflow at `.github/workflows/security.yml`
- Added Dependabot coverage for `pip` and `github-actions`
- Added PR checklist items requiring validation and security review
- Reviewed the repository shape: pure Python scientific modules, tests, and docs; no web server, auth, database, or external secret-dependent runtime committed in this branch

### Findings

| ID | Severity | Finding | Status | Remediation |
| --- | --- | --- | --- | --- |
| SEC-001 | Low | No automated secret-regression gate existed for future pull requests. | Fixed on this branch | Added tracked-file secret guard and forbidden-file checks in CI. |
| SEC-002 | Low | Dependency update/audit automation was missing. | Fixed on this branch | Added Dependabot plus a scheduled `pip-audit` security workflow. |
| SEC-003 | Low | Security review expectations were implicit rather than documented. | Fixed on this branch | Added this file and PR security checklist. |

### Residual risk

- Historical commit-by-commit secret review was not exhaustively completed in this pass.
- Dependency risk remains an ongoing maintenance concern and now depends on the scheduled workflow plus human review.
- Scientific correctness is validated by tests, but numerical-model misuse is still possible if users supply unrealistic physical parameters.

## Safe handling rules

- Never commit `.env` files, API tokens, private keys, or raw credentials.
- Keep risky experiments local and out of the tracked tree.
- Treat generated reports as public unless reviewed for sensitive data.
- Prefer deterministic tests and fixed example parameters so regressions are easy to spot.

## Secure development checklist

Before merge:

1. Run project tests.
2. Review changed files for secret material and unsafe sample data.
3. Confirm CI permissions stay least-privilege.
4. Document any residual numerical or operational risk introduced by the change.
5. Add regression tests for bug fixes and safety-sensitive logic.
