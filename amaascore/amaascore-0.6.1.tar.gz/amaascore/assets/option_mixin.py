from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal


class OptionMixin(object):

    @property
    def option_style(self):
        if hasattr(self, '_option_style'):
            return self._option_style

    @option_style.setter
    def option_style(self, option_style):
        if option_style in ['American', 'Bermudan', 'European']:
            self._option_style= option_style
        else:
            raise ValueError("Invalid value for option_style: %s" % option_style)

    @property
    def option_type(self):
        if hasattr(self, '_option_type'):
            return self._option_type

    @option_type.setter
    def option_type(self, option_type):
            if option_type in ['Put', 'Call']:
                self._option_type = option_type
            else:
                raise ValueError("Invalid value for option_type: %s" % option_type)

    @property
    def strike(self):
        if hasattr(self, '_strike'):
            return self._strike

    @strike.setter
    def strike(self, strike):
        """ Force strike to be a Decimal. """
        if strike:
            self._strike = Decimal(strike)

