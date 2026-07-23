"""Example script for beam mode prediction."""

from inference import predict_mode


def predict_beam(model, tensor):
    return predict_mode(model, tensor)
