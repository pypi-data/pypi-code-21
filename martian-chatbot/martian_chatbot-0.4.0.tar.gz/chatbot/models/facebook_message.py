from chatbot.models.user_input_message import UserInputMessage

class FacebookMessage(UserInputMessage):

    def message_service(self):
        return 'facebook'
