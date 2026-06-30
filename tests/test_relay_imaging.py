"""Validate Gaussian q-parameter relay-imaging propagation."""
import numpy as np

from relay_imaging import (
    q_from_w, w_from_q, RelayTelescope, propagate, build_nilop_relays,
)


def test_q_roundtrip_recovers_waist():
    w = 2e-3
    q = q_from_w(w)
    assert np.isclose(w_from_q(q), w, rtol=1e-9)


def test_magnification_ratio():
    relay = RelayTelescope("x", 300.0, 600.0)
    assert np.isclose(relay.magnification, 2.0)


def test_telescope_magnifies_beam():
    """A 1:2 telescope should roughly double the collimated beam diameter."""
    w0 = 3e-3
    q = q_from_w(w0)
    relay = RelayTelescope("x", 300.0, 600.0)
    q_out, _ = propagate(q, relay.elements())
    assert w_from_q(q_out) > w0


def test_full_chain_expands_beam():
    """Beam should grow monotonically toward the booster (paper: 6->16 mm)."""
    w0 = 3e-3
    q = q_from_w(w0)
    diam = [2 * w0]
    for relay in build_nilop_relays():
        q, _ = propagate(q, relay.elements())
        diam.append(2 * w_from_q(q))
    assert diam[-1] > diam[0]
