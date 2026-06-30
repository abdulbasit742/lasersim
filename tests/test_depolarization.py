"""Validate thermal depolarization loss."""
from depolarization import DepolRod


def test_no_power_no_loss():
    rod = DepolRod()
    assert rod.depol_fraction(0.0) < 1e-9


def test_loss_increases_with_power():
    rod = DepolRod()
    assert rod.depol_fraction(300) > rod.depol_fraction(50)


def test_compensation_reduces_loss():
    rod = DepolRod()
    assert rod.depol_fraction(200, compensated=True) < rod.depol_fraction(200, compensated=False)


def test_loss_is_a_fraction():
    rod = DepolRod()
    for p in (50, 200, 400):
        f = rod.depol_fraction(p)
        assert 0.0 <= f <= 1.0
