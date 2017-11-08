from django.test import TestCase
from django.test.client import RequestFactory

from cms.api import add_plugin
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer

from .cms_plugins import IconPlugin
from .models import Icon


class IconTests(TestCase):

    def test_plugin_html(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            IconPlugin,
            'en',
            icon='fa-bath'
        )
        renderer = ContentRenderer(request=RequestFactory())
        html = renderer.render_plugin(model_instance, {})
        self.assertEqual(html, '<i class="fa fa-bath"></i>')

    def test_fa_icon_class_names(self):
        model = Icon(icon='fa-bath')
        self.assertEqual(model.icon_class_names, 'fa fa-bath')

    def test_extra_spin_classes(self):
        model = Icon(icon='fa-cog')
        model.spin = True
        self.assertEqual(model.icon_class_names, 'fa fa-cog fa-spin fa-fw')

    def test_extra_pulse_classes(self):
        model = Icon(icon='fa-cog')
        model.pulse = True
        self.assertEqual(model.icon_class_names, 'fa fa-cog fa-pulse fa-fw')

    def test_extra_fixed_width_classes(self):
        model = Icon(icon='fa-cog')
        model.fixed_width = True
        self.assertEqual(model.icon_class_names, 'fa fa-cog fa-fw')

    def test_extra_size_classes(self):
        model = Icon(icon='fa-cog')
        model.size = 'fa-4x'
        self.assertEqual(model.icon_class_names, 'fa fa-cog fa-4x')

    def test_str(self):
        model = Icon(icon='fa-facebook')
        self.assertEqual(str(model), 'fa-facebook')
