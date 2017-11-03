class Service(object):
    """
    Attributes:
        id (str): unique id

        creation_time (str): creation time

        name (str): name of the service
    """
    def __init__(self, id, creation_time, name):
        self.id = id
        self.creation_time = creation_time
        self.name = name


class User(object):
    """
    Attributes:
        id (str): unique id

        creation_time (str): creation time

        username (str): name of the user
    """
    def __init__(self, id, creation_time, username):
        self.id = id
        self.creation_time = creation_time
        self.username = username
