'''
Provides a simple pretty-printed prose description of JSON-like data
(made up of simple types, lists, and dictionaries).
'''

indentAmount = 2


def describe(thing, indent = 0):
    spaces = ' ' * indent
    
    if isinstance(thing, (bool, int, float, complex, str)):
        return '*'
    elif isinstance(thing, list):
        if len(thing) is 0:
            return 'empty list'
        else:
            elts = describe(thing[0], __incr_ind(indent))
            if elts.count("\n") == 0:
                return 'list of ' + elts.strip()
            else:
                return 'list of:\n' + elts
    elif isinstance(thing, dict):
        keys = [ k for k in thing.keys() if k ]
        keys.sort(key=lambda x: x.lower())
        desc = spaces + 'dictionary with {\n'
        key_spaces = ' ' * __incr_ind(indent)
        for k in keys:
            leader = key_spaces + k + " : "
            desc += leader + describe(thing[k], len(leader)).strip() + "\n"
        desc += spaces + "}"
    
        return desc
    
    return "?"


def __incr_ind(amt):
    return amt + indentAmount


if __name__ == "__main__":
    print(describe({ 'name' : 'blah', 'age' : 4, 'city' : 'Rome'}))
    print(describe({ 'name' : 'blah', 'age' : 4, 'cities' : ['Rome', 'Madrid', 'Tokyo']}))
    print(describe({ 'name' : { 'first' : "john", 'last' : 'doe'}, 'age' : 4, 'cities' : ['Rome', 'Madrid', 'Tokyo']}))
    
