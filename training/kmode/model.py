"""Neural network models for laser beam K-mode classification."""

from __future__ import annotations

try:
    import torch
    from torch import nn
except ImportError:  # keep physics package usable without ML extras
    torch = None
    nn = None


if nn is not None:
    class KModeClassifier(nn.Module):
        """Small configurable classifier for beam mode features."""

        def __init__(self, input_features: int = 4, classes: int = 10):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_features, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, classes),
            )

        def forward(self, x):
            return self.network(x)
else:
    class KModeClassifier:
        def __init__(self, *args, **kwargs):
            raise ImportError("Install torch to use KModeClassifier")
