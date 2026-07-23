"""Experiment analytics foundation for LaserSim."""

from statistics import mean


def summarize_runs(runs):
    """Return basic statistics from experiment runs."""
    if not runs:
        return {"count": 0, "average_confidence": 0}

    return {
        "count": len(runs),
        "average_confidence": mean(r.get("confidence", 0) for r in runs),
    }
