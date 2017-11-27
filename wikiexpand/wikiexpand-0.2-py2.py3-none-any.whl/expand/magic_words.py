#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

#import weakref

from ..compat import p3_str
from .tools import str2wikicode


NOT_IMPLEMENTED = (
    "NAMESPACENUMBER",
)


class MagicWord(object):
    """
    Render magic words given a page context.
    """

    def __init__(self, page_context):
        self._context = page_context
        self._pf = self._context.parser_functions

        self.magic_words = {
            "!": self.pipe,
            "PAGENAME": self.PAGENAME,
            "FULLPAGENAME": self.FULLPAGENAME,
            "NAMESPACE": self.NAMESPACE,
            "TALKSPACE": self.TALKSPACE,
            "TALKPAGENAME": self.TALKPAGENAME,
            "TALKPAGENAMEE": self.TALKPAGENAMEE,
            "ARTICLESPACE": self.ARTICLESPACE,
            "SUBJECTSPACE": self.ARTICLESPACE,
            "PAGENAMEE": self.PAGENAMEE,
            "FULLPAGENAMEE": self.FULLPAGENAMEE,
            "NAMESPACEE": self.NAMESPACEE,
            "TALKSPACEE": self.TALKSPACEE,
            "ARTICLESPACEE": self.ARTICLESPACEE,
            "SUBJECTSPACEE": self.ARTICLESPACEE,
            "CURRENTTIMESTAMP": self.DT_TIMESTAMP,
            "LOCALTIMESTAMP": self.DT_TIMESTAMP,
            "CURRENTWEEK": self.DT_WEEK,
            "LOCALWEEK": self.DT_WEEK,
            "CURRENTTIME": self.DT_TIME,
            "LOCALTIME": self.DT_TIME,
            "CURRENTHOUR": self.DT_HOUR,
            "LOCALHOUR": self.DT_HOUR,
            "CURRENTDAYNAME": self.DT_DAYNAME,
            "LOCALDAYNAME": self.DT_DAYNAME,
            "CURRENTDOW": self.DT_DOW,
            "LOCALDOW": self.DT_DOW,
            "CURRENTDAY": self.DT_DAY,
            "LOCALDAY": self.DT_DAY,
            "CURRENTDAY2": self.DT_DAY2,
            "LOCALDAY2": self.DT_DAY2,
            "CURRENTYEAR": self.DT_YEAR,
            "LOCALYEAR": self.DT_YEAR,
            "CURRENTMONTH": self.DT_MONTH,
            "LOCALMONTH": self.DT_MONTH,
            "CURRENTMONTH1": self.DT_MONTH1,
            "LOCALMONTH1": self.DT_MONTH1,
            "CURRENTMONTHNAME": self.DT_MONTHNAME,
            "LOCALMONTHNAME": self.DT_MONTHNAME,
            "CURRENTMONTHABBREV": self.DT_MONTHABBREV,
            "LOCALMONTHABBREV": self.DT_MONTHABBREV,
            "BASEPAGENAME": self.BASEPAGENAME,
            "BASEPAGENAMEE": self.BASEPAGENAMEE,
            "ROOTPAGENAME": self.ROOTPAGENAME,
            "ROOTPAGENAMEE": self.ROOTPAGENAMEE,
            "SUBPAGENAME": self.SUBPAGENAME,
            "SUBPAGENAMEE": self.SUBPAGENAMEE,
            "ARTICLEPAGENAME": self.ARTICLEPAGENAME,
            "ARTICLEPAGENAMEE": self.ARTICLEPAGENAMEE,
            "SUBJECTPAGENAME": self.ARTICLEPAGENAME,
            "SUBJECTPAGENAMEE": self.ARTICLEPAGENAMEE,
        }

    def __call__(self, name, *args, **kwargs):
        if name in NOT_IMPLEMENTED:
            raise NotImplementedError(name)

        if name in self.magic_words:
            return self.magic_words[name](*args, **kwargs)

        #raise NotImplementedError(name)
        raise KeyError(name)

    def pipe(self, *args, **kwargs):
        return str2wikicode("|")

    def PAGENAME(self, *args, **kwargs):
        name = self._context.clean_title()
        return str2wikicode(name)

    def PAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_pagenamee(name))

    def FULLPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_fullpagename(name))

    def FULLPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_fullpagenamee(name))

    def NAMESPACE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_namespace(name))

    def NAMESPACEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_namespacee(name))

    def TALKSPACE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_talkspace(name))

    def TALKSPACEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_talkspacee(name))

    def TALKPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_talkpagename(name))

    def TALKPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_talkpagenamee(name))

    def ARTICLESPACE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_articlespace(name))

    def ARTICLESPACEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_articlespacee(name))

    def DT_TIMESTAMP(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%Y%m%d%H%M%S"))

    def DT_WEEK(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(p3_str(dt.isocalendar()[1]))

    def DT_TIME(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%H:%M"))

    def DT_HOUR(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%H"))

    def DT_DAYNAME(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%A"))

    def DT_DOW(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%w"))

    def DT_DAY(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(p3_str(dt.day))

    def DT_DAY2(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%d"))

    def DT_YEAR(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%Y"))

    def DT_MONTH(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%m"))

    def DT_MONTH1(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(p3_str(dt.month))

    def DT_MONTHNAME(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%B"))

    def DT_MONTHABBREV(self, *args, **kwargs):
        dt = self._pf.aux_time
        return str2wikicode(dt.strftime("%b"))

    def BASEPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_basepagename(name))

    def BASEPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_basepagenamee(name))

    def ROOTPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_rootpagename(name))

    def ROOTPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_rootpagenamee(name))

    def SUBPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_subpagename(name))

    def SUBPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_subpagenamee(name))

    def ARTICLEPAGENAME(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_articlepagename(name))

    def ARTICLEPAGENAMEE(self, *args, **kwargs):
        name = self._context.title()
        return str2wikicode(self._pf.str_articlepagenamee(name))
