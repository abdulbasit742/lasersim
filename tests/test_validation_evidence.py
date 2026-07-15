from __future__ import annotations

import json
from pathlib import Path

import pytest

import validate
from validation_evidence import EVIDENCE, EVIDENCE_LEVELS, build_report, validate_registry


def sample_results():
    return [
        validate.Check("energy", True, "final 1280 mJ"),
        validate.Check("safety", False, "NOHD unavailable"),
        validate.Check("walkoff", True, "longer crystal less overlap"),
    ]


def test_registry_matches_every_executable_check():
    validate_registry(validate.CHECK_NAMES)
    assert validate.CHECK_NAMES == tuple(spec.name for spec in validate.CHECKS)
    assert set(validate.CHECK_NAMES) == set(EVIDENCE)
    assert len(validate.CHECKS) == len(EVIDENCE) == 20


def test_registry_rejects_missing_or_orphan_metadata():
    with pytest.raises(ValueError, match="missing evidence"):
        validate_registry([*validate.CHECK_NAMES, "unregistered"])
    with pytest.raises(ValueError, match="orphan evidence"):
        validate_registry(validate.CHECK_NAMES[:-1])


def test_every_evidence_entry_is_specific_and_supported():
    for evidence in EVIDENCE.values():
        assert evidence.level in EVIDENCE_LEVELS
        assert evidence.quantity.strip()
        assert evidence.unit.strip()
        assert evidence.criterion.strip()
        assert evidence.reference.strip()
        assert evidence.reference.lower() not in {"known bound", "reference", "paper"}


def test_report_separates_evidence_levels():
    report = build_report(sample_results())
    assert report["schema_version"] == 1
    assert report["summary"]["total"] == 3
    assert report["summary"]["passed"] == 2
    assert report["summary"]["failed"] == 1
    assert report["summary"]["by_evidence_level"]["literature"] == {
        "passed": 1,
        "failed": 0,
        "total": 1,
    }
    assert report["summary"]["by_evidence_level"]["smoke"]["failed"] == 1
    assert report["checks"][0]["evidence"]["unit"] == "mJ"


def test_report_is_json_serializable_and_names_limitations():
    payload = json.dumps(build_report(sample_results()), sort_keys=True)
    assert "Invariant and smoke checks are not experimental validation" in payload
    assert '"environment"' in payload


def test_text_output_displays_evidence_grade_and_caveat():
    text = validate.render_text(sample_results())
    assert "[LITERATURE" in text
    assert "[SMOKE" in text
    assert "invariant and smoke checks are not experimental validation" in text


def test_run_checks_records_exceptions_under_stable_id():
    def broken_function():
        raise RuntimeError("boom")

    results = validate.run_checks([validate.CheckSpec("stable-id", broken_function)])
    assert len(results) == 1
    assert results[0].name == "stable-id"
    assert results[0].passed is False
    assert results[0].detail == "ERROR: boom"


def test_run_checks_rejects_mismatched_returned_id():
    def wrong_id():
        return validate.Check("other-id", True, "incorrect")

    result = validate.run_checks([validate.CheckSpec("registered-id", wrong_id)])[0]
    assert result == validate.Check(
        "registered-id",
        False,
        "ERROR: check returned mismatched ID 'other-id'",
    )


def test_json_cli_exit_code_reflects_failed_checks(monkeypatch, capsys):
    monkeypatch.setattr(validate, "run_checks", lambda: sample_results())
    assert validate.main(["--format", "json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["failed"] == 1


def test_report_file_refuses_to_clobber(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(validate, "run_checks", lambda: [validate.Check("energy", True, "ok")])
    target = tmp_path / "validation.json"
    assert validate.main(["--format", "json", "--output", str(target)]) == 0
    original = target.read_text(encoding="utf-8")
    assert validate.main(["--format", "json", "--output", str(target)]) == 2
    assert target.read_text(encoding="utf-8") == original
    assert validate.main(["--format", "json", "--output", str(target), "--overwrite"]) == 0
