"""Compare inference backends."""


def compare_results(cpu, gpu, tensorrt):
    return {
        "cpu": cpu,
        "gpu": gpu,
        "tensorrt": tensorrt,
    }
