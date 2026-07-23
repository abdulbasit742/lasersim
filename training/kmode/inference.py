"""Inference utilities for trained K-mode beam classifiers."""

import torch


def predict_mode(model, sample):
    model.eval()
    with torch.no_grad():
        output = model(sample)
        prediction = torch.argmax(output, dim=1)
    return prediction
