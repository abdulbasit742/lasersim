"""Validate laser hazard analysis."""
from safety import BeamHazard


def test_fluence_drops_with_distance():
    h = BeamHazard()
    assert h.fluence_at(100) < h.fluence_at(0)


def test_joule_beam_is_class4():
    h = BeamHazard(energy_J=1.28)
    assert "Class 4" in h.hazard_class()


def test_nohd_positive_for_dangerous_beam():
    h = BeamHazard(energy_J=1.28)
    assert h.nohd_m() > 0


def test_fluence_at_nohd_near_mpe():
    import numpy as np
    h = BeamHazard()
    assert np.isclose(h.fluence_at(h.nohd_m()), h.mpe_Jcm2, rtol=0.05)


def test_required_od_positive_at_source():
    h = BeamHazard()
    assert h.required_OD(0.0) > 0
