# Skill registry

This registry tracks concrete, acceptance-tested improvements for LASERSIM. Prioritize security first, then scientific trust, then usability.

## Done on `world-class-polish`

### SKILL-001 — Baseline security automation

- **Status:** Done on branch
- **Why it matters:** Prevents accidental secret regressions and adds recurring dependency checks.
- **Acceptance test:**
  - `security.yml` fails when a tracked `.env`, private key, or common token pattern is added.
  - Dependabot monitors Python and GitHub Actions dependencies.

### SKILL-002 — Contributor and citation metadata

- **Status:** Done on branch
- **Why it matters:** Makes the project easier to maintain and cite in academic contexts.
- **Acceptance test:**
  - Repository contains `CONTRIBUTING.md` and `CITATION.cff`.

## Ready next

### SKILL-003 — README quickstart and workflow map

- **Priority:** High
- **Why it matters:** New users need a fast path from install to first validated simulation.
- **Acceptance test:**
  - README shows one minimal install path.
  - README shows one minimal simulation command.
  - README links to architecture, benchmarks, validation, and security docs.

### SKILL-004 — Numerical validation matrix expansion

- **Priority:** High
- **Why it matters:** Scientific trust depends on checking representative physics regimes, not only smoke tests.
- **Acceptance test:**
  - Add at least 3 focused regression tests for fragile numerical assumptions.
  - Each test names the physical regime or invariant being protected.

### SKILL-005 — Benchmark reproducibility harness

- **Priority:** Medium
- **Why it matters:** Benchmark claims should be reproducible and versioned.
- **Acceptance test:**
  - A documented command regenerates benchmark outputs.
  - Benchmarks state hardware/software assumptions.

### SKILL-006 — Packaging and module boundary cleanup

- **Priority:** Medium
- **Why it matters:** The project is still script-heavy, which raises maintenance cost as it grows.
- **Acceptance test:**
  - Public entry points are documented.
  - Internal helpers are grouped behind stable module boundaries.
  - Imports remain backwards-compatible or migration notes are added.
