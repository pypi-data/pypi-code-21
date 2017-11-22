from xiaoe.type import MessageCreateData


class Message(object):
    @classmethod
    def create(cls, data: MessageCreateData, poster):
        path = '/message.send/'
        return poster.post(path, data.data)
