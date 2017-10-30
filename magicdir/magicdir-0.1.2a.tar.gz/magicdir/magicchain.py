import keyword
from copy import copy


class MagicList(list):
    """ List-like class that collects attributes and applies functions """

    def __getattr__(self, item):
        return MagicList([getattr(x, item) for x in self])

    def __call__(self, *args, **kwargs):
        return MagicList([x(*args, **kwargs) for x in self])


class MagicChain(object):
    """ A tree-like class for chaining commands and attributes together """

    def __init__(self, parent=None, push_up=None):
        """
        Chainer constructor

        :param parent: parent node that called this object
        :type parent: MagicChain
        :param push_up: whether to push up attributes to the root node
        :type push_up: boolean
        """
        self._parent = parent
        self._children = {}
        self._grandchildren = {}
        self._push_up = False
        if push_up is not None:
            self._push_up = push_up
        self._alias = None

    @property
    def alias(self):
        return self._alias

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return MagicList(self._children.values())

    @property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root

    def is_root(self):
        return self is self.root

    def descendents(self, include_self=False):
        c = []
        if include_self:
            c = [self]
        if not self._children == {}:
            children = list(self._children.values())
            c += children
            for child in children:
                c += child.descendents()
        return MagicList(c)

    def ancestors(self, include_self=False):
        p = []
        if self.parent is not None:
            p += self.parent.ancestors(include_self=True)
        if include_self:
            p += [self]
        return MagicList(p)

    # def ancestor_attrs(self, attr, include_self=False):
    #     nodes = self.ancestors(include_self=include_self)
    #     return [getattr(n, attr) for n in nodes]
    #
    # def descendent_attrs(self, attr, include_self=False):
    #     nodes = self.descendents(include_self=include_self)
    #     return [getattr(n, attr) for n in nodes]

    def delete(self):
        if self.parent is not None:
            parent = self.parent
            rm = parent._remove_child(self.alias)
            rm._parent = None
            parent._update_grandchildren()
            rm._update_grandchildren()
            return rm

    # def connect(self, other, push_up=None):
    #     raise NotImplemented("Connect is not yet implemented.")
    #     # if push_up is None:
    #     #     push_up = self._push_up
    #     # other.remove()
    #     # self._add_child(other, push_up=push_up)

    def _sanitize_identifier(self, iden):
        if keyword.iskeyword(iden):
            raise AttributeError("\"{}\" is reserved and is not a valid identified.".format(iden))
        if not iden.isidentifier():
            raise AttributeError("\"{}\" is not a valid identifier.".format(iden))
        if hasattr(self, iden):
            raise AttributeError("identifier \"{}\" already exists".format(iden))

    def _create_child(self, alias, with_attributes=None, push_up=None):
        if push_up is None:
            push_up = self._push_up
        self._sanitize_identifier(alias)
        child = self._copy(alias, with_attributes)
        return self._add_child(child, push_up=push_up)

    def _add_child(self, child, push_up=None):
        if push_up is None:
            push_up = self._push_up
        if child.alias in self._children:
            raise AttributeError("Cannot add alias {}. Try using a unique alias.".format(child.alias))
        self._children[child.alias] = child
        if push_up:
            self._add_grandchild(child)
        return child

    def _remove_child(self, alias):
        if alias in self._children:
            return self._children.pop(alias)

    def _update_grandchildren(self):
        """ Updates accessible children """
        if self._push_up:
            self.root._grandchildren = {}
            d = self.root.descendents()
            for c in self.root.descendents():
                self._add_grandchild(c)

    def _add_grandchild(self, child):
        if child.alias not in self.root._children:
            if hasattr(self.root, child.alias):
                raise AttributeError("Cannot push alias {} to root. Try using a unique alias.".format(child.alias))
            self.root._grandchildren[child.alias] = child
        return child

    # def _remove_grandchild(self, alias):
    #     gc = self.root._grandchildren
    #     if alias in gc:
    #         return gc.pop(alias)

    def _copy(self, alias, with_attributes=None):
        c = copy(self)
        c._parent = self
        c._children = {}
        c._grandchildren = {}
        if with_attributes is None:
            with_attributes = {}
        for k, v in with_attributes.items():
            setattr(c, k, v)
        c._alias = alias
        return c

    def __getattr__(self, name):
        c = {}
        c.update(object.__getattribute__(self, "_children"))
        c.update(object.__getattribute__(self, "_grandchildren"))
        if name in c:
            return c[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        ckey = '_children'
        gckey = '_grandchildren'
        if ckey in self.__dict__ and gckey in self.__dict__:
            c = {}
            c.update(object.__getattribute__(self, "_children"))
            c.update(object.__getattribute__(self, "_grandchildren"))
            if name in c:
                raise AttributeError("Cannot set attribute \"{}\".".format(name))
        return object.__setattr__(self, name, value)