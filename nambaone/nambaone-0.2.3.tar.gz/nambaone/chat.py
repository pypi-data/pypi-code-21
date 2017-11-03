class Chat:

    def __init__(self, id, name='', image=''):
        self.id = id
        self.name = name
        self.image = image

    @staticmethod
    def from_dict(data):
        chat = Chat(id=data['id'], name=data['name'], image=data['image'])

        return chat
