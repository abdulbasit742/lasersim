"""Evaluation utilities for K-mode classification."""


def accuracy(predictions, labels):
    correct = 0
    total = len(labels)
    for p, y in zip(predictions, labels):
        correct += int(p == y)
    return correct / total if total else 0.0
