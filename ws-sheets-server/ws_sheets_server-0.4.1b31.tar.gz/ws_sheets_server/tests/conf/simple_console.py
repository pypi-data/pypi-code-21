
from ws_sheets_server.tests.conf.simple import Conf as Conf1

class Conf(Conf1):
    @classmethod
    def prepare(cls, **kwargs):
        Conf1.prepare(**kwargs)

        cls.log_console()



