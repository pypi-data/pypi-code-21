"""
Following controls.

"""
from enum import Enum, unique


@unique
class FollowMode(Enum):
    """
    Hypertext traversal mode.

     -  Follow all links (ALL)
     -  Follow child links (CHILD)
     -  Follow pagination only (PAGE)
     -  Follow no links (NONE)

    """
    ALL = u"ALL"
    CHILD = u"CHILD"
    PAGE = u"PAGE"
    NONE = u"NONE"
