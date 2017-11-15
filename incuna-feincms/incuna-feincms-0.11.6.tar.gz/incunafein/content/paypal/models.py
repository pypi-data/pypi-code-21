from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import RequestContext


class PaypalContent(models.Model):
    title = models.CharField(max_length=200,help_text=_('This will be used before the paypal buy now buttons and on the paypal shopping cart.'))
    price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        abstract = True
        verbose_name = _('paypal')
        verbose_name_plural = _('paypals')

    def render(self, **kwargs):
        paypal_email = settings.PAYPAL_EMAIL
        paypal_url = getattr(settings, 'PAYPAL_URL', 'https://www.paypal.com/cgi-bin/webscr')
        paypal_vat = getattr(settings, 'PAYPAL_VAT', None)
        self.site = Site.objects.get_current()
        request = kwargs.get('request')

        return render_to_string([
            'content/paypal/%s.html' % self.region,
            'content/paypal/default.html',
            ], {'content': self, 'paypal_email': paypal_email, 'paypal_url': paypal_url, 'paypal_vat':paypal_vat}, context_instance=RequestContext(request))


