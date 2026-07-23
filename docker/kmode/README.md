# LaserSim K-mode Docker Environment

This container provides a reproducible environment for beam profile ML experiments.

## Build

```bash
docker compose -f docker/kmode/docker-compose.yml build
```

## Run

```bash
docker compose -f docker/kmode/docker-compose.yml up
```

Future extensions:
- CUDA GPU image
- distributed training
- experiment service deployment
