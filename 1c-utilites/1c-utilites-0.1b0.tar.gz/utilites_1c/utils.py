def import_class(path):
    '''
    Get class from string-path

    :param path: -- string containing full python-path
    :type path: str
    :return: -- return class or module in path
    :rtype: class, module, object
    '''
    m_len = path.rfind(".")
    class_name = path[m_len + 1:len(path)]
    try:
        module = __import__(path[0:m_len], globals(), locals(), [class_name])
        return getattr(module, class_name)
    except SystemExit:
        return None  # nocv


class BackendLoader(object):
    BACKENDS = None

    def get_backends_dict(self):
        return self.BACKENDS

    @property
    def backends(self):
        return self.get_backends_dict()

    def list(self):
        return sorted(self.backends.keys())

    def get(self, name):
        # pylint: disable=unsubscriptable-object
        return import_class(self.backends[name]["BACKEND"])

    def add_arguments(self, parser):
        pass

    def run(self, args):
        return self.get(args.backend)(args)
