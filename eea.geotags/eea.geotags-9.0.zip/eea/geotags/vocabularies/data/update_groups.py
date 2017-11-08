""" Update countries dictionary
"""
import json as simplejson
import urllib
from datetime import datetime
from pprint import pformat
from eventlet.green import urllib2

COUNTRY_INFO = 'http://ws.geonames.org/countryInfoJSON'
GROUPS = {
    ('efta4', 'EFTA4'): {
        ('ch', 'ch'): {},
        ('is', 'is'): {},
        ('li', 'li'): {},
        ('no', 'no'): {},
    },
    ('eu15', 'EU15'): {
        ('at', 'at'): {},
        ('be', 'be'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lu', 'lu'): {},
        ('nl', 'nl'): {},
        ('pt', 'pt'): {},
        ('se', 'se'): {},
    },
    ('eu25', 'EU25'): {
        ('at', 'at'): {},
        ('be', 'be'): {},
        ('cy', 'cy'): {},
        ('cz', 'cz'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('ee', 'ee'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('hu', 'hu'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lt', 'lt'): {},
        ('lu', 'lu'): {},
        ('lv', 'lv'): {},
        ('mt', 'mt'): {},
        ('nl', 'nl'): {},
        ('pl', 'pl'): {},
        ('pt', 'pt'): {},
        ('se', 'se'): {},
        ('si', 'si'): {},
        ('sk', 'sk'): {},
    },
    ('eu27', 'EU27'): {
        ('at', 'at'): {},
        ('be', 'be'): {},
        ('bg', 'bg'): {},
        ('cy', 'cy'): {},
        ('cz', 'cz'): {},
        ('de', 'de'): {},
        ('dk', 'dk'): {},
        ('ee', 'ee'): {},
        ('es', 'es'): {},
        ('fi', 'fi'): {},
        ('fr', 'fr'): {},
        ('gb', 'gb'): {},
        ('gr', 'gr'): {},
        ('hu', 'hu'): {},
        ('ie', 'ie'): {},
        ('it', 'it'): {},
        ('lt', 'lt'): {},
        ('lu', 'lu'): {},
        ('lv', 'lv'): {},
        ('mt', 'mt'): {},
        ('nl', 'nl'): {},
        ('pl', 'pl'): {},
        ('pt', 'pt'): {},
        ('ro', 'ro'): {},
        ('se', 'se'): {},
        ('si', 'si'): {},
        ('sk', 'sk'): {},
    },
}


class Updater(object):
    """ Updater
    """
    _data = {}

    def __init__(self, **kwargs):
        self.info = kwargs.get('info', COUNTRY_INFO)
        self.groups = kwargs.get('groups', GROUPS)
        self.prefix = kwargs.get('prefix', 'geo-')

    @property
    def data(self):
        """ Data
        """
        return self._data

    def _update(self):
        """ Update
        """
        for group, countries in self.groups.items():
            self._data[group] = {}
            print 'Update group: %s' % group[0]
            for code, _country in countries.keys():
                query = {
                    'country': code,
                    'lang': 'en',
                    'style': 'full',
                }
                url_query = urllib.urlencode(query)
                con = urllib2.urlopen(self.info, url_query)
                json = con.read()
                data = simplejson.loads(json)
                data = data.get('geonames')[0]

                geoid = data.get('geonameId')
                title = data.get('countryName')
                name = "%s%s" % (self.prefix, geoid)

                self._data[group][(name, title)] = {}
                print '\tUpdated country %s' % title

    def __call__(self, **kwargs):
        self._update()
        return self.data

if __name__ == "__main__":
    updater = Updater()
    res = {}
    res[('geotags', "Geotags Tree")] = updater()
    res = 'VOC = ' + pformat(res)
    filename = 'groups.' + datetime.now().strftime('%Y%m%d%H%M%S') + '.py'
    open(filename, 'w').write(res)
    print 'See file: %s' % filename
