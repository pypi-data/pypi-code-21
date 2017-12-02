""" Authority element """


class Authority(object):
    """ An Authority """

    def __init__(self, wan, pridisk, admin, lan):
        self._wan = wan
        self._pridisk = pridisk
        self._admin = admin
        self._lan = lan

    def get_wan(self):
        return self._wan

    def get_pridisk(self):
        return self._pridisk

    def get_admin(self):
        return self._admin

    def get_lan(self):
        return self._lan


def create_authority_from_json(json_entry):
    # json_entry = json.loads(json_entry_as_string)
    return Authority(json_entry['wan'], json_entry['pridisk'],
                     json_entry['admin'], json_entry['lan'])
