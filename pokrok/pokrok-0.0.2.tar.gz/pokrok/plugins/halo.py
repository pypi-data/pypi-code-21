from pokrok.plugins import (
    DefaultProgressMeterFactory, BaseProgressMeter, Status)
from pokrok.styles import Style, Widget


class HaloProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        style_superset = Style(unsized=[Widget.SPINNER])
        super().__init__('halo', HaloProgressMeter, style_superset)

    def iterate(
            self, iterable, size=None, widgets=None, desc=None, start=None,
            **kwargs):
        if self._load_module():
            with self._module.Halo(text=desc or '', **kwargs):
                yield from iterable
        else:
            return iterable


class HaloProgressMeter(BaseProgressMeter):
    def __init__(self, mod, size, widgets, desc, start, **kwargs):
        super().__init__(size)
        self.spinner = mod.Halo(text=desc or '', **kwargs)

    def start(self):
        super().start()
        self.spinner.start()

    def finish(self):
        super().finish()
        self.spinner.succeed()

    def increment(self, n=1):
        pass
