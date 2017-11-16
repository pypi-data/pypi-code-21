from slacker import Slacker
import os

class BrewerBot(Slacker):
    def __init__(self):
        self.token_file = os.path.expanduser("~") + "/slack.token"
        self.slacker = Slacker(self.get_token())
        self.channel = os.getenv('brewer_channel', '@luke')

    def get_token_from_file(self):
        with open(self.token_file, "r") as file:
            # FIXME: Boot up brewer_network if there's no token??
            return file.readlines()[0].rstrip()

    def get_token(self):
        return os.getenv('brewer_token', self.get_token_from_file())

    def send(self, message):
        # I don't want to mess around with 'super'. It's confusing and I don't have time.
        self.slacker.chat.post_message(self.channel, message, username = "Beer Bot")
        return True
