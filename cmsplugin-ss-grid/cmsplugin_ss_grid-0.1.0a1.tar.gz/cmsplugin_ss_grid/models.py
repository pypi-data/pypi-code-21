from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from filer.fields.image import FilerImageField
from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible

from .fields import ColorPickerField

CONFIG = getattr(settings, 'CMSPLUGIN_SS_GRID', {})

BACKGROUND_CLASSES = CONFIG.get('BACKGROUND_CLASSES', [])
CELL_CLASSES = CONFIG.get('CELL_CLASSES', [])

INHERIT = 0
SMALL_CELL_WIDTHS = [(w, str(w)) for w in range(1, 13)]
CELL_WIDTHS = [(INHERIT, 'Inherit')] + SMALL_CELL_WIDTHS


@python_2_unicode_compatible
class Container(CMSPlugin):
    background_class = models.CharField(
        _('background class'), choices=BACKGROUND_CLASSES,
        blank=True, null=True,
        max_length=255
    )
    background_image = FilerImageField(
        verbose_name=_('Background Image'),
        null=True,
        blank=True
    )
    background_color = ColorPickerField(
        verbose_name=_('Background Colour'),
        null=True,
        blank=True,
        help_text=_('This can be seen while the image loads or if there is no image')
    )

    @property
    def background_classes(self):
        return self.background_class or ''

    @property
    def background_style(self):
        rv = []
        if self.background_color:
            rv.append('background-color:{}'.format(self.background_color))
        if self.background_image:
            rv.append("background-image:url('{}')".format(self.background_image.url))
        return ';'.join(rv)

    def __str__(self):
        return self.get_background_class_display() or ''


@python_2_unicode_compatible
class ContainerCell(CMSPlugin):
    size_mobile = models.IntegerField(
        _('size mobile'),
        choices=SMALL_CELL_WIDTHS,
        default=12
    )

    size_tablet = models.IntegerField(
        _('size tablet'),
        choices=CELL_WIDTHS,
        default=INHERIT
    )

    size_desktop = models.IntegerField(
        _('size desktop'),
        choices=CELL_WIDTHS,
        default=INHERIT
    )

    size_large_desktop = models.IntegerField(
        _('size large desktop'),
        choices=CELL_WIDTHS,
        default=INHERIT
    )

    custom_class = models.CharField(
        _('class'), choices=CELL_CLASSES,
        blank=True, null=True,
        max_length=255
    )

    @property
    def classes(self):
        rv = ['col-sm-{}'.format(self.size_mobile)]
        if self.size_tablet:
            rv.append('col-md-{}'.format(self.size_tablet))
        if self.size_desktop:
            rv.append('col-lg-{}'.format(self.size_desktop))
        if self.size_large_desktop:
            rv.append('col-xl-{}'.format(self.size_large_desktop))
        if self.custom_class:
            rv.append(self.custom_class)

        return ' '.join(rv)

    def __str__(self):
        rv = ['Mobile {}'.format(self.size_mobile)]
        if self.size_tablet:
            rv.append('Tablet {}'.format(self.size_tablet))
        if self.size_desktop:
            rv.append('Desktop {}'.format(self.size_desktop))
        if self.size_large_desktop:
            rv.append('Large Desktop {}'.format(self.size_large_desktop))

        return '; '.join(rv)
