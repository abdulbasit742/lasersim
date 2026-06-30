"""Validate the laser-ranging link budget."""
import numpy as np

from ranging import RangingLink


def test_returns_drop_with_range():
    link = RangingLink()
    assert link.photons_returned(1000e3) > link.photons_returned(10000e3)


def test_more_energy_more_returns():
    lo = RangingLink(energy_J=0.1)
    hi = RangingLink(energy_J=1.28)
    assert hi.photons_returned(1000e3) > lo.photons_returned(1000e3)


def test_tighter_divergence_more_returns():
    wide = RangingLink(div_urad=50)
    tight = RangingLink(div_urad=5)
    assert tight.photons_returned(1000e3) > wide.photons_returned(1000e3)


def test_precision_improves_with_returns():
    link = RangingLink()
    near = link.range_precision_m(500e3)
    far = link.range_precision_m(5000e3)
    assert near < far    # more photons near -> finer precision


def test_photons_sent_positive():
    assert RangingLink().photons_sent() > 0
