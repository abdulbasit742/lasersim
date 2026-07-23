"""Hardware-in-the-loop controller foundation."""


class HardwareController:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        return self.connected

    def send_command(self, command):
        if not self.connected:
            raise RuntimeError("Hardware not connected")
        return {"command": command, "status": "queued"}
