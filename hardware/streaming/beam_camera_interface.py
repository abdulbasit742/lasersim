"""Live beam camera acquisition interface foundation.

Provides a hardware abstraction layer for future camera integrations.
"""

class BeamCameraInterface:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.connected = False

    def connect(self):
        self.connected = True
        return self.connected

    def capture_frame(self):
        if not self.connected:
            raise RuntimeError("Camera is not connected")
        return None
