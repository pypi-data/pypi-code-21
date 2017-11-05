import time

class OptionalArgument():
    def __repr__(self):
        return "<optional argument>"

optionalArg = OptionalArgument()

class CharacterSetError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def count(string, character, start = optionalArg, end = optionalArg, ignoreCase = False):
    if start == optionalArg:
        start = 0
    if end == optionalArg:
        end = len(string)
    if ignoreCase:
        return string.lower().count(character.lower(), start, end)
    else:
        return string.count(character, start, end)

def is_ascii(string):
    return all(ord(x) < 128 for x in string)

def ascii_sum(string):
    if not is_ascii(string):
        raise CharacterSetError
    return sum([ord(x) for x in string])