from collections import UserList, UserDict, UserString

from enum import Enum


class SirenBase:
    pass


class UserInt(int):
    pass


# TODO: get rid of this nonsense
def to_renderable(v):
    if not hasattr(v, 'render'):
        if type(v) == list:
            v = UserList(v)
        elif type(v) == dict:
            v = UserDict(v)
        elif type(v) == str:
            v = UserString(v)
        elif type(v) == int:
            v = UserInt(v)
        elif issubclass(v.__class__, Enum):
            v = UserString(v.value)
        v.__class__ = type('Renderable{}'.format(v.__class__.__name__), (v.__class__, RendererMixin), {})
    return v


class RendererMixin:
    def render_list(self):
        return [to_renderable(v).render() for v in self if v]

    def render_dict(self):
        return {k: to_renderable(v).render() for k, v in self.items() if v}

    def render_media_type(self):
        return self.get_type()

    def render_entity(self):
        return {k[1:]: to_renderable(v).render() for k, v in self.__dict__.items() if v}

    def render(self):
        if (issubclass(self.__class__, SirenBase)):
            return self.render_entity()
        elif isinstance(self, UserDict):
            return self.render_dict()
        elif isinstance(self, UserList):
            return self.render_list()
        elif hasattr(self, 'data'):
            return self.data

        return self

