
__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'

# Credit: http://amir.rachum.com/blog/2012/04/26/implementing-the-singleton-pattern-in-python/


class SingletonType(type):

    """ Singleton Class

    You can use this class to make a singleton class by setting the __metaclass__ parameter
    of your class to this.

    For example:

        class NewSingletonClass(object):
            __metaclass__ = SingletonType

            def __init__(self):
                ...
    """

    def __call__(cls, *args, **kwargs):

        try:
            return cls.__instance

        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance
