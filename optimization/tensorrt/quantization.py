"""Model quantization helpers for low latency inference."""


def quantize_model(model, precision="fp16"):
    """Prepare model for reduced precision inference."""
    return {
        "model": model,
        "precision": precision,
        "status": "quantization_ready"
    }
