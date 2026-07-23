"""Entry point for K-mode training."""

from .generate_dataset import generate_dataset


def run_training():
    X, y = generate_dataset(1000)
    print(f"Dataset ready: {X.shape}, labels: {y.shape}")


if __name__ == "__main__":
    run_training()
