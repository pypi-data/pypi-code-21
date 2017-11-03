

from Tkinter import W, EW
from uiutil.frame.frame import BaseFrame
from uiutil.window.root import RootWindow
from uiutil.widget.entry import TextEntry

if __name__ == u"__main__":
    import sys
    sys.path.append(u'..')
    from validation import valid_ipv4, valid_ipv6
else:
    from ..validation import valid_ipv4, valid_ipv6


class IPv4Entry(TextEntry):
    DEFAULT_VALUE = u'0.0.0.0'
    VALID_CHARACTERS = u'0123456789.'

    def __init__(self,
                 *args,
                 **kwargs):
        super(IPv4Entry, self).__init__(*args,
                                        **kwargs)

    @staticmethod
    def valid(value):
        return valid_ipv4(value)

    @staticmethod
    def permit_invalid_value(value):
        return len([c for c in value if c not in IPv4Entry.VALID_CHARACTERS]) == 0


class IPv6Entry(TextEntry):
    DEFAULT_VALUE = u'::'
    VALID_CHARACTERS = u'0123456789ABCDEFabcdef:'

    def __init__(self,
                 *args,
                 **kwargs):

        super(IPv6Entry, self).__init__(*args,
                                        **kwargs)

    @staticmethod
    def valid(value):
        return valid_ipv6(value)

    @staticmethod
    def permit_invalid_value(value):
        return len([c for c in value if c not in IPv6Entry.VALID_CHARACTERS]) == 0


class IPTestFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.label(text=u'IPv4:',
                   row=self.row.next(),
                   column=self.column.start(),
                   sticky=W)

        self.__ipv4_field = IPv4Entry(width=len(u'255.255.255.255'),
                                      row=self.row.current,
                                      column=self.column.next(),
                                      sticky=W)

        self.label(text=u'IPv6:',
                   row=self.row.next(),
                   column=self.column.start(),
                   sticky=W)

        self.__ipv6_field = IPv6Entry(width=len(u'abcd:abcd:abcd:abcd:abcd:abcd:abcd:abcd'),
                                      column=self.column.next(),
                                      sticky=W)


class DeviceIPEntryTest(RootWindow):

    def __init__(self, *args, **kwargs):
        super(DeviceIPEntryTest, self).__init__(*args, **kwargs)

    def _setup(self):

        self.title(u"Test Device Frame")
        self.ip_frame = IPTestFrame(parent=self._main_frame)
        self.ip_frame.grid(sticky=EW)


if __name__ == u'__main__':
    DeviceIPEntryTest()
