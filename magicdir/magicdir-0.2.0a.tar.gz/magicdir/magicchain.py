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

    def __init__(self, push_up=None):
        """
        Chainer constructor

        :param parent: parent node that called this object
        :type parent: MagicChain
        :param push_up: whether to push up attributes to the root node
        :type push_up: boolean
        """
        self._parent = None
        self._children = {}
        self._grandchildren = {}
        self._push_up = False
        if push_up is not None:
            self._push_up = push_up

    # TODO: add dynamic attr that looks at parent? It would be really slow...

    @property
    def attr(self):
        if self.parent:
            for k, v in self.parent._children.items():
                if v is self:
                    return k

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

    # def connect(self, other, push_up=None):
    #     raise NotImplemented("Connect is not yet implemented.")
    #     # if push_up is None:
    #     #     push_up = self._push_up
    #     # other.remove()
    #     # self._add_child(other, push_up=push_up)

    def remove_parent(self):
        if self.parent is not None:
            parent = self.parent
            rm = parent._remove_child(self.attr)
            rm._parent = None
            parent._update_grandchildren()
            rm._update_grandchildren()
            return rm

    def _sanitize_identifier(self, iden):
        if keyword.iskeyword(iden):
            raise AttributeError("\"{}\" is reserved and is not a valid identified.".format(iden))
        if not iden.isidentifier():
            raise AttributeError("\"{}\" is not a valid identifier.".format(iden))

    def _validate_attr(self, attr, push_up=None):
        if push_up is None:
            push_up = self._push_up
        if hasattr(self, attr):
            raise AttributeError("Attribute \"{}\" already exists".format(attr))
        if push_up:
            if hasattr(self.root, attr):
                raise AttributeError("Cannot push up attr \"{}\". Attribute already exists".format(attr))

    # def _add_as_child(self, child):
    #     # self._validate_child(child)
    #     self._children[child.attr] = child
    #     return child

    # def _validate_child(self, child):
    #     if child.attr in self._children:
    #         raise AttributeError("Cannot add attr {}. Try using a unique attr.".format(child.attr))

    # def _add_as_grandchild(self, child):
    #     # self._validate_grandchild(child)
    #     self.root._grandchildren[child.attr] = child
    #     return child

    # def _validate_grandchild(self, child):
    #     if child.attr in self.root._grandchildren:
    #         raise AttributeError("Cannot push attr {} to root. Try using a unique attr.".format(child.attr))

    def _add(self, attr, child, push_up=None, make_attr=True):
        if make_attr:
            self._sanitize_identifier(attr)
        if push_up is None:
            push_up = self._push_up
        self._validate_attr(attr, push_up)
        self._children[attr] = child
        if push_up:
            if attr not in self.root._children:
                self.root._grandchildren[attr] = child
        return child

    def _create_child(self, with_attributes=None):
        c = copy(self)
        c._parent = self
        c._children = {}
        c._grandchildren = {}
        if with_attributes is None:
            with_attributes = {}
        for k, v in with_attributes.items():
            setattr(c, k, v)
        return c

    def _create_and_add_child(self, attr, with_attributes=None, push_up=None, make_attr=True):
        if push_up is None:
            push_up = self._push_up
        child = self._create_child(with_attributes)
        return self._add(attr, child, push_up=push_up, make_attr=make_attr)

    def _remove_child(self, attr):
        if attr in self._children:
            return self._children.pop(attr)

    def _update_grandchildren(self):
        """ Updates accessible children """
        if self._push_up:
            self.root._grandchildren = {}
            for c in self.children:
                d = c.descendents(include_self=False)
                for gc in d:
                    self._add_grandchild(gc)

    def _attributes(self):
        return list(self._children.keys()) + list(self._grandchildren.keys())

    def _add_grandchild(self, child):
        self.root._grandchildren[child.attr] = child
        return child

    def get(self, attr):
        return getattr(self, attr)

    def has(self, attr):
        return hasattr(self, attr)

    # def _remove_grandchild(self, attr):
    #     gc = self.root._grandchildren
    #     if attr in gc:
    #         return gc.pop(attr)

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

    # # TODO: add __dir__
    def __dir__(self):
        print('dir called')
        return super().__dir__() + list(self._children.keys()) + list(self._grandchildren.keys())

