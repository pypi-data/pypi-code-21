# coding: utf-8
from django.utils.translation import ugettext_lazy as _


QUESTION_TYPE_RADIO = u'Radio'
QUESTION_TYPE_CHECKBOXES = u'Checkboxes'
QUESTION_TYPE_SELECT = u'Select'
QUESTION_TYPE_TEXT = u'Text'
QUESTION_TYPE_TEXTAREA = u'TextArea'
QUESTION_TYPE_NUMBER = u'Number'
QUESTION_TYPE_DATE = u'Date'
QUESTION_TYPE_DATETIME = u'DateTime'
QUESTION_TYPE_LIST = u'List'
QUESTION_TYPE_GRID = u'Grid'

QUESTION_TYPE_CHOICES = (
    (QUESTION_TYPE_RADIO, _(u'Radio')),
    (QUESTION_TYPE_CHECKBOXES, _(u'Checkboxes')),
    (QUESTION_TYPE_SELECT, _(u'Select')),
    (QUESTION_TYPE_TEXT, _(u'Text')),
    (QUESTION_TYPE_TEXTAREA, _(u'TextArea')),
    (QUESTION_TYPE_NUMBER, _(u'Number')),
    (QUESTION_TYPE_DATE, _(u'Date')),
    (QUESTION_TYPE_DATETIME, _(u'DateTime')),
    (QUESTION_TYPE_LIST, _(u'List')),
    (QUESTION_TYPE_GRID, _(u'Grid')),
)
