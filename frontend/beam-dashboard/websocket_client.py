"""WebSocket client foundation for LaserSim dashboard."""

class BeamStreamClient:
    def __init__(self, url):
        self.url = url
        self.connected = False

    def connect(self):
        self.connected = True

    def receive_frame(self):
        return None
