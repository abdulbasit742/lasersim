"""Intelligent conversation manager foundation."""


class IntelligentConversationManager:
    def __init__(self):
        self.conversations = []

    def store_conversation(self, conversation):
        self.conversations.append(conversation)

    def history(self):
        return list(self.conversations)
