from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, StreamFieldPanel, FieldRowPanel,
    MultiFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from molo.core.blocks import MarkDownBlock
from molo.core.utils import generate_slug
from molo.core.models import (
    ArticlePage,
    SectionPage,
    TranslatablePageMixinNotRoutable,
    PreventDeleteMixin,
    Main,
    index_pages_after_copy,
)

SectionPage.subpage_types += ['yourwords.YourWordsCompetition']


class YourWordsCompetitionIndexPage(Page, PreventDeleteMixin):
    parent_page_types = ['core.Main']
    subpage_types = ['yourwords.YourWordsCompetition']

    def copy(self, *args, **kwargs):
        site = kwargs['to'].get_site()
        main = site.root_page
        YourWordsCompetitionIndexPage.objects.child_of(main).delete()
        super(YourWordsCompetitionIndexPage, self).copy(*args, **kwargs)


@receiver(index_pages_after_copy, sender=Main)
def create_yourwords_competition_index_page(sender, instance, **kwargs):
    if not instance.get_children().filter(
            title='Your words competitions').exists():
        yourwords_competition_index = YourWordsCompetitionIndexPage(
            title='Your words competitions', slug=('yourwords-%s' % (
                generate_slug(instance.title), )))
        instance.add_child(instance=yourwords_competition_index)
        yourwords_competition_index.save_revision().publish()


class YourWordsCompetition(TranslatablePageMixinNotRoutable, Page):
    parent_page_types = [
        'yourwords.YourWordsCompetitionIndexPage', 'core.SectionPage']
    subpage_types = ['yourwords.TermsAndConditions', 'yourwords.ThankYou']
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', MarkDownBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
    ], null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    extra_style_hints = models.TextField(
        default='',
        null=True, blank=True,
        help_text=_(
            "Styling options that can be applied to this section "
            "and all its descendants"))

    def get_effective_extra_style_hints(self):
            return self.extra_style_hints

    def get_effective_image(self):
        return self.image

    def thank_you_page(self):
        qs = ThankYou.objects.live().child_of(self)
        if qs.exists():
            return qs.last()
        return None

    class Meta:
        verbose_name = 'YourWords Competition'
        verbose_name_plural = 'YourWords Competitions'


YourWordsCompetition.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('description'),
    ImageChooserPanel('image'),
    StreamFieldPanel('content'),
    MultiFieldPanel(
        [
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ],
        heading="Your Words Competition Settings",)
]

YourWordsCompetition.settings_panels = [
    MultiFieldPanel(
        [FieldRowPanel(
            [FieldPanel('extra_style_hints')], classname="label-above")],
        "Meta")
]


class YourWordsCompetitionEntry(models.Model):
    competition = models.ForeignKey(YourWordsCompetition)
    submission_date = models.DateField(null=True, blank=True,
                                       auto_now_add=True)
    user = models.ForeignKey('auth.User')
    story_name = models.CharField(max_length=128)
    story_text = models.TextField()
    terms_or_conditions_approved = models.BooleanField()
    hide_real_name = models.BooleanField()
    is_read = models.BooleanField(default=False)
    is_shortlisted = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)

    article_page = models.ForeignKey(
        'core.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Page to which the entry was converted to')
    )

    panels = [
        MultiFieldPanel(
            [
                # TODO: Use ReadOnlyPanel for story_name and story_text
                # TODO: Add back other fields as read_only
                FieldPanel('competition'),
                FieldPanel('story_name'),
                FieldPanel('story_text'),
                FieldPanel('is_read'),
                FieldPanel('is_shortlisted'),
                FieldPanel('is_winner'),
            ],
            heading="Entry Settings",)
    ]

    class Meta:
        verbose_name = 'YourWords Competition Entry'
        verbose_name_plural = 'YourWords Competition Entries'


class TermsAndConditions(ArticlePage):
    parent_page_types = ['yourwords.YourWordsCompetition']
    subpage_types = []

    def get_parent_page(self):
        return YourWordsCompetition.objects.all().ancestor_of(self).last()


TermsAndConditions.promote_panels = [
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]


class ThankYou(ArticlePage):
    parent_page_types = ['yourwords.YourWordsCompetition']
    subpage_types = []

    def get_parent_page(self):
        return YourWordsCompetition.objects.all().ancestor_of(self).last()


ThankYou.promote_panels = [
    MultiFieldPanel(
        Page.promote_panels,
        "Common page configuration", "collapsible collapsed")]
