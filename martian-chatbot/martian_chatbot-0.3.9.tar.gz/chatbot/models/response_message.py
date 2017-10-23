class ResponseMessage(object):

    __from_user__ = False
    __message_service__ = 'service'

    def __init__(self, sender, service, message, message_type, response_type):
        self.sender = sender
        self.service = service
        self.message = message
        self.message_type = message_type
        self.response_type = response_type