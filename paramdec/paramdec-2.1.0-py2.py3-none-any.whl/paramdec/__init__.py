"""
Paramdec
========

Paramdec is a convenient way to create parametrized decorators.

Docs and examples are in project repo: <https://github.com/Suenweek/paramdec>.
"""


from collections import namedtuple


Author = namedtuple("Author", ["name", "email"])


authors = [
    Author("Roman Novatorov", "suenweek@protonmail.com")
]


__version__ = "2.1.0"
__author__ = ", ".join("%s <%s>" % author for author in authors)


from .paramdec import paramdec


__all__ = ("paramdec",)
