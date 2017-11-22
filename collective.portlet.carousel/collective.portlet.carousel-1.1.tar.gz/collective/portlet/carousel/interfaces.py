from i18n import MessageFactory as _

from plone.supermodel.model import Schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel.directives import fieldset
from plone.namedfile.field import NamedBlobImage
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.interface import alsoProvides, Interface

from z3c.relationfield.schema import RelationChoice, RelationList

# GOOD
import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.widgets')
except pkg_resources.DistributionNotFound:
    from plone.formwidget.contenttree import ObjPathSourceBinder
    HAS_WIDGETS = False
else:
    HAS_WIDGETS = True


class ICarouselItem(Interface):
    """ Marker inferface for item that it can be considered a carousel item """


class ICarouselItemBehavior(Schema, ICarouselItem):

    fieldset(
        'carousel',
        label=_('fieldset_carousel', default=u'Carousel'),
        fields=(
            'carousel_heading',
            'carousel_description',
            'carousel_background',
            'carousel_background_link',
            'carousel_link',
            'carousel_extlink',
            'carousel_caption',
        ),
    )

    carousel_heading = schema.TextLine(
        title=_(u"Carousel heading"),
        description=_(u"If this heading is not specified the title of the "
                      u"object will be used as heading"),
        required=False
    )

    carousel_description = schema.Text(
        title=_(u"Carousel description"),
        description=_(u"If this description is not specified the description "
                      u"of the object will be used as description"),
        required=False
    )

    carousel_background = NamedBlobImage(
        title=_(u"Carousel background"),
        description=_(u"This image is used as background in the carousel"),
        required=False
    )

    if HAS_WIDGETS:
        carousel_background_link = RelationChoice(
            title=_(u"Carousel background link"),
            description=_(u"If selected this link will be used "
                          u"from background in the carousel"),
            required=False,
            vocabulary='plone.app.vocabularies.Catalog'
        )

        carousel_link = RelationChoice(
            title=_(u"Carousel link"),
            description=_(
                u"If selected this link will be used from the carousel "
                u"item, otherwise a link to this object is used"),
            required=False,
            vocabulary='plone.app.vocabularies.Catalog'
        )
    else:
        carousel_background_link = RelationChoice(
            title=_(u"Carousel background link"),
            description=_(u"If selected this link will be used "
                          u"from background in the carousel"),
            required=False,
            source=ObjPathSourceBinder(portal_type=['Image']),
        )

        carousel_link = RelationChoice(
            title=_(u"Carousel link"),
            description=_(
                u"If selected this link will be used from the carousel "
                u"item, otherwise a link to this object is used"),
            required=False,
            source=ObjPathSourceBinder(),
        )

    carousel_extlink = schema.URI(
        title=_(u"Carousel external link"),
        description=_(u"Entering a manual link here will override  "
                      u"any selection in the link field above."),
        required=False
    )

    carousel_caption = schema.Text(
        title=_(u"Carousel caption"),
        description=u'',
        required=False
    )

alsoProvides(ICarouselItemBehavior, IFormFieldProvider)


class ICarouselPortlet(IPortletDataProvider):
    title = schema.TextLine(
        title=_(u"Portlet header"),
    )

    if HAS_WIDGETS:
        collection_reference = RelationChoice(
            title=_(u"Collection reference"),
            description=_(
                u"Select the collection that should be used to fetch "
                u"the elements that are shown in the carousel"),
            required=False,
            vocabulary='plone.app.vocabularies.Catalog'
        )

        references = RelationList(
            title=_(u"References to elements"),
            description=_(
                u"If no collection is selected the following elements "
                u"will be displayed in the carousel"),
            value_type=RelationChoice(
                required=False,
                vocabulary='plone.app.vocabularies.Catalog'
            ),
            required=False
        )

    else:
        collection_reference = RelationChoice(
            title=_(u"Collection reference"),
            description=_(
                u"Select the collection that should be used to fetch "
                u"the elements that are shown in the carousel"),
            required=False,
            source=ObjPathSourceBinder(portal_type=['Collection',
                                                    'Topic']),
        )

        references = RelationList(
            title=_(u"References to elements"),
            description=_(
                u"If no collection is selected the following elements "
                u"will be displayed in the carousel"),
            value_type=RelationChoice(
                required=False,
                source=ObjPathSourceBinder(
                    object_provides=ICarouselItem.__identifier__
                ),
            ),
            required=False
        )

    limit = schema.Int(
        title=_(u"Number of elements to be shown in the carousel"),
        required=True,
    )

    timeout = schema.Int(
        title=_(u"Rotation speed"),
        description=_(u"How long to display each banner (in seconds)."),
        required=True,
    )

    automatic_rotation = schema.Bool(
        title=_(u"Automatic rotation"),
        required=False,
        default=True,
    )

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above "
                      u"without the standard header, border or footer"),
        required=False,
        default=False
    )
