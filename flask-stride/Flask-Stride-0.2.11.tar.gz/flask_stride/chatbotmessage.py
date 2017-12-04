from .module import Module

class ChatBotMessage(Module):
    type = 'chat:bot:messages'

    def __init__(self, key, pattern, path):
        super().__init__(key)
        self.add_property('pattern', pattern)
        self.add_property('url', path)
