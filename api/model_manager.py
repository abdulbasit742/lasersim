"""Model loading abstraction for API inference."""

class ModelManager:
    def __init__(self):
        self.model = None

    def load(self, model_path: str):
        self.model = model_path
        return True

    def status(self):
        return {"loaded": self.model is not None}
