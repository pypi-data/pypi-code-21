from __future__ import unicode_literals

from django.conf import settings
from django.forms.widgets import TextInput
from django.template.loader import get_template


class JsTreeWidget(TextInput):
    def __init__(self, url, result_hidden=False, attrs=None):
        """
        JsTreePathFile Doc usage
        :param url: URL will serve AJAX results. See https://www.jstree.com/docs/json/
        :param result_hidden: Hide readonly input which contains selected result
        :param attrs: Override django widget HTML attributes
        """
        super(JsTreeWidget, self).__init__(attrs=attrs)
        self.url = url

        if result_hidden:
            self.input_type = 'hidden'
            self.template_name = 'django/forms/widgets/hidden.html'

        else:
            # custom widget if not specified in attrs
            self.attrs.setdefault('readonly', True)
            self.attrs.setdefault('required', True)
            self.attrs.setdefault('max_length', 255)
            self.attrs.setdefault('size', 100)

    class Media:
        css = {
            'all': (
                'jstree/css/jstree/themes/default/style{}.css/'.format('.min' if settings.DEBUG else ''),
            )
        }
        js = (
            'jstree/js/jstree{}.js'.format('.min' if settings.DEBUG else ''),
        )

    def render(self, name, value, attrs=None, renderer=None):
        rendering = super(JsTreeWidget, self).render(name, value, attrs=attrs)
        div_id = "{}-tree".format(name)
        # add custom HTML div
        template = get_template("jstree/jstree.div.html")
        rendering = "{}{}".format(rendering,
                                  template.render({'div_id': div_id,
                                                   'field_name': name, }))
        # add custom JS script
        template = get_template("jstree/jstree.init.js")
        rendering = "{}{}".format(rendering,
                                  template.render({'div_id': div_id,
                                                   'field_name': name,
                                                   'url': self.url, }))
        return rendering
