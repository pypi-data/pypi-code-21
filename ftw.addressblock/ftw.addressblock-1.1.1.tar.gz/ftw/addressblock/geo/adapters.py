from ftw.addressblock.interfaces import IAddressBlock
from ftw.geo.interfaces import IGeocodableLocation
from zope.component import adapts
from zope.interface import implements


class AddressBlockLocationAdapter(object):
    """
    Adapter that is able to represent the location in a geocodable string form.
    """
    implements(IGeocodableLocation)
    adapts(IAddressBlock)

    def __init__(self, context):
        self.context = context

    def getLocationString(self):
        """
        Build a geocodable location string from the AddressBlocks address
        related fields.
        """
        street = (self.context.address or '').strip()
        # Remove Postfach form street, otherwise Google geocoder API will
        # return wrong results.
        street = street.replace('Postfach', '').replace('\r', '').strip()
        zip_code = self.context.zip_code
        city = self.context.city
        country = self.context.country

        # The country alone is not enough fo a geo lookup, we need at least
        # another bit of the address.
        if not (street or zip_code or city):
            return ''

        return ', '.join([street, zip_code, city, country])
