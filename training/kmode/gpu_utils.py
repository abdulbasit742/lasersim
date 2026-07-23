"""GPU acceleration utilities for K-mode beam training."""

import torch


def get_device(prefer_gpu=True):
    if prefer_gpu and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def move_to_device(model, tensors, device=None):
    device = device or get_device()
    model = model.to(device)
    tensors = [t.to(device) for t in tensors]
    return model, tensors
