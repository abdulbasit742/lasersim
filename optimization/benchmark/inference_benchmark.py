"""Benchmark utilities for K-mode inference latency."""

import time


def benchmark(model, samples, runs=100):
    start = time.perf_counter()
    for _ in range(runs):
        for sample in samples:
            model(sample)
    elapsed = time.perf_counter() - start
    return {"runs": runs, "elapsed_seconds": elapsed, "avg_seconds": elapsed / runs}
