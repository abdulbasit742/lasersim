"""Synthetic augmentation utilities for laser beam ML datasets."""

import numpy as np


def add_gaussian_noise(image, sigma=0.05):
    noise = np.random.normal(0, sigma, image.shape)
    return np.clip(image + noise, 0, 1)


def random_shift(image, max_pixels=3):
    dx = np.random.randint(-max_pixels, max_pixels + 1)
    dy = np.random.randint(-max_pixels, max_pixels + 1)
    return np.roll(np.roll(image, dx, axis=0), dy, axis=1)


def augment_beam(image):
    result = image.copy()
    if np.random.rand() > 0.5:
        result = add_gaussian_noise(result)
    if np.random.rand() > 0.5:
        result = random_shift(result)
    return result
