"""Simple hyperparameter search utilities for K-mode training."""

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    learning_rate: float
    batch_size: int
    epochs: int


def generate_configs():
    """Generate candidate training configurations."""
    rates = [0.001, 0.0005]
    batches = [16, 32]
    epochs = [20, 50]

    return [
        TrainingConfig(lr, batch, epoch)
        for lr in rates
        for batch in batches
        for epoch in epochs
    ]
