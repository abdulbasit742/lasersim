"""Remote control API foundation for LaserSim autonomous systems."""

class RemoteControlAPI:
    def __init__(self):
        self.connected_clients = []

    def register_client(self, client):
        self.connected_clients.append(client)

    def dispatch_command(self, command):
        return {"command": command, "status": "queued"}
