"""Validate the end-to-end chain integrator."""
from chain_e2e import run


def test_fundamental_chain_runs():
    lines, e_out, lam = run("none", "none")
    assert lam == 1064
    assert e_out > 950
    assert any("amplifier" in s for s, _ in lines)


def test_green_harmonic_reduces_energy_and_shifts_wavelength():
    _, e_fund, _ = run("none", "none")
    _, e_green, lam = run("green", "none")
    assert lam == 532
    assert e_green < e_fund


def test_uv_harmonic():
    _, e_uv, lam = run("uv", "none")
    assert lam == 355
    assert e_uv > 0


def test_application_appends_stage():
    base, _, _ = run("none", "none")
    with_app, _, _ = run("none", "ranging")
    assert len(with_app) > len(base)
