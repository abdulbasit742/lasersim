"""Validate the damage-threshold auditor."""
import numpy as np

from damage import scaled_lidt, audit_chain, headroom, TAU_REF_PS


def test_lidt_scaling_law():
    base = scaled_lidt(1.0, TAU_REF_PS)
    longer = scaled_lidt(1.0, 4 * TAU_REF_PS)
    assert np.isclose(longer / base, 2.0, rtol=1e-6)


def test_lidt_at_reference_is_reference():
    assert np.isclose(scaled_lidt(1.0, TAU_REF_PS), 1.0)


def test_audit_returns_reports():
    reports = audit_chain()
    assert len(reports) > 0
    for r in reports:
        assert r.peak_fluence > 0
        assert r.lidt > 0


def test_headroom_positive():
    reports = audit_chain()
    assert headroom(reports) > 0


def test_higher_lidt_more_margin():
    low = headroom(audit_chain(lidt_ref=0.8))
    high = headroom(audit_chain(lidt_ref=2.0))
    assert high > low
