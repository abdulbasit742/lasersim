"""Utilities for comparing K-mode experiments."""


def compare_results(results):
    """Return best experiment by validation accuracy."""
    if not results:
        return None
    return max(results, key=lambda item: item.get("accuracy", 0))
