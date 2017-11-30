import logging

import sys
import inspect

_py2 = sys.version_info[0] == 2
logger = logging.getLogger("rpc")


def rpcapi(returns, **parameter_types):
    """rpc注册装饰器"""

    def decorator(f):
        # Put the rule cache on the method itself instead of globally
        if not hasattr(f, '_rule_cache') or f._rule_cache is None:
            f._rule_cache = {f.__name__: [(returns, parameter_types)]}
        elif not f.__name__ in f._rule_cache:
            f._rule_cache[f.__name__] = [(returns, parameter_types)]
        else:
            f._rule_cache[f.__name__].append((returns, parameter_types))

        return f

    return decorator


def get_interesting_members(cls):
    """Returns a list of methods that can be routed to"""

    predicate = inspect.ismethod if _py2 else inspect.isfunction
    all_members = inspect.getmembers(cls, predicate=predicate)
    return [member for member in all_members
            if ((hasattr(member[1], "__self__") and not member[1].__self__ in inspect.getmro(cls)) if _py2 else True)
            and not member[0].startswith("_")]



def register(handlers):
    test2 = 'syntax = "proto3";\npackage {};\n'.format(handlers.package)
    service = "service {} {{\n".format(handlers.name)

    def make_proxy_method(name):

        i = handlers()
        view = getattr(i, name)
        return view

    members = get_interesting_members(handlers)

    for name, value in members:
        proxy = make_proxy_method(name)
        for idx, cached_rule in enumerate(value._rule_cache[name]):
            returns, method = cached_rule
            return_type = returns.name
            message = "message {}Request {{".format(name)
            c = 1
            paramenter_types = str()
            for i in method:
                paramenter_types = "{} {} = {};".format(method[i].name, i, c)
                message += paramenter_types
                c += 1
            message += "}\n"
            test2 += message
            message2 = "message {}Reply {{".format(name)
            message2 += "{} {} = 1;}}\n".format(return_type, "_result")
            test2 += message2
            service += "rpc {} ({}Request) returns ({}Reply){{}}\n".format(name, name, name)
    service += "}"
    test2 += service
    logging.debug("proto file:{}".format(test2))
    return test2,handlers()
