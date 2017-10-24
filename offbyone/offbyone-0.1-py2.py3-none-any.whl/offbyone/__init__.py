import random
import sys
import builtins

def offbyone(item):
    '''
    `offbyone` will try to change an input value in some way or another.

    * If it's a boolean, the value gets flipped. True becomes False and vice versa.
    * If it's an int or a float, either -1 or +1 gets added to the value.
    * If it's a string, a random character is chosen and either -1 or +1 gets added to its ord() value.
    * If it's a list, `offbyone` gets called on every element.
    * If it's a tuple, `offbyone` gets called on every element. since it's immutable, we need to do some casting
    back and forth to make it work.
    * If it's a dict, `offbyone` gets called on every value.
    * If the input value is an instance of something else, nothing is done.
    '''
    coin = random.choice([-1, 1]) # choose a random value for changing other values
    if isinstance(item, bool):
        return not item # flip the boolean to the opposite
    if isinstance(item, (int, float)):
        return item + coin # add the coin value to the existing value
    if isinstance(item, str):
        c = random.randint(0, len(item)-1) # choose a random index for the string
        return "".join([chr(ord(l)+coin) if i == c else l for i, l in enumerate(item)]) # iterate over the string
                                                                                        # and alter the one chosen
                                                                                        # character at index `c`
                                                                                        # then rebuild the string again
    if isinstance(item, list):
        return list(map(offbyone, item)) # for every value in the list, call this function
    if isinstance(item, tuple):
        return tuple(offbyone(list(item))) # cast tuple to list, and call this function on it, then cast to tuple again
    if isinstance(item, dict):
        for x in item.keys():           # iterate over the keys in the dict
            item[x] = offbyone(item[x]) # and call this function on each value
        return item
    else:
        return item                     # if nothing has been caught, just return the original item

def print_decorator(func):
    '''
    `print_decorator` is a function meant to wrap the builtin print function.

    * `offbyone` gets called on the input argument before the "real" print function is called.
    '''
    def wrapped_print(*args, **kwargs):
        return func(offbyone(*args), **kwargs) # call offbyone before printing
    return wrapped_print

def displayhook(value):
    '''
    `displayhook` is a function meant to replace sys.displayhook.

    * `offbyone` gets called on the input value before it goes through the rest of the function.
    '''
    if value is None:
        return
    # Set '_' to None to avoid recursion
    builtins._ = None
    text = repr(offbyone(value)) # the original call here is repr(value), but we'll add an `offbyone` call on `value`
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        bytes = text.encode(sys.stdout.encoding, 'backslashreplace')
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(bytes)
        else:
            text = bytes.decode(sys.stdout.encoding, 'strict')
            sys.stdout.write(text)
    sys.stdout.write("\n")
    builtins._ = value

builtins.print = print_decorator(print) # hijack the print function
sys.displayhook = displayhook           # hijack the displayhook
