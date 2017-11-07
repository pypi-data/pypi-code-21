from IPython import get_ipython
import inspect

class NsDefault:
    pass

def defaultNsParams(ns, defaultMarker=NsDefault, printNsUsage=False):
    def wrapperfunc(f):
        specargs, varargs, keywords, defaults = inspect.getargspec(f)
        def wrappedfunction(*args,**kwargs):
            for i,arg in enumerate(specargs):
                if defaults[i] != defaultMarker:
                    continue
                if len(args) > i:
                    continue
                if arg in kwargs:
                    continue
                if printNsUsage:
                    print('using ns default for',arg,'=',ns[arg])
                kwargs[arg] = ns[arg]
            f(*args,**kwargs)
        return wrappedfunction
    return wrapperfunc

