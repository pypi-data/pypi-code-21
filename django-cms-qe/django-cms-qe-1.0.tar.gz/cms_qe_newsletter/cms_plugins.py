from typing import Iterable, Dict, Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms_qe_newsletter.forms import SubscriberForm
from django.utils.translation import ugettext as _

from .models import NewsletterPluginModel


@plugin_pool.register_plugin
class NewsletterPlugin(CMSPluginBase):
    """
    Newsletter Django-CMS plugin. Allow add the form with subscriptions on a page.
    """
    model = NewsletterPluginModel
    name = _('Newsletter subscription form')
    render_template = 'cms_qe/newsletter/newsletter.html'
    fieldsets = [
        (None, {
            'fields': (
                'title',
                'mailing_lists',
                'fullname_show',
                'fullname_require',
            )
        })
    ]
    cache = False

    def render(self, context: Dict[str, Any], instance: NewsletterPluginModel, placeholder) -> Iterable:
        request = context['request']
        if request.method == 'POST':
            form = SubscriberForm(fullname_require=instance.fullname_require, data=request.POST)
            if form.is_valid():
                form.save(instance.mailing_lists.all())
                form.saved = True
        else:
            form = SubscriberForm(fullname_require=instance.fullname_require)
        context.update({
            'instance': instance,
            'form': form,
        })
        return context
