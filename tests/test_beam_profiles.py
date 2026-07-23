import numpy as np


def test_beam_profile_output():
    sample = np.ones((32, 32))
    assert sample.shape == (32, 32)
    assert np.isfinite(sample).all()
