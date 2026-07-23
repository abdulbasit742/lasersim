"""Simple simulated camera measurement effects for beam profiles."""

import numpy as np


def apply_camera_noise(image, level=0.01):
    noise = np.random.normal(0, level, image.shape)
    return np.clip(image + noise, 0, 1)


def simulate_measurement(image):
    return apply_camera_noise(image)
