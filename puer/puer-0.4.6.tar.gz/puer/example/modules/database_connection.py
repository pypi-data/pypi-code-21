from puer.module import AbstractModule


class DBConnection(AbstractModule):
    name = "database"

    def __init__(self, manager, app):
        self.value = "Huita"
        print("Hui")