# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.test import TestCase

from pages.schema import schema
from pages.models.page import Page
from pages.models.slider import Slider, SliderItem, SliderContent, SliderContentType


class SliderTestCase(TestCase):

    def setUp(self):
        self._create_data()

    def _create_page(self):
        page = Page()
        page.title = 'Test Page'
        page.external_url = 'https://www.crehana.com/'
        page.is_active = True
        page.save()
        return page

    def _create_slider(self, page):
        slider = Slider()
        slider.page = page
        slider.title = 'Test Page'
        slider.is_active = True
        slider.save()
        return slider

    def _create_item_slider(self, slider):
        slider_item = SliderItem()
        slider_item.slider = slider
        slider_item.active_from = timezone.now()
        slider_item.active_to = timezone.now()
        slider_item.save()
        return slider_item

    def _create_item_slider_content(self, slider_item):
        type_content = SliderContentType.objects.all()[0]
        slider_content = SliderContent()
        slider_content.slider_item = slider_item
        slider_content.type_content = type_content
        slider_content.active_from = timezone.now()
        slider_content.active_to = timezone.now()
        slider_content.config = '{"font-size": "medium", "text-align": "center"}'
        slider_content.save()

    def _create_data(self):
        page = self._create_page()
        slider = self._create_slider(page)
        slider_item = self._create_item_slider(slider)
        self._create_item_slider_content(slider_item)

    def get_sliders_query(self):
        query = '''
                    {
                       sliders {
                         title
                         is_active
                         dots
                         speed
                         items {
                            absolute_url_picture_pc
                            absolute_url_picture_tablet
                            absolute_url_picture_mobile
                            active_from
                            active_to
                            order
                            contents {
                                content
                                config
                                order
                                type_content {
                                    name
                                }
                            }
                         }
                       }
                    }
                '''
        return query

    def test_get_sliders(self):
        result = schema.execute(self.get_sliders_query())
        sliders = result.data.get('sliders', [])
        self.assertEquals(len(sliders), 1)
