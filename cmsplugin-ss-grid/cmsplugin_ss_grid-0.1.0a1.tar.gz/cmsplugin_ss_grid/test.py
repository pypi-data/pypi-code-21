from django.test import TestCase
from django.test.client import RequestFactory

from cms.api import add_plugin
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer

from .cms_plugins import ContainerPlugin, ContainerCellPlugin
from .models import Container


class GridTests(TestCase):

    def test_container_html(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            ContainerPlugin,
            'en',
            background_class='background--light'
        )
        renderer = ContentRenderer(request=RequestFactory())
        html = renderer.render_plugin(model_instance, {})
        html = html.replace('\n', '')
        self.assertEqual(html, '<div class="background background--light" style=""><div class="container"><div class="row"></div></div></div>')

    def test_cell_html(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            ContainerCellPlugin,
            'en',
            size_desktop=4
        )
        renderer = ContentRenderer(request=RequestFactory())
        html = renderer.render_plugin(model_instance, {})
        html = html.replace('\n', '')
        self.assertEqual(html, '<div class="col-sm-12 col-lg-4"></div>')
