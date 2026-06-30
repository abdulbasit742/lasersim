"""The expanded validation capstone should pass every check."""
from validate import CHECKS, main


def test_all_checks_pass():
    for fn in CHECKS:
        c = fn()
        assert c.passed, f"{c.name} failed: {c.detail}"


def test_main_returns_zero():
    assert main() == 0


def test_have_many_checks():
    assert len(CHECKS) >= 20
