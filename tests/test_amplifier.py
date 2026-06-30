"""Validate the Frantz-Nodvik amplifier chain against the NILOP paper."""
import numpy as np
import pytest

from amplifier import (
    SuperGaussianBeam, GainModule, frantz_nodvik, b_integral,
    build_nilop_amplifier, PAPER_MEASURED,
)


def test_frantz_nodvik_small_signal_limit():
    # For tiny input fluence, F_out ~ G0 * F_in (linear gain regime).
    f_sat, g0, f_in = 0.3, 5.0, 1e-4
    f_out = frantz_nodvik(f_in, g0, f_sat)
    assert f_out == pytest.approx(g0 * f_in, rel=1e-2)


def test_frantz_nodvik_monotonic():
    f_sat, g0 = 0.3, 4.0
    fs = np.linspace(1e-3, 1.0, 50)
    out = [frantz_nodvik(f, g0, f_sat) for f in fs]
    assert all(b >= a for a, b in zip(out, out[1:]))


def test_supergaussian_peak_fluence_gaussian():
    # n=2 Gaussian: F0 = 2*E/(pi w^2) = 2 * avg_fluence
    beam = SuperGaussianBeam(energy_J=1.0, radius_cm=0.5, order_n=2)
    assert beam.peak_fluence == pytest.approx(2.0 * beam.avg_fluence, rel=1e-6)


def test_circular_polarization_reduces_B():
    b_lin = b_integral(1e9, 13.0, circular=False)
    b_circ = b_integral(1e9, 13.0, circular=True)
    assert b_circ == pytest.approx(b_lin * 2.0 / 3.0, rel=1e-6)


def test_full_chain_reaches_joule_level():
    """Modeled final output should land near the paper's 1280 mJ (+/- 25%)."""
    results = build_nilop_amplifier().run()
    final = results[-1].e_out_mJ
    assert 950.0 <= final <= 1600.0


def test_b_integrals_within_safe_limit():
    """No stage should exceed the ~3 rad self-focusing safety limit."""
    results = build_nilop_amplifier().run()
    assert max(r.b_integral for r in results) < 3.0


def test_stage_gains_positive():
    results = build_nilop_amplifier().run()
    amps = [r for r in results if "AMP" in r.name]
    assert all(r.gain > 1.0 for r in amps)
