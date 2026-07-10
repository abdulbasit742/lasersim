"""Runtime diagnostics helpers for reproducing CI/test environment issues.

This module avoids third-party imports so it can run even when optional
dependencies are missing or broken on a specific interpreter.
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Iterable

DEFAULT_DEPENDENCIES = (
    "numpy",
    "scipy",
    "matplotlib",
    "pytest",
    "streamlit",
    "pandas",
)

DEFAULT_MODULES = (
    "ablation",
    "amplifier",
    "cli",
    "propagation",
    "thermal_fem",
    "validate",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _dependency_record(package_name: str) -> dict[str, object]:
    try:
        version = metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return {"installed": False, "version": None, "error": "not-installed"}
    except Exception as exc:  # pragma: no cover - defensive guard for unusual metadata failures
        return {
            "installed": False,
            "version": None,
            "error": f"{type(exc).__name__}: {exc}",
        }

    return {"installed": True, "version": version, "error": None}


def _import_record(module_name: str) -> dict[str, object]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return {
            "module": module_name,
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    return {
        "module": module_name,
        "ok": True,
        "file": getattr(module, "__file__", None),
        "error_type": None,
        "error": None,
    }


def _normalize(items: Iterable[str] | None, defaults: tuple[str, ...]) -> list[str]:
    values = [item for item in (items or defaults) if item]
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped


def build_environment_report(
    module_names: Iterable[str] | None = None,
    package_names: Iterable[str] | None = None,
) -> dict[str, object]:
    """Collect a JSON-serialisable snapshot of runtime compatibility state."""
    selected_modules = _normalize(module_names, DEFAULT_MODULES)
    selected_packages = _normalize(package_names, DEFAULT_DEPENDENCIES)

    dependency_versions = {
        package_name: _dependency_record(package_name) for package_name in selected_packages
    }
    module_imports = [_import_record(module_name) for module_name in selected_modules]

    return {
        "generated_at": _utc_now(),
        "python": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
            },
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "dependency_versions": dependency_versions,
        "module_imports": module_imports,
    }


def format_summary(report: dict[str, object]) -> str:
    dependency_versions = report["dependency_versions"]
    assert isinstance(dependency_versions, dict)
    module_imports = report["module_imports"]
    assert isinstance(module_imports, list)

    installed = sum(
        1 for record in dependency_versions.values() if isinstance(record, dict) and record.get("installed")
    )
    healthy_imports = sum(
        1 for record in module_imports if isinstance(record, dict) and record.get("ok")
    )

    python_section = report["python"]
    assert isinstance(python_section, dict)
    version_info = python_section["version_info"]
    assert isinstance(version_info, dict)

    return (
        f"Python {version_info['major']}.{version_info['minor']}.{version_info['micro']} | "
        f"dependencies installed: {installed}/{len(dependency_versions)} | "
        f"module imports passing: {healthy_imports}/{len(module_imports)}"
    )


def write_environment_report(
    destination: str | Path,
    module_names: Iterable[str] | None = None,
    package_names: Iterable[str] | None = None,
) -> Path:
    output_path = Path(destination)
    report = build_environment_report(module_names=module_names, package_names=package_names)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture a runtime compatibility report for LASERSIM support and CI triage."
    )
    parser.add_argument(
        "--module",
        dest="modules",
        action="append",
        default=None,
        help="Additional module import to probe. Can be provided multiple times.",
    )
    parser.add_argument(
        "--package",
        dest="packages",
        action="append",
        default=None,
        help="Additional package metadata lookup to probe. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON file path to write the report to.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary after producing the report.",
    )
    args = parser.parse_args(argv)

    report = build_environment_report(module_names=args.modules, package_names=args.packages)

    if args.output is not None:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.summary:
        print(format_summary(report))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
