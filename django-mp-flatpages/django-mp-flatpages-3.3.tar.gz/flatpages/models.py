
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


class FlatPage(models.Model):

    site = models.ForeignKey(
        Site, verbose_name=_('Site'), default=settings.SITE_ID)

    url = models.CharField(_('URL'), max_length=100, db_index=True)

    title = models.CharField(_('title'), max_length=200)

    meta_k = models.CharField(_('keywords'), max_length=200)

    meta_d = models.CharField(_('description'), max_length=200)

    content = models.TextField(_('content'), blank=True)

    template_name = models.CharField(
        _('template name'), max_length=70, blank=True,
        help_text=_(
            "Example: 'flatpages/contact_page.html'. If this isn't provided, "
            "the system will use 'flatpages/default.html'."
        ),
    )
    registration_required = models.BooleanField(
        _('registration required'),
        help_text=_("If this is checked, only logged-in "
                    "users will be able to view the page."),
        default=False)

    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ['url']

    def __unicode__(self):
        return "%s -- %s" % (self.url, self.title)
