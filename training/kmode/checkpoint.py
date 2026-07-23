"""Checkpoint helpers for K-mode models."""

import os


def save_checkpoint(model, path):
    import torch
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    torch.save(model.state_dict(), path)


def load_checkpoint(model, path):
    import torch
    state = torch.load(path, map_location='cpu')
    model.load_state_dict(state)
    return model
