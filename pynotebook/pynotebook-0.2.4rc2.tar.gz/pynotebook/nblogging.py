# -*- coding: latin-1 -*-

# Simple logging facility. It allows to record and replay everything
# the user enters. Logging is ment for debugging. It will be removed
# once all errors are fixed :-)

_buffer = []

def log(object, descr, *args):
    # Log a change of an object. 
    _buffer.append((object, descr)+args)


def logged(f):
    def new_f(self, *args, **kwds):
        log(self, f.__name__, args, kwds)
        return f(self, *args)
    return new_f


def get_log(object):
    for l in _buffer:
        if l[0] is object:
            yield l


def write_log(filename, object):
    import cPickle
    f = open(filename, 'wb')
    l = list(get_log(object))
    cPickle.dump(l, f)
    

def load_log(filename):
    import cPickle
    return cPickle.load(open(filename, 'rb'))
    
