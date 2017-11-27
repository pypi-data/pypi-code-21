from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.geo.mapwidget.browser.widget import MapWidget
from ftw.addressblock.behaviors.misc import IAddressblockMisc
from ftw.addressblock.interfaces import IAddressBlockDetailView
from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class AddressMixin(object):
    address_template = ViewPageTemplateFile('templates/address.pt')

    def get_address_as_html(self):
        address = self.context.address
        extra_address_line = self.context.extra_address_line
        html = []
        if address:
            html.append(address)
        if extra_address_line:
            html.append(extra_address_line)
        return '<br />'.join(html)

    def has_team(self):
        result = aq_parent(aq_inner(self.context)).getFolderContents(
            contentFilter={
                'portal_type': 'ftw.simplelayout.ContentPage',
                'id': 'team',
            })
        return bool(result)

    def address(self):
        return self.address_template()

    def get_address_map(self):
        address_map = MapWidget(self, self.request, self.context)
        address_map.mapid = "geo-%s" % self.context.getId()
        address_map.addClass('block-map')
        address_map.klass = 'blockwidget-cgmap'
        return address_map

    def get_opening_hours(self):
        if IAddressblockMisc(self.context, None) and self.context.opening_hours:
            return self.context.opening_hours.output
        return ''

    def get_accessibility(self):
        if IAddressblockMisc(self.context, None) and self.context.accessibility:
            return self.context.accessibility.output
        return ''

    def get_directions(self):
        if self.context.directions:
            return self.context.directions.output
        return ''


class AddressBlockView(AddressMixin, BaseBlock):

    template = ViewPageTemplateFile('templates/block.pt')

    def get_data(self):
        data = {
            'title': self.context.Title(),
            'address': {
                'title': self.context.address_title,
                'phone': self.context.phone,
                'detail_view_url': '{0}/addressblock_detail_view'.format(
                    self.context.absolute_url()
                ),
                'accessibility': self.get_accessibility(),
                'opening_hours': self.get_opening_hours(),
                'email': self.context.email,
                'contact_url': '{0}/@@contact'.format(
                    self.context.absolute_url()
                ),
                'has_team': self.has_team(),
                'team_url': './team',
            },
            'wrapper_class': '',
        }
        return data


class AddressBlockDetailView(AddressMixin, BrowserView):
    """
    A browser view which renders the details of the address. The
    address block renders a link to this view.
    """
    implements(IAddressBlockDetailView)
