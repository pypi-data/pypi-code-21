class Data:

    value = None

    def __init__(self, value, type, default=None):
        if not default == None:
            self.value = default
            self.type = 

    def set_value(self, value):
        self.value = value


class Model:

    def get_fields(self):
        for field in dir(self):
            if type(getattr(self, field)) == Data:
                print("Found one")


if __name__ == "__main__":

    class SSHAuth(Model):

        ip = Data()
        username = Data()
        password = Data()
        time = Data()

    test = SSHAuth()
    test.get_fields()