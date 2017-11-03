from . chat import Chat


class Message:

    def __init__(self, id, chat, content, type, status=0, bot=None):
        self.id = id
        self.bot = bot
        self.chat = chat
        self.type = type
        self.status = status
        self.content = content

    def reply_typing(self):
        self.bot.typing_start(self.chat.id)

    def reply_typing_stop(self):
        self.bot.typing_stop(self.chat.id)

    def reply_text(self, content):
        self.bot.send_message(self.chat.id, content, 'text/plain')

    @staticmethod
    def from_dict(data):
        chat = Chat(id=data['chat_id'])
        message = Message(id=data['id'], chat=chat, type=data['type'], content=data['content'])

        return message
