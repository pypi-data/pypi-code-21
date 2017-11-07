from IPython import get_ipython
import inspect

class MustDefineNsVal:
    pass
class NsDefaultOrVal:
    def __init__(self, defaultVal=MustDefineNsVal):
        self.defaultVal = defaultVal

nsDefault = NsDefaultOrVal()
nsOrNone = NsDefaultOrVal(None)

def defaultNsParams(ns, printNsUsage=False):
    def wrapperfunc(f):
        specargs, varargs, keywords, defaults = inspect.getargspec(f)
        def wrappedfunction(*args,**kwargs):
            for i,arg in enumerate(specargs):
                if type(defaults[i]) != NsDefaultOrVal: # no use NS default
                    continue
                if len(args) > i: # arg was overridden
                    continue
                if arg in kwargs: # kwarg was overridden
                    continue
                replace = defaults[i].defaultVal
                if replace == MustDefineNsVal:
                    # must specify a value in ns
                    replace = ns[arg]
                else:
                    # optional to specify a value in ns
                    replace = ns.get(arg,replace)
                if printNsUsage:
                    print('using ns default for',arg,'=',ns[arg])
                kwargs[arg] = replace
            f(*args,**kwargs)
        return wrappedfunction
    return wrapperfunc

