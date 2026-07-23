"""Beam prediction service foundation for LaserSim."""

class BeamPredictionService:
    def __init__(self, model=None):
        self.model = model

    def predict(self, beam_input):
        if self.model is None:
            return {"status": "model_not_loaded"}
        return self.model.predict(beam_input)
