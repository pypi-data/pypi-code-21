import importlib

def getClass(modulePath, className):
    module = importlib.import_module(modulePath)
    return module.__dict__[className]

def getClassByPath(classPath):
    path       = classPath.split(".")
    modulePath = ".".join(path[:-1])
    className  = path[-1]
    return getClass(modulePath, className)

def getModule(modulePath):
    return importlib.import_module(modulePath)
