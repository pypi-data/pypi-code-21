import os

from boom.api import API
from boom.models import Message


class ConversationService(API):

    def __init__(self):
        self.url = os.getenv("BOOM_CONVERSATION_URL", "https://conversation.boomletsgo.com")

    def receive(self, message):
        response = ConversationResponse()
        api_response = self.post("message", message)[0]
        response.message = Message(**api_response["message"])

        for item in api_response["context"]:
            response.context.append(Message(**item))

        for item in api_response["responses"]:
            response.responses.append(Message(**item))

        return response


class ConversationResponse(object):

    def __init__(self):
        self.message = None
        self.context = []
        self.responses = []
