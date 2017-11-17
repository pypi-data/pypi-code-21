import enum


class Widget(enum.Enum):
    BAR = 'bar'
    ETA = 'eta'
    ELAPSED = 'elapsed'
    SPINNER = 'spinner'


class StyleManager(dict):
    def __init__(self, default_style=None):
        super().__init__()
        self['default'] = default_style or Style()

    def set_style_options(self, config, **kwargs):
        pass


class Style:
    def __init__(self, widgets=None, sized=None, unsized=None):
        if widgets:
            self.sized = sized or widgets
            self.unsized = unsized or widgets
        else:
            self.sized = sized
            self.unsized = unsized

    def get_widgets(self, sized):
        return self.sized if sized else self.unsized
