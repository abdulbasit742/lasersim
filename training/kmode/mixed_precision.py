"""Mixed precision training helpers."""

import torch


def create_scaler(enabled=True):
    return torch.cuda.amp.GradScaler(enabled=enabled)


def autocast_context(enabled=True):
    return torch.cuda.amp.autocast(enabled=enabled)
