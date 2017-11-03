# -*- coding: utf-8 -*-
"""MLS development detail view."""

# python imports
from email import message_from_string
from email.utils import (
    formataddr,
    getaddresses,
)
from mls.apiclient import exceptions
import json
import logging
import pkg_resources

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api as plone_api
from plone.app.layout.viewlets.common import ViewletBase
from plone.directives import form
from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.formwidget.captcha.validator import (
    CaptchaValidator,
    WrongCaptchaCode,
)
from plone.memoize.view import memoize
from plone.mls.core.navigation import ListingBatch
try:
    from plone.mls.listing.interfaces import IMLSUISettings
    HAS_UI_SETTINGS = True
except ImportError:
    HAS_UI_SETTINGS = False
from plone.registry.interfaces import IRegistry  # noqa
from plone.z3cform import z2
from z3c.form import (
    button,
    field,
    validator,
)
from z3c.form.interfaces import HIDDEN_MODE, IFormLayer
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import (
    getUtility,
    queryMultiAdapter,
)
from zope.i18n import translate
from zope.interface import (
    alsoProvides,
    implementer,
)

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

# local imports
from ps.plone.mls import (
    _,
    PLONE_4,
    PLONE_5,
    api,
    config,
    utils,
)
from ps.plone.mls.interfaces import IDevelopmentDetails


logger = logging.getLogger(config.PROJECT_NAME)

EMAIL_TEMPLATE = _(
    u'development_contact_email',
    default=u'Enquiry from: {name} <{sender_from_address}>\n'
    u'Development URL: {url}\n'
    u'\n'
    u'Message:\n'
    u'{message}'
)


MAP_JS = """
var isTouch = false;
var map;

window.addEventListener('touchmove', function MoveDetector(){{
    isTouch = true;
    window.removeEventListener('touchmove', MoveDetector);
    map = initializeMap();
}});

function loadScript(src, callback) {{
  var script = document.createElement("script");
  script.type = "text/javascript";
  if (callback) {{
    script.onload = callback;
  }}
  document.getElementsByTagName("head")[0].appendChild(script);
  script.src = src;
}}


function loadGoogleMaps(callback) {{
  if (typeof google === 'object' && typeof google.maps === 'object') {{
    callback();
  }} else {{
    loadScript('https://maps.googleapis.com/maps/api/js?key={ak}', callback);
  }}
}}


function initializeMap() {{
    var center = new google.maps.LatLng({lat}, {lng})

    var myOptions = {{
        zoom: {zoom},
        center: center,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        mapTypeControl: true,
        disableDoubleClickZoom: true,
        overviewMapControl: true,
        streetViewControl: true,
        scrollwheel: false,
        draggable:!isTouch
    }}

    var map = new google.maps.Map(
        document.getElementById('{map_id}'),
        myOptions
    );

    var has_marker = true;
    if(has_marker) {{
        var myLatlng = new google.maps.LatLng({lat}, {lng});
        var marker = new google.maps.Marker({{
            position: myLatlng,
            map: map,
            icon: {icon}
        }});
    }}

    google.maps.event.addDomListener(window, "resize", function() {{
        var center = map.getCenter();
        google.maps.event.trigger(map, "resize");
        map.setCenter(center);
    }});

    return map;
}};

loadGoogleMaps(initializeMap);

"""


class IContactForm(form.Schema):
    """Contact Form schema."""

    sender_from_address = schema.TextLine(
        constraint=utils.validate_email,
        description=PMF(
            u'help_sender_from_address',
            default=u'',
        ),
        required=True,
        title=PMF(u'label_sender_from_address', default=u'E-Mail'),
    )

    name = schema.TextLine(
        description=PMF(
            u'help_sender_fullname',
            default=u'',
        ),
        required=True,
        title=PMF(u'label_name', default=u"Name"),
    )

    phone = schema.TextLine(
        required=False,
        title=PMF(u'label_phone', default=u'Phone')
    )

    message = schema.Text(
        constraint=utils.contains_nuts,
        description=PMF(
            u'help_message',
            default=u'',
        ),
        max_length=1000,
        required=True,
        title=PMF(u'label_message', default=u'Message'),
    )

    form.widget(captcha=CaptchaFieldWidget)
    captcha = schema.TextLine(
        required=True,
        title=_(u'Captcha'),
    )

    subject = schema.TextLine(
        required=False,
        title=PMF(u'label_subject', default=u'Subject')
    )


class ContactForm(form.Form):
    """Contact Form."""

    fields = field.Fields(IContactForm)
    ignoreContext = True
    method = 'post'
    _email_sent = False
    fields['captcha'].widgetFactory = CaptchaFieldWidget
    email_override = None

    def __init__(self, context, request, info=None, development=None):
        super(ContactForm, self).__init__(context, request)
        self.item_info = info
        self.development = development

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(config.SETTINGS_DEVELOPMENT_COLLECTION, {})

    def update(self):
        if self.config.get('show_captcha', False) is False:
            self.fields = field.Fields(IContactForm).omit('captcha')

        email_override = self.config.get('contact_override', None)

        if email_override is not None:
            self.email_override = email_override

        super(ContactForm, self).update()

    def updateWidgets(self):
        super(ContactForm, self).updateWidgets()
        urltool = plone_api.portal.get_tool(name='portal_url')
        portal = urltool.getPortalObject()
        subject = u'{portal_title}: {title}'.format(
            portal_title=portal.getProperty('title').decode('utf-8'),
            title=self.development.title.value,
        )
        self.widgets['subject'].mode = HIDDEN_MODE
        self.widgets['subject'].value = subject

    @property
    def already_sent(self):
        return self._email_sent

    @button.buttonAndHandler(PMF(u'label_send', default='Send'), name='send')
    def handle_send(self, action):
        """Send button for sending the email."""
        can_send = True
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if 'captcha' in data:
            can_send = False
            # Verify the user input against the captcha
            captcha = CaptchaValidator(
                self.context,
                self.request,
                None,
                IContactForm['captcha'],
                None,
            )
            try:
                can_send = captcha.validate(data['captcha'])
            except WrongCaptchaCode, e:
                self.status = e.doc()
                return

        if not self.already_sent and can_send:
            if self.send_email(data):
                self._email_sent = True
                plone_api.portal.show_message(
                    message=_(u'Your contact request was sent successfully.'),
                    request=self.request,
                    type='info',
                )
        self.request.response.redirect(self.request.URL)
        return

    def send_email(self, data):
        """Construct and send an email message."""
        urltool = plone_api.portal.get_tool(name='portal_url')
        portal = urltool.getPortalObject()

        try:
            email_charset = plone_api.portal.get_registry_record(
                'plone.email_charset',
            )
        except plone_api.exc.InvalidParameterError:
            email_charset = portal.getProperty('email_charset', 'utf-8')

        recipient = None
        portal_address = portal.getProperty('email_from_address')

        try:
            agent = self.item_info
            recipient = agent.email.value
        except Exception:
            recipient = portal_address

        if self.email_override is not None:
            recipient = self.email_override

        recipients = [recipient]
        bcc = self.config.get('contact_form_bcc', None)
        if bcc is not None:
            recipients += [formataddr(addr) for addr in getaddresses((bcc, ))]

        sender = formataddr((data['name'], data['sender_from_address']))

        subject = data['subject']
        data['url'] = self.request.getURL()
        body = translate(
            EMAIL_TEMPLATE,
            context=self.request,
        ).format(**data)
        email_msg = message_from_string(body.encode(email_charset))
        email_msg['To'] = formataddr((recipient, recipient))

        plone_api.portal.send_email(
            sender=sender,
            recipient=recipients,
            subject=subject,
            body=email_msg,
        )
        return True


# Register Captcha validator for the captcha field in the ICaptchaForm
validator.WidgetValidatorDiscriminators(
    CaptchaValidator, field=IContactForm['captcha'])


@implementer(IDevelopmentDetails)
class DevelopmentDetails(BrowserView):
    """Detail view for MLS developments."""

    _item = None
    _contact_form = None
    _contact_info = None

    if PLONE_5:
        index = ViewPageTemplateFile('templates/development_details_p5.pt')
    elif PLONE_4:
        index = ViewPageTemplateFile('templates/development_details_view.pt')

    def __call__(self):
        self.setup()
        return self.render()

    def render(self):
        return self.index()

    def setup(self):
        self.registry = getUtility(IRegistry)  # noqa
        if PLONE_5:
            from Products.CMFPlone.resources import add_resource_on_request
            if self.use_fotorama():
                add_resource_on_request(self.request, 'psplonefotorama')
            try:
                pkg_resources.get_distribution('ps.plone.realestatefont')
            except pkg_resources.DistributionNotFound:
                pass
            else:
                from Products.GenericSetup.tool import UNKNOWN
                setup = plone_api.portal.get_tool(name='portal_setup')
                profile = 'profile-ps.plone.realestatefont:default'
                if setup.getLastVersionForProfile(profile) != UNKNOWN:
                    add_resource_on_request(
                        self.request,
                        'psplonerealestatefont',
                    )

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.context)
        return annotations.get(config.SETTINGS_DEVELOPMENT_COLLECTION, {})

    @property
    def item(self):
        if self._item is None:
            self._item = self._get_item()
        return self._item

    def _get_item(self):
        cache = IAnnotations(self.request)
        item = cache.get('ps.plone.mls.development.traversed', None)

        if item is None:
            item_id = getattr(self.request, 'development_id', None)
            if not item_id:
                return

            portal_state = queryMultiAdapter(
                (self.context, self.request),
                name='plone_portal_state',
            )
            lang = portal_state.language()
            item = api.get_development(
                item_id=item_id,
                context=self.context,
                request=self.request,
                lang=lang,
            )
        return item

    @property
    def lead_image(self):
        """"""
        item = self.item
        try:
            img = item.lead_image
        except AttributeError:
            pass
        else:
            return img

        try:
            images = item.pictures()
        except AttributeError:
            pass
        else:
            if len(images) > 0:
                return images[0]

    @property
    def map_id(self):
        """Generate a unique css id for the map."""
        try:
            item_id = self.item.id.value
        except Exception:
            item_id = 'unknown'
        return u'map__{0}'.format(item_id)

    def javascript_map(self):
        """Return the JS code for the map."""
        if not hasattr(self.item, 'geolocation') or not self.item.geolocation:  # noqa
            return

        icon = getattr(self.item, 'icon', None)
        if icon is not None:
            icon = icon.value
        icon_url = json.dumps(icon)

        lat, lng = self.item.geolocation.value.split(',')

        return MAP_JS.format(
            icon=icon_url,
            lat=lat,
            lng=lng,
            map_id=self.map_id,
            zoom=self.config.get('map_zoom_level', 7),
            ak=self.googleapi,
        )

    @property
    def googleapi(self):
        if not HAS_UI_SETTINGS:
            return ''

        if self.registry is not None:
            try:
                settings = self.registry.forInterface(IMLSUISettings)  # noqa
            except Exception:
                logger.warning('MLS UI settings not available.')
            else:
                return getattr(settings, 'googleapi', '')
        return ''

    def use_fotorama(self):
        if not HAS_UI_SETTINGS:
            return False

        if self.registry is not None:
            try:
                settings = self.registry.forInterface(IMLSUISettings)  # noqa
            except Exception:
                logger.warning('MLS UI settings not available.')
            else:
                return getattr(settings, 'slideshow') == u'fotorama'
        return False

    def use_galleria(self):
        if not HAS_UI_SETTINGS:
            return True

        if self.registry is not None:
            try:
                settings = self.registry.forInterface(IMLSUISettings)  # noqa
            except Exception:
                logger.warning('MLS UI settings not available.')
            else:
                return getattr(settings, 'slideshow') == u'galleria'
        # Fallback: 'galleria' is the default.
        return True

    def titles_for_phases(self):
        """Get the titles for the Development Phase fields."""
        raw = api.DevelopmentPhase.get_field_titles(self.item._api)
        return raw.get('response', {}).get('fields', {})

    def titles_for_groups(self):
        """Get the titles for the Property Group fields."""
        raw = api.PropertyGroup.get_field_titles(self.item._api)
        return raw.get('response', {}).get('fields', {})

    def distance_class(self):
        """Count how many distances are set"""
        counter = 0
        # get all distances
        item = self.item
        airport = item.airport_name or item.airport_distance
        bank = item.bank_name or item.bank_distance
        gas_station = item.gas_station_name or item.gas_station_distance
        hospital = item.hospital_name or item.hospital_distance
        shopping = item.shopping_name or item.shopping_distance

        if airport is not None:
            counter += 1
        if bank is not None:
            counter += 1
        if gas_station is not None:
            counter += 1
        if hospital is not None:
            counter += 1
        if shopping is not None:
            counter += 1

        return 'count_{0}'.format(counter)

    def show_section_contact(self):
        """Should the contact us section be shown at all?"""
        show_form = self.contact_form() is not None
        show_info = self.contact_info() is not None
        return show_info or show_form

    def _get_contact_info(self):
        if self._contact_info is not None:
            return self._contact_info

        item = self.item
        agency = getattr(item, 'agency', None)
        if agency is not None and agency() is not None:
            agency = agency()
            agency.override(context=self.context)
        agent = getattr(item, 'agent', None)
        if agent is not None and agent() is not None:
            agent = agent()
            agent.override(context=self.context)
        self._contact_info = {
            'agency': agency,
            'agent': agent,
        }
        return self._contact_info

    def contact_info(self):
        """Get the contact information, if enabled."""
        if not self.config.get('show_contact_info', False):
            return
        return self._get_contact_info()

    def contact_form(self):
        """Get the contact form, if enabled."""
        if not self.config.get('show_contact_form', False):
            return

        if self._contact_form is not None:
            return self._contact_form

        item_info = self._get_contact_info().get('agent')
        z2.switch_on(self, request_layer=IFormLayer)
        self._contact_form = ContactForm(
            aq_inner(self.context),
            self.request,
            info=item_info,
            development=self.item,
        )
        if HAS_WRAPPED_FORM:
            alsoProvides(self._contact_form, IWrappedForm)
        return self._contact_form

    def contact_link(self):
        return self.config.get('show_contact_link', False)

    def get_field_label(self, field_name):
        """Get the field label for ``field_name``.

        Do this even if the data may not exist within the current
        development object.
        """
        field = api.Field(field_name, None, self.item)
        return field.title

    def format_distance(self, name, distance):
        """Format the distance labels.

        Do this in the form of ``name - distance`` but also correctly handle
        None values.
        """
        text = []
        if name is not None:
            text.append(name)
        if distance is not None:
            text.append(distance)
        return u' - '.join(text)

    def base_url(self):
        return self.context.absolute_url()

    def group_listings(self, group=None):
        """Return the property group listings."""
        try:
            group_id = group.id.value
        except Exception:
            return

        try:
            item = api.PropertyGroup.get(self.item._api, group_id)
        except exceptions.ResourceNotFound:
            return None

        params = {
            'sort_on': 'last_activated_date',
            'reverse': '1',
        }
        try:
            results, batching = item.listings(params=params)
        except exceptions.MLSError, e:
            logger.warn(e)

        if results is None:
            return
        return ListingBatch(results, 0, batch_data=batching)


class HeaderViewlet(ViewletBase):
    """Header Image"""

    _id = None
    _title = None
    _headline = None
    _location = None
    _logo = None
    _banner = None
    _has_banner = False

    @property
    def available(self):
        # do we have a development?
        self._id = getattr(self.request, 'development_id', None)
        if self._id is not None:
            return True
        else:
            return False

    @property
    def get_title(self):
        """Get development title"""
        return self._title

    @property
    def get_headline(self):
        """Get development headline"""
        return self._headline

    @property
    def get_location(self):
        """Get development location"""
        return self._location

    @property
    def get_logo(self):
        """Get development logo"""
        return self._logo

    @property
    def get_banner(self):
        """Get development header"""
        return self._banner

    def update(self):
        """Prepare view related data."""
        super(HeaderViewlet, self).update()

        if self.available:
            self._set_development_info()

    def _set_banner(self, item):
        """Look for available Header image"""
        try:
            # banner image as regular data
            self._banner = item.banner_image.value
            self._has_banner = True
        except Exception:
            self._has_banner = False

    def _set_development_info(self):
        """Set all available data for the development header"""
        cache = IAnnotations(self.request)
        item = cache.get('ps.plone.mls.development.traversed', None)

        if item is not None:
            # try to set the available data
            try:
                self._logo = item.logo.value
            except Exception:
                pass
            try:
                self._title = item.title.value
            except Exception:
                pass
            try:
                self._headline = item.headline.value
            except Exception:
                pass
            try:
                seq = (item.city.value,
                       item.subdivision.value,
                       item.country.value)
                joint = ', '
                self._location = joint.join(seq)
            except Exception:
                self._location = item.location.value
            # set header image
            self._set_banner(item)


class DevelopmentCanonicalURL(ViewletBase):
    """Defines a canonical link relation viewlet.

    This needs to be displayed across the site. A canonical page is
    the preferred version of a set of pages with highly similar
    content. For more information, see:
    https://tools.ietf.org/html/rfc6596
    https://support.google.com/webmasters/answer/139394?hl=en
    """

    @memoize
    def render(self):
        context_state = queryMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')
        base_url = context_state.current_base_url()
        return u'    <link rel="canonical" href="{0}" />'.format(base_url)
