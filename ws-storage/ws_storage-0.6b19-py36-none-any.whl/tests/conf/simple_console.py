
from ws_storage.tests.conf.simple import Conf as Conf1

class Conf(Conf1):
    @classmethod
    def prepare(cls, mode, conf_dir, impl, port=None):
        Conf1.prepare(mode, conf_dir, impl, port)

        cls.log_console()



