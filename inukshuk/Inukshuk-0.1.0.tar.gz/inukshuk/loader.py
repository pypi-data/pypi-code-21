import os
import os.path


class TemplateSource:
    def __init__(self, name, source, getmtime=None):
        self.name = name
        self.source = source
        self.getmtime = getmtime


class Loader:
    def getSource(self, engine, name):
        raise NotImplementedError()

    def findAllNames(self, engine):
        return []


class FileSystemLoader(Loader):
    def __init__(self, root_dirs):
        super().__init__()
        if not isinstance(root_dirs, list):
            root_dirs = [root_dirs]
        self.root_dirs = root_dirs

    def getSource(self, engine, name):
        for r in self.root_dirs:
            try_path = os.path.join(r, name)
            try:
                with open(try_path, 'r', encoding='utf-8') as fp:
                    return TemplateSource(name, fp.read(),
                                          lambda: os.path.getmtime(try_path))
            except OSError:
                pass
        return None

    def findAllNames(self, engine):
        for r in self.root_dirs:
            for dirpath, dirnames, filenames in os.walk(r):
                for fn in filter(lambda fn: fn[0] != '.', filenames):
                    full_path = os.path.join(dirpath, fn)
                    name = os.path.relpath(full_path, r)
                    yield name


class EndPointMapLoader(Loader):
    def __init__(self, endpoints, delim='/'):
        super().__init__()
        self.endpoints = endpoints
        self.delim = delim

    def getSource(self, engine, name):
        try:
            idx = name.index(self.delim)
        except ValueError:
            return None

        endpoint = name[:idx]
        try:
            loader = self.endpoints[endpoint]
        except KeyError:
            return None

        sub_name = name[idx + 1:]
        return loader.getSource(engine, sub_name)

    def findAllNames(self, engine):
        delim = self.delim
        for e, l in self.endpoints.items():
            for name in l.findAllNames():
                yield '%s%s%s' % (e, delim, name)


class CompositeLoader(Loader):
    def __init__(self, loaders):
        super().__init__()
        self.loaders = loaders

    def getSource(self, engine, name):
        for l in self.loaders:
            b = l.getSource(engine, name)
            if b is not None:
                return b
        return None

    def findAllNames(self, engine):
        for l in self.loaders:
            yield from l.findAllNames(engine)


class StringsLoader(Loader):
    def __init__(self, templates=None):
        super().__init__()
        self.templates = templates or {}

    def getSource(self, engine, name):
        try:
            return TemplateSource(name, self.templates[name])
        except KeyError:
            return None

    def findAllNames(self, engine):
        return self.templates.keys()
