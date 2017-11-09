from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


class CarouselPlugin(CMSPlugin):
    """A carousel"""

    # VERTICAL = True
    # HORIZONTAL = False
    # VERTICAL_CHOICES = (
    #     (HORIZONTAL, _('Horizontal')),
    #     (VERTICAL, _('Vertical'))
    # )

    name = models.SlugField(
        _('name'),
        max_length=30,
        unique=False,  # django-cms keeps two copies
        blank=False,
        null=False
    )

    show_arrows = models.BooleanField(
        _('show arrows'),
        default=True,
        help_text=_('Enable Next/Prev arrows.')
    )

    autoplay = models.BooleanField(
        _('autoplay'),
        default=True,
        help_text=_('Enable auto play of slides.')
    )

    autoplay_speed = models.SmallIntegerField(
        _('autoplay speed'),
        default=3000,
        help_text=_('Auto play change interval (in milliseconds).')
    )

    slides_to_show = models.SmallIntegerField(
        _('slides to show'),
        default=1,
        help_text=_('Number of slides to show at a time.')
    )

    center_mode = models.BooleanField(
        _('center mode'),
        default=True,
        help_text=_(
            'Enable centered view with partial prev/next slides. '
            'Use with odd numbered slidesToShow counts.'
        )
    )

    dots = models.BooleanField(
        _('show dots'),
        default=True,
        help_text=_('Show current slide indicator dots.')
    )

    focus_on_select = models.BooleanField(
        _('focus on select'),
        default=False,
        help_text=_('Enable focus on selected element (click).')
    )

    infinite = models.BooleanField(
        _('infinite'),
        default=True,
        help_text=_('Infinite looping.')
    )

    speed = models.SmallIntegerField(
        _('speed'),
        default=300,
        help_text=_('Transition speed (in milliseconds).')
    )

    # vertical = models.BooleanField(
    #     _('slide direction'),
    #     choices=VERTICAL_CHOICES,
    #     default=HORIZONTAL
    # )

    variable_width = models.BooleanField(
        _('variable width'),
        default=True,
        help_text=_('Variable width slides.')
    )

    height = models.CharField(
        _('height'),
        max_length=10,
        null=False, blank=False,
        help_text=_('CSS size for the carousel height.')
    )

    slide_margin = models.CharField(
        _('slide margin'),
        max_length=10,
        null=False, blank=False,
        help_text=_('CSS size for the margin between slides.')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Carousel')
        verbose_name_plural = _('Carousels')


class SlidePlugin(CMSPlugin):
    """A generic slide"""

    show_caption = models.BooleanField(
        _('show caption'),
        default=False,
    )

    caption_text = models.CharField(
        _('caption'), max_length=400, default='', blank=True,
    )

    def __str__(self):
        return self.caption_text

    class Meta:
        verbose_name = _('Slide')
        verbose_name_plural = _('Slides')
