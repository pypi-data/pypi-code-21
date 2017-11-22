''' A small synchronous plugin applicator module. '''

from lib.plugins.hipchat import HipChatPlugin


class Anchor():
    '''
    Anchor is a small but powerful way to architect libraries.
    Classes are created by base classing Anchor.
    Call apply to register callbacks on any plugin.
    The plugins can be called via "apply_plugins".
    Plugins would generally receive a single arg - "compilation"
    Very similar to webpack's tapable. (https://github.com/webpack/tapable)
    '''

    def __init__(self):
        ''' Initialize our plugin pool. '''
        self._plugins = {}

        self.apply(HipChatPlugin())

    def apply_plugins(self, event, *args, **kwargs):
        ''' Apply plugins registered for a event. '''
        if isinstance(event, list):
            for name in event:
                self.apply_plugins(name, *args, **kwargs)
            return

        if event not in self._plugins:
            return
        plugins = self._plugins[event]
        for plugin in plugins:
            plugin(*args, **kwargs)

    def has_plugins(self, event):
        ''' Check if any plugins are registered to a event. '''
        if event not in self._plugins:
            return False
        plugins = self._plugins[event]

        return len(plugins)

    def plugin(self, event, callback_function):
        ''' Register a plugin under a event. '''
        if isinstance(event, list):
            for name in event:
                self.plugin(name, callback_function)
            return
        if event not in self._plugins:
            self._plugins[event] = [callback_function]
        else:
            self._plugins[event].append(callback_function)

    def apply(self, *args):
        ''' Attaches the plugins to the instance. '''
        for arg in args:
            arg.apply(self)
