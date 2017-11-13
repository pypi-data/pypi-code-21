
# todo  update docs, defaults are aquired at definition time. Show trick for doing late bound attributes

# todo  add support for Void elements (self closing tags both with and without />
# todo  add a module for css parsing
# todo  Simplify structure so user doesn't need to import 3 different objects

import collections

class TreeNode:
    """tree_node is an object used to construct object-trees for generation of structed text like html/xhtml/svg code"""

    defaults = {}  # Contains default values used for tag properties

    def __new__(typ, name, *args, **kwargs):
        obj = object.__new__(typ)
        obj.name = name
        obj.args = args
        # The kwargs are initiated using defaults for the tag if they exist
        obj.kwargs = dict(TreeNode.defaults[name].copy(), **kwargs) if name in TreeNode.defaults else kwargs
        # todo should this be stored in self.__dict__ instead of self.__dict__['kwargs'] ?
        return obj

    def __getattr__(self, item):
        if item in object.__getattribute__(self, 'kwargs').keys():
            return self.kwargs[item]
        else:
            return object.__getattribute__(self, item)

    # todo Is there anything to gain from defining setattr?

    def __setattr__(self, key, value):
        if key not in ('name', 'args', 'kwargs', 'value'):
            self.kwargs[key] = value
        else:
            object.__setattr__(self, key, value)

    def __str__(self):

        # Generate attribute definitions:
        properties = (' '+' '.join([f'{name}="{value}"' for name, value in self.kwargs.items()])) \
            if len(self.kwargs) > 0 else ''

        if isinstance(self.args, collections.Iterator):
            # This unwraps iterators so they aren't exausted if the structure is iterated more than once.
            self.args = list(self.args)

        # Generate content string
        content_string = ''.join([''.join(str(x) for x in line) if hasattr(line, '__iter__') else str(line) for line in self.args])

        # Return content with enclosing tag
        return f'<{self.name}{properties}>{content_string}</{self.name}>'


class TreeSeed:
    """Class to make it easy to generate arbitrary tags.
    If a tag is present as a subclass of TreeSub, then it's automatically switched."""
    def __getattr__(self, attr):
        sub_node = next((x for x in TreeSub.__subclasses__() if x.__name__ == attr), None)
        if sub_node:
            def wrapper(*arg, **kwargs):
                return sub_node(*arg, **kwargs)
        else:
            def wrapper(*arg, **kwargs):
                return TreeNode(attr, *arg, **kwargs)
        return wrapper

# todo, if the class name is passed on in the attribute access, then direct subclasses of TreeNode can be used instead
class TreeSub(TreeNode):
    """ TreeSub is a TreeNode subclass used to register user-defined tags """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, cls.__name__, *args, **kwargs)

    def __str__(self):
        return str(self.construct(*self.args, **self.kwargs))


"""html is an instantiated object of the TreeSeed class, 
used to provide easy generation of TreeNodes through attribute access 
Type annotation against HTMLTagList is added purely to be able to have autocompletion in editors that support this"""
from pyno.html_tags_autocomplete import HTMLTagList
html = TreeSeed()  # type: HTMLTagList