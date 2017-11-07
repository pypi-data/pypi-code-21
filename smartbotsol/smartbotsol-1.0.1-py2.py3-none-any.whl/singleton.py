class Singleton(type):
    """ 
    Use this class to provide singleton characteristics for your classes:

    class MyClass(BaseClass, metaclass=Singleton): 
            pass

    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]