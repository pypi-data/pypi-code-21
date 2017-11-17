from pokrok.plugins import (
    DefaultProgressMeterFactory, BaseProgressMeter, Status)
from pokrok.styles import Style, Widget


class TqdmProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        style_superset = Style([
            Widget.BAR, Widget.ETA, Widget.ELAPSED, Widget.SPINNER
        ])
        super().__init__('tqdm', TqdmProgressMeter, style_superset)

    def iterate(
            self, iterable, size=None, widgets=None, desc=None, start=None,
            **kwargs):
        if self._load_module():
            return self._module.tqdm(
                iterable, total=size, desc=desc, initial=start or 0, **kwargs)
        else:
            return iterable


class TqdmProgressMeter(BaseProgressMeter):
    def __init__(self, mod, size, widgets, desc, start, **kwargs):
        super().__init__(size)
        self.tqdm = mod.tqdm(
            total=size, desc=desc, initial=start or 0, **kwargs)

    def finish(self):
        super().finish()
        self.tqdm.close()

    def increment(self, n=1):
        self._check_status(Status.STARTED)
        self.tqdm.update(n)
