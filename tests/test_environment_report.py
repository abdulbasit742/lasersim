from environment_report import build_environment_report, format_summary


def test_build_environment_report_returns_expected_shape():
    report = build_environment_report(
        module_names=["json", "sys"],
        package_names=["pytest", "definitely-not-installed-package"],
    )

    assert report["python"]["version_info"]["major"] >= 3
    assert report["platform"]["system"]

    dependency_versions = report["dependency_versions"]
    assert dependency_versions["pytest"]["installed"] is True
    assert dependency_versions["definitely-not-installed-package"]["installed"] is False

    module_imports = {item["module"]: item for item in report["module_imports"]}
    assert module_imports["json"]["ok"] is True
    assert module_imports["sys"]["ok"] is True


def test_format_summary_counts_successes_and_failures():
    report = build_environment_report(
        module_names=["json", "definitely_missing_module_for_lasersim"],
        package_names=["pytest", "definitely-not-installed-package"],
    )

    summary = format_summary(report)

    assert "Python " in summary
    assert "dependencies installed: 1/2" in summary
    assert "module imports passing: 1/2" in summary
