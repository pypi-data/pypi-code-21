from __future__ import unicode_literals

from django.forms.widgets import TextInput
from django.template.loader import get_template
from django.conf import settings


class JsTreeWidget(TextInput):
    def __init__(self, url, attrs=None):
        super(JsTreeWidget, self).__init__(attrs=attrs)
        self.url = url
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
        rendering = "{}{}".format(rendering,
                                  get_template("jstree/widgets/jstree.div.html").render(
                                      {'div_id': div_id,
                                       'field_name': name, })
                                  )
        rendering = "{}{}".format(rendering,
                                  get_template("jstree/widgets/jstree.init.js").render(
                                      {'div_id': div_id,
                                       'field_name': name,
                                       'url': self.url})
                                  )
        return rendering
