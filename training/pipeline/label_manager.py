"""Automated dataset labeling foundation."""


def create_label(sample, predicted_mode):
    return {
        "sample": sample,
        "label": predicted_mode,
    }
