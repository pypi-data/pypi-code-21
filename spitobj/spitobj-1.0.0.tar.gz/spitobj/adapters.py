from .spitobj import Spitobj


class SpitobjFactoryBoy:
    """Primitive FactoryBoy-like interface"""

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls().new(*args, **kwargs)
        return obj

    @classmethod
    def create_batch(cls, times, *args, **kwargs):
        spitobj = cls()
        objs = []
        for i in range(times):
            obj = spitobj.new(*args, **kwargs)
            objs.append(obj)
        return objs


class SpitobjSqlalchemy(Spitobj):
    sqlalchemy_session = None
    commit = True

    def __init__(self, *args, **kwargs):
        assert self.sqlalchemy_session != None, "Set sqlalchemy_session for {}".format(type(self))
        super().__init__(*args, **kwargs)

    def new(self, *args, **kwargs):
        obj = super().new(*args, **kwargs)
        if self.commit:
            self.save(obj)
        return obj

    def save(self, obj):
        self.sqlalchemy_session.add(obj)
        self.sqlalchemy_session.commit()

    @classmethod
    def get(cls, *args, **kwargs):
        spitobj = cls()
        obj = spitobj.new(*args, **kwargs)
        return obj

    @classmethod
    def get_saved(cls, *args, **kwargs):
        spitobj = cls()
        obj = spitobj.new(*args, **kwargs)
        spitobj.save(obj)
        return obj
