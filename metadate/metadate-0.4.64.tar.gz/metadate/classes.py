from datetime import datetime
from metadate.utils import Units
from metadate.utils import FREQ
from metadate.utils import RD_ARG_TO_UNIT
from dateutil.relativedelta import relativedelta


class Meta(object):

    def __init__(self, x, span):
        self.x = x
        self.span = span

    def __repr__(self):
        msg = "{}(x={})"
        return msg.format(self.__class__.__name__, self.x)


class MetaPeriod(Meta):

    def __init__(self, start_date, end_date, level, spans, locale, text):
        self.start_date = start_date
        self.end_date = end_date
        self.level = level
        self.spans = spans
        self.locale = locale
        self.text = text
        self.matches = [text[i:j] for i, j in spans]

    def __repr__(self):
        name = self.__class__.__name__
        cases = ['start_date', 'end_date', 'level', 'matches', 'locale']
        n = len(name) + 1
        atts = ", ".join([str(getattr(self, x))
                          for x in cases if getattr(self, x, None) is not None])
        return "{}({})".format(name, atts)

    def to_dict(self):
        result = {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'level': self.level,
            'spans': [{"begin": x[0], "end": x[1]} for x in self.spans],
            'matches': self.matches,
        }
        return result


class MetaUnit(Meta):

    def __init__(self, unit, span, modifier=1):
        self.unit = unit
        self.span = span
        self.level = Units[unit]
        self.modifier = modifier

    def __repr__(self):
        cases = ["unit", "modifier"]
        atts = {x: str(getattr(self, x)) for x in cases if getattr(self, x, None) is not None}
        values = ', '.join(["{}={}".format(x, atts[x]) for x in cases if x in atts])
        return "{}({})".format(self.__class__.__name__, values)


class MetaOrdinal(Meta):

    def __init__(self, amount, span):
        self.amount = float(amount)
        self.span = span

    def __repr__(self):
        cases = ["amount"]
        atts = {x: str(getattr(self, x)) for x in cases if getattr(self, x, None) is not None}
        values = ', '.join(["{}={}".format(x, atts[x]) for x in cases if x in atts])
        return "{}({})".format(self.__class__.__name__, values)


class MetaRelative(Meta):

    def __init__(self, span, level=None, rd=None, **rd_args):
        if level is None:
            level = min([RD_ARG_TO_UNIT[x] for x in rd_args])
        self.rd_args = rd_args
        self.level = level
        if rd is not None:
            self.rd = rd_args
        else:
            for x in ["seasons", "quarters"]:
                if x in rd_args:
                    del rd_args[x]
            self.rd = relativedelta(**rd_args)
        self.span = span

    def __add__(self, other):
        # if overlap, crash
        rd = self.rd + other.rd
        level = self.level if self.level > other.level else other.level
        span = sorted(self.span + other.span)
        return MetaRelative(level, span, rd=rd)

    def __repr__(self):
        return "{}(rd={}, level={})".format(self.__class__.__name__, self.rd, self.level)


class MetaModifier(Meta):

    def __init__(self, x, value, span):
        self.x = x
        self.value = value
        self.span = span

    def __repr__(self):
        msg = "{}(x={}, value={})"
        return msg.format(self.__class__.__name__, self.x, self.value)


class MetaRange(Meta):
    pass


class MetaBetween(Meta):

    def __init__(self, start, end, level, span):
        self.start = start
        self.end = end
        self.level = level
        self.span = span

    def __repr__(self):
        msg = "{}(start={}, end={}, level={})"
        return msg.format(self.__class__.__name__, self.start, self.end, self.level)


class MetaEvery(Meta):

    def __init__(self, freq, interval, level, span):
        self.span = span
        self.freq = freq
        self.interval = interval
        self.level = level

    def __repr__(self):
        msg = "{}(freq={}, interval={}, level={})"
        return msg.format(self.__class__.__name__, self.freq, self.interval, self.level)


class MetaAnd(Meta):
    pass


class MetaDuration(Meta):

    def __init__(self, rd, level, span):
        self.span = span
        self.rd = rd
        self.level = level

    def __repr__(self):
        msg = "{}(rd={}, level={})"
        return msg.format(self.__class__.__name__, self.rd, self.level)
