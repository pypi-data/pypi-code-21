# -*- coding: utf-8 -*-
"""Listing search banner."""

# python imports
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import copy
import urlparse

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from plone.supermodel.directives import fieldset
from plone.z3cform import z2
# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False
from z3c.form import (
    button,
    field,
)
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import StaticWidgetAttribute
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import (
    alsoProvides,
    noLongerProvides,
)
from zope.schema.vocabulary import (
    SimpleTerm,
    SimpleVocabulary,
)

# local imports
from ps.plone.mls import (
    _,
    PLONE_4,
    PLONE_5,
    config,
)
from ps.plone.mls.interfaces import (
    IListingSearchBanner,
    IPossibleListingSearchBanner,
)

FIELDS_SECTION_1 = [
    'section_1_search_target',
    'section_1_title',
    'section_1_categories',
    'section_1_default_category',
    'section_1_hide_categories',
    'section_1_hide_beds',
    'section_1_hide_section',
]
FIELDS_SECTION_2 = [
    'section_2_search_target',
    'section_2_title',
    'section_2_categories',
    'section_2_default_category',
    'section_2_hide_categories',
    'section_2_hide_beds',
    'section_2_hide_section',
]
FIELDS_SECTION_3 = [
    'section_3_search_target',
    'section_3_title',
    'section_3_categories',
    'section_3_default_category',
    'section_3_hide_categories',
    'section_3_hide_beds',
    'section_3_hide_section',
]
FIELDS_SECTION_4 = [
    'section_4_search_target',
    'section_4_title',
    'section_4_categories',
    'section_4_default_category',
    'section_4_hide_categories',
    'section_4_hide_beds',
    'section_4_hide_section',
]
FIELDS_UI = [
    'image',
    'image_url',
]

LABEL_SECTION_SEARCH_PAGE = _(u'Search Target Page')
LABEL_SECTION_TITLE = _(u'Title')
LABEL_SECTION_CATEGORIES = _(u'Categories')
LABEL_SECTION_DEFAULT_CATEGORY = _(u'Default Category')
LABEL_SECTION_HIDE_CATEGORY = _(u'Hide category')
LABEL_SECTION_HIDE_BEDS = _(u'Hide bedrooms')
LABEL_SECTION_HIDE_SECTION = _(u'Hide section')

DESCRIPTION_SECTION_SEARCH_PAGE = _(
    u'Select the activated listing search page which will be used to show '
    u'the results.'
)
DESCRIPTION_SECTION_TITLE = _(u'')
DESCRIPTION_SECTION_CATEGORIES = _(u'')
DESCRIPTION_SECTION_DEFAULT_CATEGORY = _(u'')
DESCRIPTION_SECTION_HIDE_CATEGORY = _(
    u'Hide the category field and use default setting.'
)
DESCRIPTION_SECTION_HIDE_BEDS = _(
    u'Hide the bedrooms field.'
)
DESCRIPTION_SECTION_HIDE_SECTION = _(
    u'Don\'t show this section at all.'
)

DEFAULT_CATEGORIES_1 = (
    u'all:All:listing_type=rs,cs,ll\n'
    u'houses:Houses:listing_type=rs&object_type=house,mobile,multiplex,'
    u'townhouse,freestanding_villa\n'
    u'condos:Condos:listing_type=rs&object_type=apartment,condominium,'
    u'half_duplex\n'
    u'land:Land:listing_type=ll\n'
    u'commercial:Commercial:listing_type=cs&object_type=\n'
)

DEFAULT_CATEGORIES_2 = (
    u'all:All:listing_type=rl,cl\n'
    u'houses:Houses:listing_type=rl&object_type=house,mobile,multiplex,'
    u'townhouse,freestanding_villa\n'
    u'condos:Condos:listing_type=rl&object_type=apartment,condominium,'
    u'half_duplex\n'
    u'commercial:Commercial:listing_type=cl&object_type=\n'
)


class ISectionForm(form.Schema):
    """Section Search Form schema."""

    category = schema.Choice(
        required=True,
        title=_(u'Category'),
        values=['one', 'two'],
    )

    q = schema.TextLine(
        required=False,
        title=_(u'Location, Keywords, Listing ID, ...'),
    )

    beds = schema.Choice(
        required=False,
        title=_(u'Bedrooms'),
        source='ps.plone.mls.listings.min_bedrooms',
    )

    price_min = schema.Int(
        required=False,
        title=_(u'Price (Min)'),
    )

    price_max = schema.Int(
        required=False,
        title=_(u'Price (Max)'),
    )


class SectionForm(form.Form):
    """Section Search Form."""

    fields = field.Fields(ISectionForm)
    ignoreContext = True
    method = 'post'

    def __init__(self, context, request, config=None, prefix=None):
        super(SectionForm, self).__init__(context, request)
        self.config = config
        self.categories = None
        self.category_queries = {}
        if prefix is not None and isinstance(prefix, basestring):
            self.prefix = 'form.{0}.'.format(prefix)

    @button.buttonAndHandler(PMF(u'label_search', default=u'Search'),
                             name='search')
    def handle_search(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        url = '?'.join([
            self.search_target_url,
            self.prepare_query_string(data),
        ])
        self.request.response.redirect(url)

    def _prepare_category_search(self, query):
        result = []
        prefix = 'form.{0}.widgets.'.format(self.search_target_id)
        params = dict(urlparse.parse_qsl(query))
        for key, value in params.items():
            values = value.split(',')
            if len(values) > 1:
                for item in values:
                    result.append(urlencode({
                        prefix + key + ':list': item,
                    }))
            else:
                result.append(urlencode({prefix + key: value}))
        return '&'.join(result)

    def prepare_query_string(self, data=None):
        prefix = 'form.{0}.widgets.'.format(self.search_target_id)
        category_query = ''
        query = {
            'form.{0}.buttons.search'.format(self.search_target_id): '',
        }
        if not data:
            return ''
        beds = data.pop('beds', None)
        if beds:
            query[prefix + 'beds-min'] = beds
            query[prefix + 'beds-max'] = '--MAXVALUE--'
        category = data.pop('category', None)
        if self.config.get('hide_categories', False):
            category = self.config.get('default_category', None)
        if category:
            q = self.category_queries.get(category)
            category_query = self._prepare_category_search(q)
        for key, value in data.items():
            if value is not None:
                query[prefix + key] = value
        return '&'.join([
            urlencode(query),
            category_query,
        ])

    @property
    def search_target_url(self):
        target_uid = self.config.get('search_target', None)
        if not target_uid:
            return
        obj = api.content.get(UID=target_uid)
        return obj.absolute_url()

    @property
    def search_target_id(self):
        target_uid = self.config.get('search_target', None)
        if not target_uid:
            return
        obj = api.content.get(UID=target_uid)
        return obj.id

    def update(self):
        """Update form to match configuration."""
        omitted = []
        self._generate_categories()
        if self.config.get('hide_categories', False) or not self.categories:
            omitted.append('category')
        if self.config.get('hide_beds', False):
            omitted.append('beds')
        self.fields = field.Fields(ISectionForm).omit(*omitted)
        self.update_fields()
        super(SectionForm, self).update()
        if PLONE_5:
            if 'category' in self.widgets:
                self.widgets['category'].pattern_options = {
                    'placeholder': _(u'Select a Category'),
                }
            if 'beds' in self.widgets:
                self.widgets['beds'].pattern_options = {
                    'placeholder': _(u'Beds'),
                }

    def update_fields(self):
        """Update form field configurations."""
        if 'category' in self.fields:
            field = self.fields['category']
            field.field.vocabulary = self.categories
            default = self.config.get('default_category', None)
            if default not in self.category_queries:
                default = list(self.categories)[0].token
            field.field.default = default

        if PLONE_5:
            from plone.app.z3cform.widget import SelectFieldWidget

            if 'category' in self.fields:
                self.fields['category'].widgetFactory = SelectFieldWidget
            if 'beds' in self.fields:
                self.fields['beds'].widgetFactory = SelectFieldWidget

    def _generate_categories(self):
        """Return a new categories vocabulary."""
        categories = self.config.get('categories', None)
        if not categories:
            return
        terms = []
        for category in categories.splitlines():
            try:
                key, title, query = category.split(':')
            except ValueError:
                continue
            else:
                terms.append(SimpleTerm(key, key, title))
                self.category_queries[key] = query

        self.categories = SimpleVocabulary(terms)


class SearchBanner(ViewletBase):
    """Listing Search Banner."""

    if PLONE_5:
        index = ViewPageTemplateFile('templates/search_banner_p5.pt')
    elif PLONE_4:
        index = ViewPageTemplateFile('templates/search_banner.pt')
    config = None
    section_1 = None
    section_2 = None
    section_3 = None
    section_4 = None

    @property
    def available(self):
        """Check if this viewlet is available for rendering."""
        return IListingSearchBanner.providedBy(self.context) and (
            self.section_1 or self.section_2 or
            self.section_3 or self.section_4
        )

    def get_config(self):
        """Get the configuration data from annotations."""
        annotations = IAnnotations(self.context)
        self.config = copy.deepcopy(
            annotations.get(config.SETTINGS_LISTING_SEARCH_BANNER, {})
        )

    @property
    def image_url(self):
        """Return the image URL for the background image."""
        image = self.config.get('image', None)
        if image is not None:
            filename, data = b64decode_file(image)
            return '{0}/@@listing-search-banner-image/{1}'.format(
                self.context.absolute_url(),
                filename,
            )
        image_url = self.config.get('image_url', None)
        if image_url is not None and image_url != u'http://':
            return image_url

    def map_config(self, section=None):
        """Return a config specific for a section."""
        config = {}
        if section is None:
            return
        if not isinstance(section, basestring):
            return
        for key in self.config.keys():
            if key.startswith(section):
                new_key = key[len(section) + 1:]
                config[new_key] = self.config.get(key)
        return config

    def setup_forms(self):
        """Initialize the section forms."""
        z2.switch_on(self, request_layer=IFormLayer)
        if not self.config.get('section_1_hide_section', False) and \
                self.config.get('section_1_search_target', None):
            self.section_1 = SectionForm(
                aq_inner(self.context),
                self.request,
                config=self.map_config('section_1'),
                prefix='section_1',
            )
            if HAS_WRAPPED_FORM:
                alsoProvides(self.section_1, IWrappedForm)
            self.section_1.update()
        if not self.config.get('section_2_hide_section', False) and \
                self.config.get('section_2_search_target', None):
            self.section_2 = SectionForm(
                aq_inner(self.context),
                self.request,
                config=self.map_config('section_2'),
                prefix='section_2',
            )
            if HAS_WRAPPED_FORM:
                alsoProvides(self.section_2, IWrappedForm)
            self.section_2.update()
        if not self.config.get('section_3_hide_section', False) and \
                self.config.get('section_3_search_target', None):
            self.section_3 = SectionForm(
                aq_inner(self.context),
                self.request,
                config=self.map_config('section_3'),
                prefix='section_3',
            )
            if HAS_WRAPPED_FORM:
                alsoProvides(self.section_3, IWrappedForm)
            self.section_3.update()
        if not self.config.get('section_4_hide_section', False) and \
                self.config.get('section_4_search_target', None):
            self.section_4 = SectionForm(
                aq_inner(self.context),
                self.request,
                config=self.map_config('section_4'),
                prefix='section_4',
            )
            if HAS_WRAPPED_FORM:
                alsoProvides(self.section_4, IWrappedForm)
            self.section_4.update()

    def update_config(self):
        if not self.config.get('section_1_title', None):
            self.config['section_1_title'] = u'Section 1'
        if not self.config.get('section_2_title', None):
            self.config['section_2_title'] = u'Section 2'
        if not self.config.get('section_3_title', None):
            self.config['section_3_title'] = u'Section 3'
        if not self.config.get('section_4_title', None):
            self.config['section_4_title'] = u'Section 4'

    def update(self):
        """Prepare view related data."""
        super(SearchBanner, self).update()
        self.get_config()
        self.update_config()
        self.setup_forms()


class ISearchBannerConfiguration(form.Schema):
    """Listing Search Banner configuration form schema."""

    fieldset('section_1', label=_(u'Section 1'), fields=FIELDS_SECTION_1)
    fieldset('section_2', label=_(u'Section 2'), fields=FIELDS_SECTION_2)
    fieldset('section_3', label=_(u'Section 3'), fields=FIELDS_SECTION_3)
    fieldset('section_4', label=_(u'Section 4'), fields=FIELDS_SECTION_4)
    fieldset('ui', label=_(u'UI'), fields=FIELDS_UI)

    form.widget(image=NamedImageFieldWidget)
    image = schema.ASCII(
        description=_(
            u'Upload an image file which will be used as a background for '
            u'your listing banner search.'
        ),
        required=False,
        title=_(u'Banner Image'),
    )

    image_url = schema.TextLine(
        default=u'http://',
        description=_(
            u'Instead of uploading an image, you may enter the URL of an '
            u'image hosted on another server.'
        ),
        max_length=511,
        required=False,
        title=_(u'Banner Image URL'),
    )

    section_1_search_target = schema.Choice(
        description=DESCRIPTION_SECTION_SEARCH_PAGE,
        required=False,
        vocabulary='ps.plone.mls.listings.available_searches',
        title=LABEL_SECTION_SEARCH_PAGE,
    )

    section_1_title = schema.TextLine(
        default=_(u'Buy'),
        description=DESCRIPTION_SECTION_TITLE,
        required=False,
        title=LABEL_SECTION_TITLE,
    )

    try:
        form.widget('section_1_categories', rows=6)
    except TypeError:
        pass
    section_1_categories = schema.Text(
        default=DEFAULT_CATEGORIES_1,
        description=DESCRIPTION_SECTION_CATEGORIES,
        required=False,
        title=LABEL_SECTION_CATEGORIES,
    )

    section_1_default_category = schema.TextLine(
        default=u'houses',
        description=DESCRIPTION_SECTION_DEFAULT_CATEGORY,
        required=False,
        title=LABEL_SECTION_DEFAULT_CATEGORY,
    )

    section_1_hide_categories = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_CATEGORY,
        required=False,
        title=LABEL_SECTION_HIDE_CATEGORY,
    )

    section_1_hide_beds = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_BEDS,
        required=False,
        title=LABEL_SECTION_HIDE_BEDS,
    )

    section_1_hide_section = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_SECTION,
        required=False,
        title=LABEL_SECTION_HIDE_SECTION,
    )

    section_2_search_target = schema.Choice(
        description=DESCRIPTION_SECTION_SEARCH_PAGE,
        required=False,
        vocabulary='ps.plone.mls.listings.available_searches',
        title=LABEL_SECTION_SEARCH_PAGE,
    )

    section_2_title = schema.TextLine(
        default=_(u'Rent'),
        description=DESCRIPTION_SECTION_TITLE,
        required=False,
        title=LABEL_SECTION_TITLE,
    )

    try:
        form.widget('section_2_categories', rows=6)
    except TypeError:
        pass
    section_2_categories = schema.Text(
        default=DEFAULT_CATEGORIES_2,
        description=DESCRIPTION_SECTION_CATEGORIES,
        required=False,
        title=LABEL_SECTION_CATEGORIES,
    )

    section_2_default_category = schema.TextLine(
        default=u'houses',
        description=DESCRIPTION_SECTION_DEFAULT_CATEGORY,
        required=False,
        title=LABEL_SECTION_DEFAULT_CATEGORY,
    )

    section_2_hide_categories = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_CATEGORY,
        required=False,
        title=LABEL_SECTION_HIDE_CATEGORY,
    )

    section_2_hide_beds = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_BEDS,
        required=False,
        title=LABEL_SECTION_HIDE_BEDS,
    )

    section_2_hide_section = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_SECTION,
        required=False,
        title=LABEL_SECTION_HIDE_SECTION,
    )

    section_3_search_target = schema.Choice(
        description=DESCRIPTION_SECTION_SEARCH_PAGE,
        required=False,
        vocabulary='ps.plone.mls.listings.available_searches',
        title=LABEL_SECTION_SEARCH_PAGE,
    )

    section_3_title = schema.TextLine(
        description=DESCRIPTION_SECTION_TITLE,
        required=False,
        title=LABEL_SECTION_TITLE,
    )

    try:
        form.widget('section_3_categories', rows=6)
    except TypeError:
        pass
    section_3_categories = schema.Text(
        description=DESCRIPTION_SECTION_CATEGORIES,
        required=False,
        title=LABEL_SECTION_CATEGORIES,
    )

    section_3_default_category = schema.TextLine(
        description=DESCRIPTION_SECTION_DEFAULT_CATEGORY,
        required=False,
        title=LABEL_SECTION_DEFAULT_CATEGORY,
    )

    section_3_hide_categories = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_CATEGORY,
        required=False,
        title=LABEL_SECTION_HIDE_CATEGORY,
    )

    section_3_hide_beds = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_BEDS,
        required=False,
        title=LABEL_SECTION_HIDE_BEDS,
    )

    section_3_hide_section = schema.Bool(
        default=True,
        description=DESCRIPTION_SECTION_HIDE_SECTION,
        required=False,
        title=LABEL_SECTION_HIDE_SECTION,
    )

    section_4_search_target = schema.Choice(
        description=DESCRIPTION_SECTION_SEARCH_PAGE,
        required=False,
        vocabulary='ps.plone.mls.listings.available_searches',
        title=LABEL_SECTION_SEARCH_PAGE,
    )

    section_4_title = schema.TextLine(
        description=DESCRIPTION_SECTION_TITLE,
        required=False,
        title=LABEL_SECTION_TITLE,
    )

    try:
        form.widget('section_4_categories', rows=6)
    except TypeError:
        pass
    section_4_categories = schema.Text(
        description=DESCRIPTION_SECTION_CATEGORIES,
        required=False,
        title=LABEL_SECTION_CATEGORIES,
    )

    section_4_default_category = schema.TextLine(
        description=DESCRIPTION_SECTION_DEFAULT_CATEGORY,
        required=False,
        title=LABEL_SECTION_DEFAULT_CATEGORY,
    )

    section_4_hide_categories = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_CATEGORY,
        required=False,
        title=LABEL_SECTION_HIDE_CATEGORY,
    )

    section_4_hide_beds = schema.Bool(
        description=DESCRIPTION_SECTION_HIDE_BEDS,
        required=False,
        title=LABEL_SECTION_HIDE_BEDS,
    )

    section_4_hide_section = schema.Bool(
        default=True,
        description=DESCRIPTION_SECTION_HIDE_SECTION,
        required=False,
        title=LABEL_SECTION_HIDE_SECTION,
    )


class SearchBannerConfiguration(form.SchemaForm):
    """Listing Search Banner Configuration Form."""

    schema = ISearchBannerConfiguration
    label = _(u'\'Listing Search Banner\' Configuration')
    description = _(
        u'Adjust the behaviour for this \'Listing Search Banner\'.'
    )

    def getContent(self):
        annotations = IAnnotations(self.context)
        return annotations.get(
            config.SETTINGS_LISTING_SEARCH_BANNER,
            annotations.setdefault(config.SETTINGS_LISTING_SEARCH_BANNER, {})
        )

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        annotations = IAnnotations(self.context)
        annotations[config.SETTINGS_LISTING_SEARCH_BANNER] = data
        api.portal.show_message(
            message=PMF(u'Changes saved.'),
            request=self.request,
        )


class SearchBannerStatus(object):
    """Return activation/deactivation status of the viewlet."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        return IPossibleListingSearchBanner.providedBy(self.context) and \
            not IListingSearchBanner.providedBy(self.context)

    @property
    def active(self):
        return IListingSearchBanner.providedBy(self.context)


class SearchBannerToggle(object):
    """Toggle listing search banner viewlet for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg_type = 'info'

        if IListingSearchBanner.providedBy(self.context):
            # Deactivate search banner viewlet.
            noLongerProvides(self.context, IListingSearchBanner)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Listing Search Banner\' deactivated.')
        elif IPossibleListingSearchBanner.providedBy(self.context):
            alsoProvides(self.context, IListingSearchBanner)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'\'Listing Search Banner\' activated.')
        else:
            msg = _(
                u'The \'Listing Search Banner\' does\'t work with '
                u'this content type. Add \'IPossibleListingSearchBanner\' '
                u'to the provided interfaces to enable this feature.'
            )
            msg_type = 'error'

        api.portal.show_message(
            request=self.request,
            message=msg,
            type=msg_type,
        )
        self.request.response.redirect(self.context.absolute_url())


class BannerImage(Download):
    """Banner image download view."""

    def __init__(self, context, request):
        super(BannerImage, self).__init__(context, request)
        self.filename = None
        self.data = None

        image = self.config.get('image', None)
        if image is not None:
            filename, data = b64decode_file(image)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename
            # self.width, self.height = self.data.getImageSize()

    @property
    def config(self):
        """Get the configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(config.SETTINGS_LISTING_SEARCH_BANNER, {})

    def _getFile(self):
        return self.data


NoValueBedrooms = StaticWidgetAttribute(
    _('Beds'),
    field=ISectionForm['beds'],
)
