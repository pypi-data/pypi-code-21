# -*- coding: utf-8 -*-
"""MLS development collection."""

# python imports
import copy

# zope imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.memoize.view import memoize
from plone.mls.core.navigation import ListingBatch
from z3c.form import button
from plone.supermodel.directives import fieldset
# from z3c.form.browser import checkbox
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.interface import (
    alsoProvides,
    noLongerProvides,
)
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from plone.mls.listing.browser.interfaces import (
    IBaseListingItems,
    IListingDetails,
)
from ps.plone.mls import (
    _,
    PLONE_4,
    PLONE_5,
    api,
    config,
)
from ps.plone.mls.interfaces import (
    IDevelopmentCollection,
    IDevelopmentDetails,
    IPossibleDevelopmentCollection,
)


#: Reduce the API load by defining the fields we need.
FIELDS = [
    'id',
    'title',
    'description',
    'logo',
    'location',
    'lot_size',
    'location_type',
    'number_of_listings',
    'number_of_groups',
]

EXCLUDED_SEARCH_FIELDS = [
    'map_zoom_level',
    'show_banner_image',
    'show_contact_info',
    'show_contact_form',
    'contact_override',
    'contact_form_bcc',
    'show_contact_link',
    'show_captcha',
    'modify_urls',
    'limit_developments',
    'limit_listings',
]


class DevelopmentCollectionViewlet(ViewletBase):
    """Dynamic collection of MLS developments."""

    _items = None
    _batching = None
    limit = None

    if PLONE_5:
        index = ViewPageTemplateFile('templates/development_results_p5.pt')
    elif PLONE_4:
        index = ViewPageTemplateFile('templates/development_results.pt')

    @property
    def available(self):
        """Check if this viewlet is available for rendering."""
        return IDevelopmentCollection.providedBy(self.context) and \
            not IDevelopmentDetails.providedBy(self.view) and \
            not IBaseListingItems.providedBy(self.view) and \
            not IListingDetails.providedBy(self.view)

    @property
    def config(self):
        """Get the embedding configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(config.SETTINGS_DEVELOPMENT_COLLECTION, {})

    def update(self):
        """Prepare view related data."""
        super(DevelopmentCollectionViewlet, self).update()
        self.context_state = queryMultiAdapter(
            (self.context, self.request), name='plone_context_state',
        )

        if self.available:
            # Only query the MLS if we show the viewlet.
            self.limit = self.config.get('limit_developments', 5)
            self._get_items()

    @property
    @memoize
    def items(self):
        """Return the collection items."""
        return self._items

    def _get_items(self):
        """Get the collection items from the MLS."""
        lang = self.portal_state.language()
        mlsapi = api.get_api(context=self.context, lang=lang)
        fields = copy.copy(FIELDS)
        if self.config.get('show_banner_image', False):
            fields.append('banner_image')
        params = {
            # 'summary': '1',
            'fields': u','.join(fields),
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
        }
        params.update(self.config)
        params = api.prepare_search_params(
            params,
            context=self.context,
            omit=EXCLUDED_SEARCH_FIELDS,
        )
        try:
            result = api.Development.search(mlsapi, params=params)
        except Exception:
            pass
        else:
            self._items = result.get_items()
            headers = result.get_headers()
            self._batching = {
                'results': headers.get('CountTotal'),
            }

    @memoize
    def view_url(self):
        """Generate view url."""
        if not self.context_state.is_view_template():
            # We have the default view rendered.
            return self.context_state.current_base_url()
        else:
            return '/'.join([
                absoluteURL(self.context, self.request),
                '',
            ])

    @property
    def batching(self):
        """Create the batch provider for the collection items."""
        if not self.items:
            return
        return ListingBatch(
            self.items,
            self.limit,
            self.request.get('b_start', 0),
            orphan=1,
            batch_data=self._batching,
        )

    def get_url(self, item):
        """Get the (possibly modified) URL for the development item."""
        url = u'{0}{1}'.format(self.view_url(), item.id.value)
        if self.config.get('modify_url', True):
            url = u'{0}___{1}-{2}'.format(
                url,
                item.title.value,
                item.location.value,
            )
        return url


FIELDS_FILTER = (
    'agency_developments',
    'q',
    'sort_on',
    'reverse',
)


class IDevelopmentCollectionConfiguration(form.Schema):
    """Development Collection Configuration Form."""

    fieldset(
        'filter',
        label=_(u'Filter Options'),
        fields=FIELDS_FILTER,
    )

    # Fields for 'Defautl' fieldset.
    map_zoom_level = schema.Int(
        default=7,
        description=_(
            u'Set the resolution for the map. 0 is the lowest zoom level, in '
            u'which the entire world can be seen. The higher the zoom level, '
            u'the more details can be seen. The available maximum zoom level '
            u'value differs from area to area and can change over time, also '
            u'depending on the used map provider.'
        ),
        min=0,
        max=21,
        required=True,
        title=_(u'Zoom level for maps'),
    )

    show_banner_image = schema.Bool(
        default=False,
        description=_(
            u'If enabled, show the development banner in the collection '
            u'results.'
        ),
        required=False,
        title=_(u'Show Banner Image'),
    )

    show_contact_info = schema.Bool(
        default=False,
        description=_(
            u'If enabled, the contact information for a development will be '
            u'shown on the detail page for a development.'
        ),
        required=False,
        title=_(u'Show Contact Information'),
    )

    show_contact_form = schema.Bool(
        default=False,
        description=_(
            u'If enabled, a form to contact the responsible agent will be '
            u'shown on the detail page for a development.'
        ),
        required=False,
        title=_(u'Show Contact Form'),
    )

    contact_override = schema.TextLine(
        description=_(
            u'Send the contact form to this email instead direct to the agent'
        ),
        required=False,
        title=_(u'Alternative Email recipient'),
    )

    contact_form_bcc = schema.TextLine(
        description=_(
            u'E-mail addresses which receive a blind carbon copy (comma '
            u'separated).'
        ),
        required=False,
        title=_(u'BCC Recipients'),
    )

    show_contact_link = schema.Bool(
        default=False,
        description=_(
            u'If the contact form is enabled, an anchor link will show as '
            u'quick navigation to the form.'
        ),
        required=False,
        title=_(u'Show Contact-Us anchor link'),
    )

    show_captcha = schema.Bool(
        default=False,
        description=_(
            u'Show a captcha field within the contact form to prevent spam.'
        ),
        required=False,
        title=_(u'Show Captcha'),
    )

    modify_url = schema.Bool(
        default=True,
        description=_(
            u'Modify the individual development URLs to show extra '
            u'information, such as the Title and Location'
        ),
        required=False,
        title=_(u'Modify URLs'),
    )

    limit_developments = schema.Int(
        default=5,
        description=_(
            u'How many developments should be shown per page?'
        ),
        required=True,
        title=_(u'Developments per Page'),
    )

    limit_listings = schema.Int(
        default=25,
        description=_(
            u'How many listings should be shown per devlopment listings page?'
        ),
        required=True,
        title=_(u'Listings per Page'),
    )

    # Fields for 'Filter Options' fieldset.
    agency_developments = schema.Bool(
        default=False,
        description=_(
            u'If enabled, only developments for the configured agency '
            u'will be shown.'
        ),
        required=False,
        title=_(u'Agency Developments'),
    )

    q = schema.TextLine(
        description=_(
            u'Enter a search term to filter the results.'
        ),
        required=False,
        title=_(u'Searchable Text'),
    )

    sort_on = schema.Choice(
        description=_(
            u'How should the results be sorted? If nothing is selected, the '
            u'results are sorted by relevance.'
        ),
        required=False,
        title=_('Sort results by'),
        vocabulary='ps.plone.mls.developments.sort_options',
    )

    reverse = schema.Bool(
        default=False,
        required=False,
        title=_('Reverse sort order?'),
    )

    # location_state = schema.Choice(
    #     required=False,
    #     title=_(u'State'),
    #     source='plone.mls.listing.LocationStates',
    # )

    # location_county = schema.Choice(
    #     required=False,
    #     title=_(u'County'),
    #     source='plone.mls.listing.LocationCounties',
    # )

    # location_district = schema.Choice(
    #     required=False,
    #     title=_(u'District'),
    #     source='plone.mls.listing.LocationDistricts',
    # )

    # location_type = schema.Tuple(
    #     required=False,
    #     title=_(u'Location Type'),
    #     value_type=schema.Choice(
    #         source='plone.mls.listing.LocationTypes'
    #     ),
    # )

    # geographic_type = schema.Tuple(
    #     required=False,
    #     title=_(u'Geographic Type'),
    #     value_type=schema.Choice(
    #         source='plone.mls.listing.GeographicTypes'
    #     ),
    # )

    # view_type = schema.Tuple(
    #     required=False,
    #     title=_(u'View Type'),
    #     value_type=schema.Choice(
    #         source='plone.mls.listing.ViewTypes'
    #     ),
    # )


class DevelopmentCollectionConfiguration(form.SchemaForm):
    """Development Collection Configuration Form."""

    schema = IDevelopmentCollectionConfiguration
    label = _(u'\'Development Collection\' Configuration')
    description = _(
        u'Adjust the behaviour for this \'Development Collection\' viewlet.'
    )

    def getContent(self):
        annotations = IAnnotations(self.context)
        return annotations.get(
            config.SETTINGS_DEVELOPMENT_COLLECTION,
            annotations.setdefault(config.SETTINGS_DEVELOPMENT_COLLECTION, {})
        )

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        annotations = IAnnotations(self.context)
        annotations[config.SETTINGS_DEVELOPMENT_COLLECTION] = data
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        self.request.response.redirect(absoluteURL(self.context, self.request))


class DevelopmentCollectionStatus(object):
    """Return activation/deactivation status of the viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleDevelopmentCollection.providedBy(self.context) and \
            not IDevelopmentCollection.providedBy(self.context)

    @property
    def active(self):
        return IDevelopmentCollection.providedBy(self.context)


class DevelopmentCollectionToggle(object):
    """Toggle DevelopmentCollection viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IDevelopmentCollection.providedBy(self.context):
            # Deactivate DevelopmentCollection viewlet.
            noLongerProvides(self.context, IDevelopmentCollection)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Development Collection\' viewlet deactivated.')
        elif IPossibleDevelopmentCollection.providedBy(self.context):
            alsoProvides(self.context, IDevelopmentCollection)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Development Collection\' viewlet activated.')
        else:
            msg = _(
                u'The \'Development Collection\' viewlet does\'t work with '
                u'this content type. Add \'IPossibleDevelopmentCollection\' '
                u'to the provided interfaces to enable this feature.'
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())
