from .module import Module

class ChatBot(Module):
    type = 'chat:bot'

    def __init__(self, key, mention_path, direct_message_path):
        super().__init__(key)
        self.add_property('mention', {'url': mention_path})
        self.add_property('directMessage', {'url': direct_message_path})
