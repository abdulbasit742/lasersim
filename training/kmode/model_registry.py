"""Simple model registry for K-mode experiments."""

import json
from pathlib import Path


class ModelRegistry:
    def __init__(self, path="training/kmode/models.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def register(self, name, version, metrics, checkpoint):
        data = json.loads(self.path.read_text())
        data.append({
            "name": name,
            "version": version,
            "metrics": metrics,
            "checkpoint": checkpoint,
        })
        self.path.write_text(json.dumps(data, indent=2))

    def list_models(self):
        return json.loads(self.path.read_text())
