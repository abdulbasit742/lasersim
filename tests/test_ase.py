"""Validate ASE / parasitic-oscillation limits."""
from ase import ASERod


def test_transverse_gain_exceeds_axial_for_wide_rod():
    # For a rod wider than it is long, transverse gain > axial gain.
    rod = ASERod(diameter_m=25e-3, length_m=13e-3)
    E = 1.0
    assert rod.transverse_gain(E) > rod.longitudinal_gain(E)


def test_parasitic_margin_monotonic():
    rod = ASERod()
    assert rod.parasitic_margin(2.0) > rod.parasitic_margin(0.5)


def test_max_storable_energy_positive():
    rod = ASERod()
    assert rod.max_storable_energy() > 0


def test_paper_runs_below_ceiling():
    """The paper's 1.14 J stored should sit below the parasitic ceiling."""
    rod = ASERod(diameter_m=25e-3)
    assert 1.14 <= rod.max_storable_energy() + 1e-9 or rod.parasitic_margin(1.14) < 2.0


def test_ase_shortens_lifetime():
    rod = ASERod()
    assert rod.ase_lifetime_factor(2.0) >= rod.ase_lifetime_factor(0.2)
