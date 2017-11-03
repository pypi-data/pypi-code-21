from . user import User
from . chat import Chat
from . update import Update
from . message import Message


class EventHandler:
    def __init__(self,
                 bot,
                 error_handler,
                 user_follow_handler,
                 user_unfollow_handler,
                 message_new_handler,
                 message_update_handler,
                 chat_new_handler):

        self.bot = bot

        self.error = error_handler
        self.user_follow = user_follow_handler
        self.user_unfollow = user_unfollow_handler
        self.message_new = message_new_handler
        self.message_update = message_update_handler
        self.chat_new = chat_new_handler

    def add(self, event, handler):
        setattr(self, event, handler)

    @staticmethod
    def event_user_follow(request):
        user = User(id=request['id'], name=request['name'], gender=request['gender'])

        return Update(user)

    @staticmethod
    def event_user_unfollow(request):
        user = User(id=request['id'])

        return Update(user)

    def event_message_new(self, request):
        chat = Chat(id=request['chat_id'])
        user = User(id=request['sender_id'])
        message = Message(bot=self.bot, id=request['id'], type=request['type'], chat=chat,
                          status=request['status'], content=request['content'].strip())

        return Update(user, message, chat)

    def event_message_update(self, request):
        chat = Chat(id=request['chat_id'])
        user = User(id=request['sender_id'])
        message = Message(bot=self.bot, id=request['id'], type=request['type'], chat=chat,
                          status=request['status'], content=request['content'].strip())

        return Update(user, message)

    @staticmethod
    def event_chat_new(request):
        user = User(id=request['user']['id'], name=request['user']['name'], gender=request['user']['gender'])
        chat = Chat(id=request['id'])

        return Update(user, chat)
