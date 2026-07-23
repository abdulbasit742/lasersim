"""Training utilities for K-mode beam classifiers."""

from __future__ import annotations


def train_epoch(model, loader, optimizer, loss_function):
    """Run one training epoch and return average loss."""
    model.train()
    total = 0.0
    count = 0

    for features, labels in loader:
        optimizer.zero_grad()
        output = model(features)
        loss = loss_function(output, labels)
        loss.backward()
        optimizer.step()
        total += float(loss.item())
        count += 1

    return total / max(count, 1)


def evaluate(model, loader):
    """Calculate classification accuracy."""
    model.eval()
    correct = 0
    total = 0

    for features, labels in loader:
        prediction = model(features).argmax(dim=1)
        correct += int((prediction == labels).sum())
        total += len(labels)

    return correct / max(total, 1)
