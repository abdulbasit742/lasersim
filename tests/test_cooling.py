"""Validate the convective cooling model."""
from cooling import CoolingChannel


def test_more_flow_more_cooling():
    ch = CoolingChannel()
    assert ch.film_coeff(15) > ch.film_coeff(3)


def test_more_flow_lowers_wall_rise():
    ch = CoolingChannel()
    assert ch.wall_rise(15, 200) < ch.wall_rise(3, 200)


def test_reynolds_increases_with_flow():
    ch = CoolingChannel()
    assert ch.reynolds(10) > ch.reynolds(2)


def test_higher_heat_higher_rise():
    ch = CoolingChannel()
    assert ch.wall_rise(8, 400) > ch.wall_rise(8, 100)


def test_min_flow_meets_budget():
    ch = CoolingChannel()
    f = ch.min_flow_for_budget(200, 20.0)
    assert ch.wall_rise(f, 200) <= 20.0 + 1e-6
