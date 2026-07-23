"""Model artifact storage abstraction for LaserSim."""

class ModelArtifactStore:
    def __init__(self):
        self.artifacts = {}

    def save(self, version: str, artifact_path: str):
        self.artifacts[version] = artifact_path

    def get(self, version: str):
        return self.artifacts.get(version)
