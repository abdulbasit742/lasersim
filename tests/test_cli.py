"""Validate the unified CLI dispatch."""
import cli


def test_info_runs():
    assert cli.main(["info"]) == 0


def test_default_is_info():
    assert cli.main([]) == 0


def test_unknown_command_falls_back():
    # unknown command returns the info screen (exit 0), doesn't crash
    assert cli.main(["definitely-not-an-engine"]) == 0


def test_engines_registered():
    for key in ("oscillator", "amplifier", "system", "opcpa", "sweep", "fit"):
        assert key in cli.ENGINES


def test_system_pipeline_via_cli():
    # delegating to full_system should run end-to-end without error
    assert cli.main(["system"]) == 0
