""" JSON Components
"""
import logging
import urllib
import json as simplejson
import operator
from eventlet.green import urllib2
from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName
from eea.geotags.config import WEBSERVICE
from eea.geotags.interfaces import IGeoGroups
from eea.geotags.interfaces import IBioGroups
from eea.geotags.interfaces import IGeoCountries
from eea.geotags.json.interfaces import IJsonProviderSearchMutator

logger = logging.getLogger('eea.geotags.json')

class GeoNamesJsonProvider(object):
    """ Get json from http://geonames.org and convert it to geojson
    """
    def __init__(self, context):
        self.context = context
        self._username = None

    @property
    def username(self):
        """ Geonames username
        """
        if self._username is None:
            ptool = getToolByName(self.context, 'portal_properties')
            gtool = getattr(ptool, 'geographical_properties', None)
            self._username = getattr(gtool, 'geonames_key', '')
        return self._username

    def groups(self, **kwargs):
        """ Groups
        """
        voc = queryAdapter(self.context, IGeoGroups)
        json = {
            'type': 'FeatureCollection',
            'features': []
        }
        json['features'] = []

        terms = [term for term in voc()]
        terms.sort(key=operator.attrgetter('title'))

        for term in terms:
            feature = {
                'type': 'Feature',
                'bbox': [],
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [],
                    },
                'properties': {
                    'name': '',
                    'title': '',
                    'description': '',
                    'tags': ["countries_group"],
                    'center': [],
                    'country': '',
                    'adminCode1': '',
                    'adminName1': '',
                    'other': {}
                }
            }

            feature['properties']['name'] = term.value
            feature['properties']['title'] = term.title

            # Description
            countries = queryAdapter(self.context, IGeoCountries)
            feature['properties']['description'] = term.title + ', ' + \
              ', '.join((country.title for country in countries(term.value)))

            json['features'].append(feature)
        json['features'].sort(key=lambda k: k['properties']['title'])
        return json

    def biogroups(self, **kwargs):
        """ Biogroups
        """
        voc = queryAdapter(self.context, IBioGroups)
        json = {
            'type': 'FeatureCollection',
            'features': []
        }
        json['features'] = []

        terms = [term for term in voc()]
        terms.sort(key=operator.attrgetter('title'))

        atvm = getToolByName(self.context, 'portal_vocabularies')
        avoc = atvm['biotags']

        for term in terms:
            feature = {
                'type': 'Feature',
                'bbox': [],
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [],
                    },
                'properties': {
                    'name': '',
                    'title': '',
                    'description': '',
                    'tags': ["biogeographical_region"],
                    'center': [],
                    'country': '',
                    'adminCode1': '',
                    'adminName1': '',
                    'other': {}
                }
            }

            feature['properties']['name'] = term.value
            feature['properties']['title'] = term.title
            feature['properties']['description'] = term.title

            try:
                latitude = float(avoc[term.value]['latitude'].title)
                longitude = float(avoc[term.value]['longitude'].title)
            except Exception, err:
                logger.exception(err)
                # Fallback to center of Europe
                latitude = 55.0
                longitude = 35.0
            feature['properties']['center'] = [latitude, longitude]

            json['features'].append(feature)
        json['features'].sort(key=lambda k: k['properties']['title'])
        return json

    def countries(self, **kwargs):
        """ Countries
        """
        group = kwargs.get('group', '')
        filters = []
        if group:
            voc = queryAdapter(self.context, IGeoCountries)
            filters = [term.value.replace('geo-', '') for
                       term in voc(group=group)]

        continentCode = kwargs.get('continentCode', 'EU')
        json = self.search(continentCode=continentCode,
                           featureClass='A',
                           featureCode='PCLI')
        if filters:
            features = json['features']
            json['features'] = [feature for feature in features
                                if feature['properties']['name'] in filters]

            # decide if we should extend search in Asia
            extend_asia = False
            filters_asia = []
            for feature in features:
                if not feature['properties']['name'] in filters:
                    extend_asia = True
                    filters_asia.append(feature['properties']['name'])

        # add/map countries from Asia
        if extend_asia:
            json_asia = self.search(continentCode='AS',
                                      featureClass='A',
                                      featureCode='PCLI')
            features_asia = json_asia['features']
            json['features'].extend([feature for feature in features_asia
                                 if feature['properties']['name'] in filters])

        # Fix country title
        for feature in json['features']:
            title = feature.get('properties', {}).get(
                'other', {}).get(
                    'countryName', '')
            if title:
                feature['properties']['title'] = title

        json['features'].sort(key=lambda k: k['properties']['title'])
        return json

    def nuts(self, **kwargs):
        """ Nuts
        """
        query = kwargs.copy()
        query['featureClass'] = 'A'
        query['featureCode'] = 'ADM1'
        return self.search(sort=True, **query)

    def cities(self, **kwargs):
        """ Cities
        """
        query = kwargs.copy()
        query['featureClass'] = 'P'
        return self.search(sort=True, **query)

    def natural_features(self, **kwargs):
        """ Natural features
        """
        query = kwargs.copy()
        query['featureClass'] = ['H', 'T']
        return self.search(sort=True, **query)

    def search(self, sort=False, **kwargs):
        """ Search using geonames webservice
        """
        template = {
            'type': 'FeatureCollection',
            'features': []
        }
        query = kwargs.copy()
        # remove featureClass as a way to say search for all classes if the
        # value is falsy
        if 'featureClass' in query and not query.get('featureClass'):
            del query['featureClass']
        query.setdefault('lang', 'en')
        query.setdefault('username', self.username)
        query = urllib.urlencode(query, doseq=1)
        try:
            conn = urllib2.urlopen(WEBSERVICE, query)
            json = conn.read()
        except Exception, err:
            logger.exception(err)
            return template

        try:
            json = simplejson.loads(json)
            json = json.get('geonames', []) or []
        except Exception, err:
            logger.exception(err)
            return template

        #json.sort(key=operator.itemgetter('name'))

        for item in json:
            feature = {
                'type': 'Feature',
                'bbox': [],
                'geometry': {
                    'type': 'Point',
                    'coordinates': [],
                    },
                'properties': {
                    'name': '',
                    'title': '',
                    'description': '',
                    'tags': '',
                    'center': [],
                    'country': '',
                    'adminCode1': '',
                    'adminName1': '',
                    'other': {}
                }
            }

            feature['geometry']['coordinates'] = [
                item.get('lat'), item.get('lng')]

            feature['properties']['center'] = [
                item.get('lat'), item.get('lng')]

            feature['properties']['name'] = str(item.get('geonameId'))

            feature['properties']['title'] = item.get('name')
            feature['properties']['description'] = ', '.join(x
                for x in (item.get('adminName1'), item.get('countryName')) if x)

            feature['properties']['tags'] = item.get('fcodeName')
            feature['properties']['country'] = item.get('countryCode')
            feature['properties']['adminCode1'] = item.get('adminCode1')
            feature['properties']['adminName1'] = item.get('adminName1')

            feature['properties']['other'] = item.copy()
            template['features'].append(feature)
        if sort:
            template['features'].sort(key=lambda k: k['properties']['title'])

        # Search mutator see json/adapter.py for example on how you can register
        # your own
        mutator = queryAdapter(self.context, IJsonProviderSearchMutator)
        if mutator:
            mutated_results = mutator(template)

        return mutated_results
