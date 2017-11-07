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

def defaultNsParams(ns, printNsUsage=False, nsName='default namespace'):
    def wrapperfunc(f):
        specargs, varargs, keywords, defaults = inspect.getargspec(f)
        offset = len(specargs) - len(defaults)
        def wrappedfunction(*args,**kwargs):
            for i,name in enumerate(specargs[offset:]):
                if type(defaults[i]) != NsDefaultOrVal: # no use NS default
                    continue
                if len(args) > offset+i: # name was overridden
                    continue
                if name in kwargs: # kwarg was overridden
                    continue
                varname = defaults[i].varName
                if varname == SpecParamName:
                    varname = name
                replace = defaults[i].defaultVal
                if replace == MustDefineNsVal:
                    # must specify a value in ns
                    if varname not in ns:
                        raise Exception("Missing value for "+varname+" in "+nsName+".")
                    replace = ns[varname]
                else:
                    # optional to specify a value in ns
                    replace = ns.get(varname,replace)
                if printNsUsage:
                    print('using ns default for',varname,'=',ns[varname])
                kwargs[name] = replace
            f(*args,**kwargs)
        return wrappedfunction
    return wrapperfunc

def defaultGlobalParams(f):
    from IPython import get_ipython
    return defaultNsParams(get_ipython().user_global_ns, nsName='globals', printNsUsage=get_ipython().user_global_ns.get('printNsUsage', False) )(f)

