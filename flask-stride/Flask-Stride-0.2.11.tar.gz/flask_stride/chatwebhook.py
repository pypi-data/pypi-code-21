from .module import Module

class ChatWebhook(Module):
    type = 'chat:webhook'
    valid_event = [ 'conversation:updates', 'roster:updates' ]

    def __init__(self, key, event, url):
        if event not in self.valid_event:
            raise ValueError('Invalid Event')

        super().__init__(key)
        self.add_property('event', event)
        self.add_property('url', url)
