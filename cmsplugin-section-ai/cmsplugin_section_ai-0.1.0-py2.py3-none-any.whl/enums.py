# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class SectionType(Enum):
    ONE_COLUMN = "one-column-section"
    TWO_COLUMNS = "two-column-section"
    THREE_COLUMNS = "three-column-section"
    FOUR_COLUMNS = "four-column-section"

    class Labels:
        ONE_COLUMN = _("One column")
        TWO_COLUMNS = _("Two columns")
        THREE_COLUMNS = _("Three columns")
        FOUR_COLUMNS = _("Four columns")


class BackgroundColor(Enum):
    TRANSPARENT = "bg-color-transparent"
    LIGHT_GRAY = "bg-color-light-gray"
    PRIMARY = "bg-color-primary"
    SECONDARY = "bg-color-secondary"

    class Labels:
        TRANSPARENT = _("Transparent")
        LIGHT_GRAY = _("Light Gray")
        PRIMARY = _("Primary Color")
        SECONDARY = _("Secondary Color")


class ButtonStyle(Enum):
    PRIMARY = "btn-primary"
    SECONDARY = "btn-secondary"
    LIGHT = "btn-light"
    DARK = "btn-dark"

    class Labels:
        PRIMARY = _("Primary Background")
        SECONDARY = _("Secondary Background")
        LIGHT = _("Light Background")
        DARK = _("Dark Background")


class ButtonSize(Enum):
    SM = "btn-sm"
    MD = "btn-md"
    LG = "btn-lg"

    class Labels:
        SM = _("Small")
        MD = _("Medium")
        LG = _("Large")


class Justify(Enum):
    LEFT = "text-left"
    CENTER = "text-center"
    RIGHT = "text-right"

    class Labels:
        LEFT = _("Justify left")
        CENTER = _("Justify center")
        RIGHT = _("Justify right")


class ContainerSize(Enum):
    FLUID = "container-fluid"
    CONTAINER = "container"
    CONTAINER_SMALL = "container-small"

    class Labels:
        FLUID = _("Full width")
        CONTAINER = _("Regular container")
        CONTAINER_SMALL = _("Small container")


class SectionPadding(Enum):
    EXTRA_LARGE = "extra-large-padding"
    LARGE = "large-padding"
    MEDIUM = "medium-padding"
    SMALL = "small-padding"
    NONE = "no-padding"

    class Labels:
        EXTRA_LARGE = _("Extra large padding")
        LARGE = _("Large padding")
        MEDIUM = _("Medium padding")
        SMALL = _("Small padding")
        NONE = _("No padding")


class VerticalAlign(Enum):
    TOP = "align-items-start"
    CENTER = "align-items-center"
    BOTTOM = "align-items-end"

    class Labels:
        TOP = _("Top")
        CENTER = _("Center")
        BOTTOM = _("Bottom")
