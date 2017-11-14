from . import utils
from . import template

class Payload(object):
    def __init__(self, user_id, message, quick_replies=None, notification=False):
        self.event = "send"
        self.user = user_id
        if quick_replies:
            if not isinstance(quick_replies, template.QuickReply):
                quick_replies = template.QuickReply(quick_replies)
            if isinstance(message, template.BaseTemplate):
                message.quickReply = quick_replies
        if isinstance(message, template.TextContent):
            self.textContent = message
        elif isinstance(message, str):
            self.textContent = template.TextContent(message)
            if quick_replies:
                self.textContent.quickReply = quick_replies
        elif isinstance(message, template.ImageContent):
            self.imageContent = message
        elif isinstance(message, template.CompositeContent):
            self.compositeContent = message
        else:
            raise ValueError("message type must be str or textContent  or imageContent  or compositeContent type !")
        self.options = {"notification":notification}

    def to_json(self):
        return utils.to_json(self)

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.to_json()
        return utils.to_json(other) == self.to_json()

