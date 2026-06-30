"""Validate the literature-landscape benchmark."""
from landscape import published_systems, System


def test_this_work_is_highest_energy():
    systems = published_systems()
    this = next(s for s in systems if s.is_this_work)
    others = [s for s in systems if not s.is_this_work]
    assert this.energy_mJ > max(s.energy_mJ for s in others)


def test_peak_power_computation():
    s = System("x", energy_mJ=1280, duration_ps=200, rep_hz=10, ref="")
    # 1.28 J / 200 ps = 6.4 GW
    assert abs(s.peak_power_GW - 6.4) < 0.1


def test_avg_power_computation():
    s = System("x", energy_mJ=1000, duration_ps=100, rep_hz=10, ref="")
    assert abs(s.avg_power_W - 10.0) < 1e-6


def test_exactly_one_this_work():
    systems = published_systems()
    assert sum(s.is_this_work for s in systems) == 1
