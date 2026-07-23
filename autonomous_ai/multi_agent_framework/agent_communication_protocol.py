"""Agent communication protocol foundation for LaserSim."""

class AgentCommunicationProtocol:
    def __init__(self):
        self.messages = []

    def send_message(self, sender, receiver, message):
        self.messages.append({"sender": sender, "receiver": receiver, "message": message})

    def history(self):
        return self.messages
