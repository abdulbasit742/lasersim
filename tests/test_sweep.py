"""Validate the batch sweep engine."""
import numpy as np

from sweep import (
    SweepSpec, grid, run_grid, best, vectorized_amplifier_sweep,
)


def test_grid_cartesian_product():
    specs = [SweepSpec("a", [1, 2]), SweepSpec("b", [10, 20, 30])]
    pts = grid(specs)
    assert len(pts) == 6
    assert {"a": 2, "b": 30} in pts


def test_run_grid_serial():
    pts = grid([SweepSpec("x", [1, 2, 3])])
    rows = run_grid(lambda p: {"y": p["x"] ** 2}, pts)
    assert [r["y"] for r in rows] == [1, 4, 9]


def test_best_with_constraint():
    rows = [{"v": 10, "B": 5}, {"v": 8, "B": 1}, {"v": 9, "B": 2}]
    top = best(rows, "v", maximize=True, constraint=lambda r: r["B"] < 3)
    assert top["v"] == 9


def test_vectorized_amplifier_shapes_and_gain():
    fs = np.linspace(0.05, 0.30, 10)
    br = np.linspace(0.4, 1.2, 8)
    E, B = vectorized_amplifier_sweep(fs, br)
    assert np.asarray(E).shape == (8, 10)
    assert np.all(np.asarray(E) > 0)
    # higher stored fluence -> more energy out (along the f_store axis)
    Earr = np.asarray(E)
    assert Earr[0, -1] >= Earr[0, 0]
