"""Beam visualization data renderer foundation."""

from typing import Dict, List


def normalize_intensity(values: List[float]) -> List[float]:
    if not values:
        return []
    maximum = max(values)
    if maximum == 0:
        return values
    return [value / maximum for value in values]


def create_heatmap_payload(intensity: List[float]) -> Dict:
    return {
        "type": "beam_heatmap",
        "values": normalize_intensity(intensity),
    }
