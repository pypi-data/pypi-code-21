


REGISTRY = {}


def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class


class MetaRegistry(type):

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if name not in REGISTRY:
            register_class(cls)
        return cls


class BaseClass():
    __metaclass__ = MetaRegistry


class Foo(BaseClass):
    pass


class Bar(BaseClass):
    pass


def main():
    
    print(REGISTRY)

if __name__ == '__main__':
    
    print('This is only for testing!!')
    
    main()