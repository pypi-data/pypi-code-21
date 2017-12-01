"""Unsorted utility classes and routines."""


def natural_repr(obj):
    """A string representation of a Python entity, matching the its appearance in code."""
    if isinstance(obj, list):
        return repr(list(map(natural_repr, obj)))
    if isinstance(obj, tuple):
        return repr(tuple(map(natural_repr, obj)))
    if isinstance(obj, dict):
        return repr(dict([map(natural_repr, kv) for kv in obj.items()]))
    return repr(obj)


def natural_object_repr(obj):
    """A string representation of an object, matching the its appearance in code."""
    return "{}({})".format(obj.__class__.__name__, ". ".join(
        ["{}={}".format(member, natural_repr(getattr(obj, member))) for member in dir(obj)
         if member[0] != '_' and not callable(getattr(obj, member))]))


class NaturalReprMixin(object):
    """Mixin class that provides a __repr__ implementation calling natural_object_repr."""

    def __repr__(self):
        return natural_object_repr(self)


def str_split(cmd):
    """Split a string by whitespace, unless it is already a list."""
    if isinstance(cmd, str):
        return cmd.split()
    return cmd
