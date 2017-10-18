#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import has_item
from hamcrest import not_none

from hamcrest import has_entry
from hamcrest import is_in
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import unittest

from zope import interface

from nti.schema.jsonschema import JsonSchemafier

from . import SchemaLayer


class TestConfiguredVocabulary(unittest.TestCase):

    layer = SchemaLayer

    def test_country_vocabulary(self):
        from zope.schema import Choice

        class IA(interface.Interface):
            choice = Choice(title=u"Choice",
                            vocabulary=u"Countries")

        o = object()

        choice = IA['choice'].bind(o)
        assert_that(choice.vocabulary, is_(not_none()))
        assert_that('us', is_in(choice.vocabulary))
        term = choice.vocabulary.getTermByToken('us')
        assert_that(term, has_property('value', "United States"))
        ext = term.toExternalObject()
        assert_that(ext, has_entry('flag', u'/++resource++country-flags/us.gif'))
        assert_that(ext, has_entry('title', 'United States'))

        schema = JsonSchemafier(IA).make_schema()
        assert_that(schema, has_entry('choice', has_entry('choices', has_item(ext))))
