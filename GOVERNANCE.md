# Governance

## Project goal

LASERSIM should remain a practical, readable scientific software project for laser-system modeling, not a dumping ground for disconnected scripts.

## Decision rules

1. Security and reproducibility outrank feature count.
2. Small, reviewable pull requests are preferred over broad rewrites.
3. Numerical changes must include tests, a benchmark note, or a short physical justification.
4. New dependencies must earn their keep and remain actively maintained.
5. CI and docs should evolve with the code, not after the fact.

## Maintainer expectations

- Keep default workflows safe for local use.
- Reject secret material, private datasets, and unverifiable claims.
- Prefer deterministic examples and explicit physical units.
- Record notable risk decisions in pull requests or `SECURITY.md`.

## Merge policy

A change is ready to merge when:

- tests or documented validation pass,
- docs reflect the new behavior,
- security review does not reveal active critical or high-risk findings,
- the diff is coherent enough to maintain.

## Roadmap discipline

Use `docs/SKILL_REGISTRY.md` as the deduplicated improvement queue. Add skills only when they have a concrete acceptance test and obvious user or maintainer value.
