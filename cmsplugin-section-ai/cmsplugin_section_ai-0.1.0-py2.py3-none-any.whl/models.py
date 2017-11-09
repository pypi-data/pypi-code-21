# -*- coding: utf-8 -*-
from cms.models import CMSPlugin, Page
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField
from filer.fields.file import FilerFileField

from .enums import (
    BackgroundColor,
    ButtonSize,
    ButtonStyle,
    ContainerSize,
    Justify,
    SectionPadding,
    SectionType,
    VerticalAlign
)

class Section(CMSPlugin):
    section_type = EnumField(
        SectionType,
        verbose_name=_("section type"),
        max_length=50,
        default=SectionType.ONE_COLUMN
    )
    background_color = EnumField(
        BackgroundColor,
        verbose_name=_("background color"),
        max_length=50,
        default=BackgroundColor.TRANSPARENT
    )
    background_image = FilerFileField(
        verbose_name=_(u"background image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("This overrides any given background color")
    )
    section_padding_top = EnumField(
        SectionPadding,
        verbose_name=_("top padding for this section"),
        max_length=50,
        default=SectionPadding.LARGE
    )
    section_padding_bottom = EnumField(
        SectionPadding,
        verbose_name=_("bottom padding for this section"),
        max_length=50,
        default=SectionPadding.LARGE
    )
    container_width = EnumField(
        ContainerSize,
        verbose_name=_("container width"),
        max_length=50,
        default=ContainerSize.CONTAINER
    )
    title = models.CharField(
        verbose_name=_("title"),
        max_length=75,
        blank=True,
        help_text=_("Visible title for this section")
    )
    title_position = EnumField(
        Justify,
        verbose_name=_("title alignment"),
        max_length=50,
        default=Justify.LEFT
    )
    column_vertical_alignment = EnumField(
        VerticalAlign,
        verbose_name=_("vertical alignment for columns"),
        max_length=75,
        default=VerticalAlign.TOP
    )
    extra_margin = models.BooleanField(verbose_name=_("add extra vertical margin for inner columns"), default=False)
    text_center = models.BooleanField(verbose_name=_("align column content text to center"), default=False)
    button_position = EnumField(
        Justify,
        verbose_name=_("section button alignment"),
        max_length=50,
        default=Justify.LEFT
    )
    anchor = models.CharField(
        verbose_name=_("anchor identifier"),
        max_length=50,
        blank=True,
        help_text=_("Set anchor identifier for this section to be used with anchor links.")
    )

    def __str__(self):
        return "%s - %s" % (self.section_type.label, self.title)

    @property
    def section_classes(self):
        classes = "%s %s-top %s-bottom" % (
            self.section_type.value, self.section_padding_top.value, self.section_padding_bottom.value
        )

        if self.background_image:
            classes += " section-bg-image"
        else:
            classes += " " + self.background_color.value

        return classes

    def column_classes(self):
        classes = "col-12"

        if self.section_type == SectionType.TWO_COLUMNS:
            classes += " col-md-6"
        elif self.section_type == SectionType.THREE_COLUMNS:
            classes += " col-lg-4"
        elif self.section_type == SectionType.FOUR_COLUMNS:
            classes += " col-md-6 col-lg-3"

        if self.extra_margin:
            classes += " column-extra-vertical-margin"

        return classes

    def copy_relations(self, oldinstance):
        for button in oldinstance.section_buttons.all():
            button.pk = None
            button.id = None
            button.section = self
            button.save(force_insert=True)


class Link(models.Model):
    text = models.CharField(verbose_name=_("button text"), max_length=75)
    url = models.CharField(verbose_name=_("url"), max_length=250, blank=True)
    page_link = models.ForeignKey(
        Page,
        verbose_name=_("link to a page"),
        null=True,
        blank=True,
        limit_choices_to={"publisher_is_draft": True},
        on_delete=models.SET_NULL,
        help_text=_("Page link overrides any given URL."),
        related_name="section"
    )
    style = EnumField(ButtonStyle, verbose_name=_("button style"), max_length=50, default=ButtonStyle.PRIMARY)
    size = EnumField(ButtonSize, verbose_name=_("button size"), max_length=50, default=ButtonSize.MD)
    anchor = models.CharField(
        verbose_name=_("bind to anchor"),
        max_length=30,
        blank=True,
        help_text=_("Set the anchor identifier of an element. Leave out the # prefix.")
    )

    def __str__(self):
        return self.text

    @property
    def link(self):
        link = ""

        if self.page_link:
            link = self.page_link.get_absolute_url()
        elif self.url:
            link = self.url

        if self.anchor:
            return "%s#%s" % (link, self.anchor)

        return link or "#"


class SectionButton(Link):
    section = models.ForeignKey(Section, verbose_name=_("section"), related_name="section_buttons")
