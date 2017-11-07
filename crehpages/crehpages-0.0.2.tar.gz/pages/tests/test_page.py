# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from pages.schema import schema
from pages.utils import admin
from pages.models.page import Page


class PageTestCase(TestCase):

    def setUp(self):
        self.page = self._create_page()

    def _create_page(self):
        page = Page()
        page.title = 'Test Page'
        page.external_url = 'https://www.crehana.com/'
        page.is_active = True
        page.save()
        return page

    def get_pages_query(self):
        query = '''
                    {
                       pages {
                         title
                         slug
                         external_url
                         is_active
                       }
                     }
                '''
        return query

    def get_page_query(self):
        query = '''
                    {
                       page(id: %s) {
                         title
                         slug
                         external_url
                         is_active
                       }
                     }
                ''' % self.page.id
        return query

    def test_get_pages(self):
        result = schema.execute(self.get_pages_query())
        pages = result.data.get('pages', [])
        self.assertEquals(len(pages), 1)

    def test_get_page(self):
        result = schema.execute(self.get_page_query())
        page = result.data.get('page', {})
        self.assertEquals(page.get('title'), 'Test Page')

    def test_autogenerate_slug(self):
        self.assertEquals(self.page.slug, 'test-page')
        page = Page()
        page.title = 'Test Page'
        page.external_url = 'https://www.crehana.com/'
        page.is_active = True
        page.save()
        self.assertEquals(page.slug, 'test-page-1')
        page = Page()
        page.title = 'Test Page'
        page.external_url = 'https://www.crehana.com/'
        page.is_active = True
        page.save()
        self.assertEquals(page.slug, 'test-page-2')
