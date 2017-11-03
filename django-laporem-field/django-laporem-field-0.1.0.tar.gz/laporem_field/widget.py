from django.forms import widgets
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import uuid


class LaporemWidget(widgets.Textarea):
    def __init__(self, attrs=None, laporem_model_file=None, base_model=None):
        self.laporem_model_file = laporem_model_file
        self.base_model = base_model
        super(LaporemWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        laporem_model_file = self.laporem_model_file
        base_model = self.base_model
        if not isinstance(value, str):
            if value and value.count() > 0:
                uid = value.first().object_id
            else:
                uid = uuid.uuid4()
        else:
            uid = value
            value = None

        return mark_safe(render_to_string('laporem/laporem_index.html', {
            'laporem_model_file': laporem_model_file.__name__.lower(),
            'name_field': name,
            'base_model': base_model,
            'value': str(uid),
            'objs': value
        }))

    class Media:
        js = ()

        jquery_url = getattr(settings, 'LAPOREM_JQUERY_URL', None)
        if jquery_url:
            js += (jquery_url,)
        try:
            js += (
                settings.STATIC_URL + 'laporem/js/jquery-ui.min.js',
                settings.STATIC_URL + 'laporem/js/laporem-init.js',
            )
            css = {
                'screen': (
                    settings.STATIC_URL+'laporem/css/style.css',
                ),
            }

        except:pass

