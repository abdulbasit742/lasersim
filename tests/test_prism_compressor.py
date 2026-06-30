"""Validate the prism-pair compressor."""
import numpy as np

from prism_compressor import PrismCompressor


def test_separation_gives_negative_gdd():
    pc = PrismCompressor()
    assert pc.separation_gdd_fs2(50) < 0


def test_more_separation_more_negative():
    pc = PrismCompressor()
    assert pc.separation_gdd_fs2(100) < pc.separation_gdd_fs2(20)


def test_insertion_gdd_positive():
    assert PrismCompressor().insertion_gdd_fs2() > 0


def test_null_separation_cancels_residual():
    pc = PrismCompressor()
    res = 5000.0
    sep = pc.separation_to_null(res)
    total = pc.net_gdd_fs2(sep) + res
    assert np.isclose(total, 0.0, atol=1.0)


def test_net_gdd_crosses_zero():
    pc = PrismCompressor()
    assert pc.net_gdd_fs2(1) > 0      # short sep: insertion dominates (+)
    assert pc.net_gdd_fs2(150) < 0    # long sep: separation dominates (-)
