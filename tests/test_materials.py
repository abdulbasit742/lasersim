"""Validate the material database."""
import numpy as np

from materials import get, DATABASE, to_cavity_kwargs


def test_ndyag_matches_platform_defaults():
    m = get("Nd:YAG")
    assert m.lam_nm == 1064.0
    assert np.isclose(m.sigma_m2, 2.8e-23)
    assert np.isclose(m.tau_us, 230.0)


def test_quantum_defect_positive_and_small():
    for m in DATABASE.values():
        assert 0.0 < m.quantum_defect < 0.5


def test_yb_yag_smaller_defect_than_nd_yag():
    assert get("Yb:YAG").quantum_defect < get("Nd:YAG").quantum_defect


def test_to_cavity_kwargs_builds_cavity():
    from laser_platform import Cavity
    cav = Cavity(**to_cavity_kwargs(get("Nd:YAG")))
    assert cav.N_threshold > 0


def test_unknown_material_raises():
    try:
        get("Unobtainium")
        assert False
    except KeyError:
        pass


def test_tisapph_broadest_bandwidth():
    bws = {m.name: m.bandwidth_nm for m in DATABASE.values()}
    assert max(bws, key=bws.get) == "Ti:Sapphire"
