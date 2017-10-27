from .. import service

class Database:
    from ..model import Database as DBM
    from ..config import config as c

    @classmethod
    def create(cls):
        cls.DBM.create()

    @classmethod
    def clear(cls):
        cls.DBM.clear()

    @classmethod
    def remove():
        from dxpy.filesystem import File, rm
        rm(File(c['path']))

    @classmethod
    def exists():
        from dxpy.filesystem import File
        return File(c['path']).exists


def create(s):
    from ..config import config as c
    if c['use_web_api']:
        return service.create_web(s)
    else:
        return service.create_py(s)


def read(tid):
    from ..config import config as c
    if c['use_web_api']:
        return service.read_web(tid)
    else:
        return service.read_py(tid)


def read_all():
    from ..config import config as c
    if c['use_web_api']:
        return service.read_all_web()
    else:
        return service.read_all_py()


def update(s):
    from ..config import config as c
    if c['use_web_api']:
        return service.update_web(s)
    else:
        return service.update_py(s)


def delete(tid):
    from ..config import config as c
    if c['use_web_api']:
        return service.delete_web(tid)
    else:
        return service.delete_py(tid)
