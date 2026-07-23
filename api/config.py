"""Runtime configuration for LaserSim API services."""

import os

MODEL_PATH = os.getenv("LASERSIM_MODEL_PATH", "models/kmode/latest.pt")
API_KEY = os.getenv("LASERSIM_API_KEY", "")
ENVIRONMENT = os.getenv("LASERSIM_ENV", "development")
