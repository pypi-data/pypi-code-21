'''
    These are three proxies for accessing input, output, and state.
    
    These allow to write::
    
        self.output.y = self.input.x * self.config.gain
    
    instead of::
        self.set_output('y', self.get_input('x') * self.get_config('gain'))
        
'''


class Proxy(object):
    def __init__(self, block):
        self.__dict__['block'] = block


class InputProxy(Proxy):

    def __getattr__(self, i):
        return self.__dict__['block'].get_input(i)

    def __getitem__(self, key):
        return self.__dict__['block'].get_input(key)

    def __setattr__(self, i, v):
        raise ValueError('You can only read input, not change it.')

    def __setitem__(self, key, value):
        raise ValueError('You can only read input, not change it.')


class OutputProxy(Proxy):

    def __getattr__(self, i):
        raise ValueError('You can only set the output.')

    def __getitem__(self, key):
        raise ValueError('You can only set the output.')

    def __setattr__(self, i, v):
        self.__dict__['block'].set_output(i, v)

    def __setitem__(self, key, value):
        self.__dict__['block'].set_output(key, value)


class StateProxy(Proxy):

    def __getattr__(self, i):
        return self.__dict__['block'].get_state(i)

    def __getitem__(self, key):
        return self.__dict__['block'].get_state(key)

    def __setattr__(self, i, v):
        self.__dict__['block'].set_state(i, v)

    def __setitem__(self, key, value):
        self.__dict__['block'].set_state(key, value)


class ConfigProxy(Proxy):

    def __getattr__(self, i):
        return self.__dict__['block'].get_config(i)

    def __getitem__(self, key):
        return self.__dict__['block'].get_config(key)

    def __setattr__(self, i, v):
        raise ValueError('You can only read config %r, not change it.' % i)

    def __setitem__(self, key, value):
        raise ValueError('You can only read config %r, not change it.' % key)

