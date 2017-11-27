from ftw.addressblock import _
from ftw.addressblock.interfaces import IAddressBlock
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope.i18n import translate
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IAddressBlockSchema(form.Schema):
    pass


class AddressBlock(Item):
    implements(IAddressBlock)

    def Title(self):
        return self.title or self.fallback_title

    @property
    def fallback_title(self):
        return translate(
            _(u'addressblock_title', default=u'Contact'),
            context=api.portal.get().REQUEST,
        )
