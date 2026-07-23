"""Learning rate scheduler helpers."""


def step_decay(initial_lr, epoch, drop=0.5, interval=20):
    """Return decayed learning rate."""
    factor = epoch // interval
    return initial_lr * (drop ** factor)
