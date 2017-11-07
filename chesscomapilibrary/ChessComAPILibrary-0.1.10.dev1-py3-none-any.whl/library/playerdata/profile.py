from pubapi_library.settings import PUBLIC_API, REQUEST_HEADERS


class Player:
    """TODO: docstring"""
    def __init__(self, username):
        self.player = PUBLIC_API.player(username)

    def player_details(self):
        return self.player.get(headers=REQUEST_HEADERS)

    def location(self):
        return self.player_details().location

    def id(self):
        return self.player_details()['@id']

    def username(self):
        return self.player_details().username

    def player_id(self):
        return self.player_details().player_id

    def name(self):
        return self.player_details().name

    def avatar(self):
        return self.player_details().avatar

    def country(self):
        return self.player_details().country

    def joined(self):
        return self.player_details().joined

    def last_online(self):
        return self.player_details().last_online

    def followers(self):
        return self.player_details().followers

    def status(self):
        return self.player_details().status
