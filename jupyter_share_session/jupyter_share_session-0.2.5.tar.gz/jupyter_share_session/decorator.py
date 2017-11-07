import inspect

class MustDefineNsVal:
    pass
class SpecParamName:
    pass

class NsDefaultOrVal:
    def __init__(self, defaultVal=MustDefineNsVal, varName=SpecParamName):
        self.defaultVal = defaultVal
        self.varName = varName

nsDefault = NsDefaultOrVal()
nsOrNone = NsDefaultOrVal(None)

def defaultNsParams(ns, printNsUsage=False):
    def wrapperfunc(f):
        specargs, varargs, keywords, defaults = inspect.getargspec(f)
        def wrappedfunction(*args,**kwargs):
            for i,name in enumerate(specargs):
                if type(defaults[i]) != NsDefaultOrVal: # no use NS default
                    continue
                if len(args) > i: # name was overridden
                    continue
                if name in kwargs: # kwarg was overridden
                    continue
                varname = defaults[i].varName
                if varname == SpecParamName:
                    varname = name
                replace = defaults[i].defaultVal
                if replace == MustDefineNsVal:
                    # must specify a value in ns
                    replace = ns[varname]
                else:
                    # optional to specify a value in ns
                    replace = ns.get(varname,replace)
                if printNsUsage:
                    print('using ns default for',arg,'=',ns[varname])
                kwargs[name] = replace
            f(*args,**kwargs)
        return wrappedfunction
    return wrapperfunc

def defaultGlobalParams(printNsUsage=False):
    from IPython import get_ipython
    return defaultNsParams(get_ipython().user_global_ns, printNsUsage=printNsUsage)
