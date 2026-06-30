"""Validate the Pockels-cell pulse picker."""
import numpy as np

from pockels import PockelsCell


def test_half_wave_voltage_positive():
    assert PockelsCell().half_wave_voltage() > 0


def test_full_transmission_at_vpi():
    pc = PockelsCell()
    T = pc.transmission(pc.half_wave_voltage())
    assert T > 0.99


def test_blocked_at_zero_volts():
    pc = PockelsCell()
    assert pc.transmission(0.0) < 0.01


def test_extinction_ratio_large():
    assert PockelsCell().extinction_ratio() > 100


def test_higher_rep_more_leakage():
    pc = PockelsCell()
    assert pc.neighbour_leakage(200) >= pc.neighbour_leakage(50)
