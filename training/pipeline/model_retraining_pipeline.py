"""Continuous learning pipeline foundation."""


def prepare_retraining(dataset_path, model_version):
    return {
        "dataset": dataset_path,
        "base_model": model_version,
        "status": "ready",
    }
