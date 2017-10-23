from .accessories import _Discoverable, _Categories, _States
from .protocol import _Types, _Status, _Codes, _HEX


class EnumValueGetter(object):
    def __init__(self, enum_):
            self.enum_ = enum_

    def __getattr__(self, value):
        return getattr(self.enum_, value).value

    def __call__(self, value):
        return self.enum_(value).name


Categories = EnumValueGetter(_Categories)
States = EnumValueGetter(_States)
Discoverable = EnumValueGetter(_Discoverable)
Types = EnumValueGetter(_Types)
Status = EnumValueGetter(_Status)
Codes = EnumValueGetter(_Codes)
HEX = _HEX
