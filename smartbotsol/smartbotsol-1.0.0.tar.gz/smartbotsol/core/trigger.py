

class BaseTrigger(object):
    
    def __init__(self):
        self.user = None
        self.bot = None
        self.update = None

    def __str__(self):
        return str([self.user, self.bot, self.update])

    def get_chat_id(self):
        pass

    def get_txt(self):
        pass

    def get_name(self):
        pass

    chat_id = property(get_chat_id)
    txt = property(get_txt)
    name = property(get_name)

