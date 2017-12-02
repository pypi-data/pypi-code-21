def _(method, filename, classname):
    methodname = filename.split('.')[0]
    def f(i):
        i = i.replace('_method', methodname)
        return i.replace('_class', classname)
    return map(f, method)

