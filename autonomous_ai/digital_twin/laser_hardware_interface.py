"""Laser hardware abstraction interface foundation."""

class LaserHardwareInterface:
    def __init__(self):
        self.connected = False
        self.device_state = {}

    def connect(self, device_id):
        self.connected = True
        self.device_state["device_id"] = device_id
        return self.connected

    def read_state(self):
        return self.device_state

    def send_command(self, command):
        if not self.connected:
            raise RuntimeError("Hardware not connected")
        return {"command": command, "status": "queued"}
