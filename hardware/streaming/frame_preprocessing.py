"""Beam frame preprocessing utilities for real-time inference."""

import numpy as np


def normalize_frame(frame):
    """Normalize camera intensity frame to float range [0, 1]."""
    frame = np.asarray(frame, dtype=np.float32)
    maximum = np.max(frame) if frame.size else 1.0
    if maximum == 0:
        return frame
    return frame / maximum


def resize_placeholder(frame, target_shape=None):
    """Placeholder hook for production image resizing."""
    return frame if target_shape is None else frame
