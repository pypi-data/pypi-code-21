
# Functions over lists:
def take(n, container):
    return container[:n]


def drop(n, container):
    return container[n:]


def _advanceWhile(f, container):
    n = 0
    lim = len(container)
    while n < lim and f(container[n]) == True:
        n += 1
    return n


def takeWhile(f, container):
    n = _advanceWhile(f, container)
    return container[:n]


def dropWhile(f, container):
    n = _advanceWhile(f, container)
    return container[n:]


def head(container):
    return container[0]


def tail(container):
    return container[1:]


def cons(container, val):
    ret = container[:]
    ret.insert(0, val)
    return ret


# Higher order functions over lists:
def all(f, iterable):
    ret = True
    for element in iterable:
        if not f(element):
            ret = False
            break
    return ret


def any(f, iterable):
    ret = False
    for element in iterable:
        if f(element):
            ret = True
            break
    return ret


_map = map
def map(f, it):
    return list(_map(f, it))


def map_(f, iterable):
    for v in iterable:
        f(v)


_filter = filter
def filter(f, it):
    return list(_filter(f, it))


def zipWith(f, it1, it2):
    ret = []

    for elem in zip(it1, it2):
        ret.append(f(elem[0], elem[1]))

    return ret


# Function Generation
def flip(f):
    def ret(a, b):
        return f(b, a)
    return ret


def compose(f1, f2):
    def ret(*args):
        return f1(f2(*args))

    return ret
_c = compose


def partial(f, *args1):
    def ret(*args2):
        args = args1 + args2
        return f(*args)
    return ret
_p = partial


# Error Handling:
def pcall(f, *args, **kwargs):
    ret = None
    try:
        ret = f(*args, **kwargs)
    except:
        pass

    return ret


# Operators:
class op:
    sum = lambda x, y: x + y
    sub = lambda x, y: x - y
    mul = lambda x, y: x * y
    div = lambda x, y: x / y
    eq = lambda x, y: x == y
    neq = lambda x, y: x != y
    gt = lambda x, y: x > y
    ge = lambda x, y: x >= y
    lt = lambda x, y: x < y
    le = lambda x, y: x <= y
    minus = lambda x: -x
    andf = lambda x, y: x and y
    orf = lambda x, y: x or y
    notf = lambda x: not x
    band = lambda x, y: x & y
    bor = lambda x, y: x | y
