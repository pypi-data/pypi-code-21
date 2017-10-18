__all__ = ["route", "routes"]


routes = []


def route(r, func, name=None):
    """
    
    :param t: (str) http method
    :param r: (str) route
    :param func: (class|async function) handler
    :param name: route name
    :return: 
    """
    routes.append(("*", r, func, name))
