"""Distributed training foundation for K-mode models."""


def get_distributed_config(world_size=1):
    return {
        "world_size": world_size,
        "backend": "nccl" if world_size > 1 else "single_gpu"
    }


def initialize_worker(rank, world_size):
    return {"rank": rank, "world_size": world_size}
