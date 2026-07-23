"""API route definitions placeholder."""

from .beam_service import BeamPredictionService

service = BeamPredictionService()


def predict_beam(data):
    return service.predict(data)
