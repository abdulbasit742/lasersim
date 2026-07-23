"""Visualization helpers for simulated laser beam profiles."""

import matplotlib.pyplot as plt


def show_intensity(image, title="Beam intensity"):
    plt.figure(figsize=(5, 5))
    plt.imshow(image, cmap="inferno")
    plt.title(title)
    plt.colorbar(label="Intensity")
    plt.tight_layout()
    return plt.gcf()
