from django.utils.translation import ugettext_lazy as _


class BasePayment:
    title = None

    def __init__(self, config={}):
        self.title = config.get('title', self.title)

    def get_title(self):
        return self.title

    def render_data(self, data, plain_text=False):
        from django.utils.safestring import mark_safe
        _template = '<h4>%s</h4>'
        if plain_text:
            _template = '%s'
        return mark_safe(_template % self.get_title())


class SimplePayment(BasePayment):
    title = _('Simple payment method')
