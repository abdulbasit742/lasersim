"""WebSocket server foundation for live LaserSim beam streaming."""

import asyncio
import json


class BeamWebSocketServer:
    def __init__(self):
        self.clients = set()

    async def register(self, client):
        self.clients.add(client)

    async def unregister(self, client):
        self.clients.discard(client)

    async def broadcast_prediction(self, prediction):
        message = json.dumps(prediction)
        for client in list(self.clients):
            await client.send(message)


async def start_server():
    return "WebSocket beam stream ready"
