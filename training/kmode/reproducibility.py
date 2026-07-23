"""Utilities for reproducible K-mode training runs."""

import random

try:
    import numpy as np
except ImportError:
    np = None


def set_seed(seed=42):
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)


def get_run_metadata(config):
    return {
        "seed": config.get("seed", 42),
        "config": config,
    }
