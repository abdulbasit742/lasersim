"""API smoke tests."""

from api.predict import predict_beam


def test_prediction_interface():
    result = predict_beam([0.1, 0.2])
    assert "mode" in result
