"""Validate adaptive-optics correction."""
from wavefront import Wavefront
from adaptive_optics import DeformableMirror, correctable_modes


ABERRATED = Wavefront({"defocus": 0.12, "astig": 0.08, "coma": 0.05,
                       "spherical": 0.04, "trefoil": 0.03})


def test_correction_improves_strehl():
    dm = DeformableMirror(n_actuators=37)
    residual = dm.correct(ABERRATED)
    assert residual.strehl() > ABERRATED.strehl()


def test_more_actuators_better_correction():
    few = DeformableMirror(n_actuators=4).correct(ABERRATED)
    many = DeformableMirror(n_actuators=97).correct(ABERRATED)
    assert many.strehl() >= few.strehl()


def test_correctable_modes_grows_with_actuators():
    assert correctable_modes(64) >= correctable_modes(4)


def test_residual_not_larger_than_input():
    dm = DeformableMirror(n_actuators=37)
    residual = dm.correct(ABERRATED)
    assert residual.rms_error() <= ABERRATED.rms_error() + 1e-9
