"""Evidence metadata and machine-readable reports for LASERSIM checks."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import platform
from typing import Iterable, Mapping, Sequence

import numpy as np

SCHEMA_VERSION = 1
EVIDENCE_LEVELS = ("literature", "physical_bound", "invariant", "smoke")


@dataclass(frozen=True)
class Evidence:
    level: str
    quantity: str
    unit: str
    criterion: str
    reference: str


EVIDENCE: Mapping[str, Evidence] = {
    "energy": Evidence("literature", "final amplifier energy", "mJ", "950 <= value <= 1600", "Raza et al., Optics Communications 577 (2025) 131413; reported 1280 mJ"),
    "B-integral": Evidence("physical_bound", "peak nonlinear phase", "rad", "value < 3.0", "Common high-energy laser design bound; lower accumulated nonlinear phase is preferred"),
    "polarization": Evidence("invariant", "circular-to-linear n2 reduction ratio", "dimensionless", "value is close to 2/3 within 2%", "Jones-calculus model invariant"),
    "thermal": Evidence("invariant", "rod temperature and focal response", "K / m", "higher heat load raises peak temperature and focal length remains positive", "Radial heat-equation monotonicity and sign invariant"),
    "cooling": Evidence("invariant", "coolant wall temperature rise", "K", "higher flow lowers wall rise at fixed heat load", "Convective cooling monotonicity invariant"),
    "relay": Evidence("physical_bound", "booster beam diameter", "mm", "value > 6", "NILOP relay-chain design-scale bound"),
    "ase": Evidence("physical_bound", "parasitic oscillation margin", "dimensionless", "value < 2", "ASE/parasitic-gain ceiling used by the model"),
    "damage": Evidence("physical_bound", "minimum LIDT headroom", "dimensionless", "value > 0", "Modelled laser-induced damage threshold margin"),
    "oscillator": Evidence("invariant", "steady-state inversion", "m^-3", "steady state clamps at threshold within 1e-6 relative tolerance", "Four-level laser steady-state invariant"),
    "shg": Evidence("invariant", "second-harmonic efficiency", "dimensionless", "efficiency increases between low and high tested intensity", "Undepleted/limited-conversion model monotonicity invariant"),
    "regen": Evidence("physical_bound", "regenerative amplifier buildup", "dimensionless", "energy gain > 1000", "Expected regenerative-amplifier operating-scale bound"),
    "wavefront": Evidence("invariant", "Strehl ratio", "dimensionless", "less defocus yields higher Strehl", "Wavefront-quality monotonicity invariant"),
    "safety": Evidence("smoke", "nominal ocular hazard distance", "m", "value > 0", "Computational sanity check only; not a certified safety assessment"),
    "materials": Evidence("literature", "quantum-defect ordering", "dimensionless", "Yb:YAG < Nd:YAG", "Photon-energy relation for common YAG laser transitions"),
    "dispersion": Evidence("literature", "fused-silica refractive index at 1064 nm", "dimensionless", "1.44 < value < 1.46", "Fused-silica Sellmeier relation near 1064 nm"),
    "storage": Evidence("invariant", "stored-energy efficiency", "dimensionless", "short pump duration stores more than long duration", "Upper-state lifetime/storage monotonicity invariant"),
    "coatings": Evidence("physical_bound", "HR stack reflectivity", "dimensionless", "value > 0.99", "Transfer-matrix high-reflector design bound"),
    "chain_e2e": Evidence("smoke", "UV chain output", "mJ / nm", "wavelength equals 355 nm and energy is positive", "End-to-end execution sanity check; not a literature validation"),
    "ranging": Evidence("smoke", "returned photons at 1000 km", "photons", "value > 0", "Link-budget execution sanity check"),
    "walkoff": Evidence("invariant", "nonlinear-crystal overlap fraction", "dimensionless", "5 mm overlap exceeds 50 mm overlap", "Spatial/temporal walk-off monotonicity invariant"),
}


def validate_registry(check_names: Iterable[str]) -> None:
    """Fail closed when evidence metadata and executable checks diverge."""
    names = tuple(check_names)
    missing = sorted(set(names) - set(EVIDENCE))
    extra = sorted(set(EVIDENCE) - set(names))
    problems = []
    if len(names) != len(set(names)):
        problems.append("duplicate check names")
    if missing:
        problems.append(f"missing evidence: {', '.join(missing)}")
    if extra:
        problems.append(f"orphan evidence: {', '.join(extra)}")
    for name in names:
        evidence = EVIDENCE.get(name)
        if evidence is None:
            continue
        if evidence.level not in EVIDENCE_LEVELS:
            problems.append(f"{name}: unsupported evidence level {evidence.level!r}")
        for field_name, value in asdict(evidence).items():
            if not isinstance(value, str) or not value.strip():
                problems.append(f"{name}: empty {field_name}")
    if problems:
        raise ValueError("invalid validation registry: " + "; ".join(problems))


def build_report(results: Sequence[object], generated_at: datetime | None = None) -> dict:
    """Build a stable JSON-serializable report from Check-like objects."""
    timestamp = generated_at or datetime.now(timezone.utc)
    checks = []
    by_level = {level: {"passed": 0, "failed": 0, "total": 0} for level in EVIDENCE_LEVELS}
    for result in results:
        name = str(getattr(result, "name"))
        passed = bool(getattr(result, "passed"))
        detail = str(getattr(result, "detail"))
        evidence = EVIDENCE[name]
        by_level[evidence.level]["total"] += 1
        by_level[evidence.level]["passed" if passed else "failed"] += 1
        checks.append({
            "id": name,
            "passed": passed,
            "detail": detail,
            "evidence": asdict(evidence),
        })
    passed_count = sum(item["passed"] for item in checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": timestamp.astimezone(timezone.utc).isoformat(),
        "tool": "LASERSIM",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "summary": {
            "total": len(checks),
            "passed": passed_count,
            "failed": len(checks) - passed_count,
            "by_evidence_level": by_level,
        },
        "checks": checks,
        "limitations": [
            "Invariant and smoke checks are not experimental validation.",
            "Literature checks reproduce only the stated quantity and tolerance.",
            "Safety outputs are model estimates and require qualified professional review.",
        ],
    }
