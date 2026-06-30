"""Validate third-harmonic / sum-frequency generation."""
from thg import SFGCrystal, thg_chain


def test_sfg_efficiency_bounded():
    c = SFGCrystal()
    for ir, ig in [(0, 0), (1e13, 1e13), (1e15, 1e15)]:
        e = c.sfg_efficiency(ir, ig)
        assert 0.0 <= e <= 1.0


def test_sfg_needs_both_beams():
    c = SFGCrystal()
    assert c.sfg_efficiency(1e13, 0.0) == 0.0
    assert c.sfg_efficiency(0.0, 1e13) == 0.0
    assert c.sfg_efficiency(1e13, 1e13) > 0.0


def test_thg_produces_uv():
    r = thg_chain(1.28, 200e-12, 0.8)
    assert r["e_uv_mJ"] > 0
    assert 0.0 <= r["thg_overall"] <= 1.0


def test_uv_yield_has_optimum_green_fraction():
    """Very low or very high green fraction should both yield less UV than a
    middle split."""
    low = thg_chain(1.28, 200e-12, 0.8, green_fraction=0.05)["e_uv_mJ"]
    mid = thg_chain(1.28, 200e-12, 0.8, green_fraction=0.35)["e_uv_mJ"]
    high = thg_chain(1.28, 200e-12, 0.8, green_fraction=0.95)["e_uv_mJ"]
    assert mid >= low and mid >= high
