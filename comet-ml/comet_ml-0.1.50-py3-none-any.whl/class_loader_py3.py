from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

class CustomLoader(SourceFileLoader):
    def __init__(self, fullname, spec, source, target, class_name):
        super(CustomLoader, self).__init__(fullname, spec)
        self.source_func_name = source
        self.target_func = target
        self.class_name = class_name

    def exec_module(self, module):
        super().exec_module(module)

        if self.class_name is not None:
            class_pointer = getattr(module, self.class_name)
            source_func = getattr(class_pointer, self.source_func_name)
            source_func_logged = self.target_func(source_func)
            setattr(class_pointer, self.source_func_name, source_func_logged)
        else:
            source_func = getattr(module, self.source_func_name)
            source_func_logged = self.target_func(source_func)
            setattr(module, self.source_func_name, source_func_logged)

        return module


class Finder(PathFinder):
    def __init__(self, module_name, source, target, class_name=None):
        self.module_name = module_name
        self.source = source
        self.target = target
        self.class_name = class_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            loader = CustomLoader(fullname, spec.origin, self.source, self.target, self.class_name)
            return ModuleSpec(fullname, loader)