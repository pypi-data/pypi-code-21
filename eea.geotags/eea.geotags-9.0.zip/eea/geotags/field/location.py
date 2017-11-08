""" Field
"""
import logging
import json
from Acquisition import aq_get
from zope.i18nmessageid import Message
from zope.i18n import translate
from zope.component import queryAdapter
from zope.interface import noLongerProvides, alsoProvides
from Products.Archetypes import atapi
from Products.Archetypes import PloneMessageFactory as _
from eea.geotags.interfaces import IGeoTags, IGeoTagged, IJsonProvider
logger = logging.getLogger('eea.geotags.field')


class GeotagsFieldMixin(object):
    """ Add methods to get/set json tags
    """
    @property
    def multiline(self):
        """ Multiline
        """
        return isinstance(self, atapi.LinesField)

    def getJSON(self, instance, **kwargs):
        """ Get GeoJSON tags from instance annotations using IGeoTags adapter
        """
        geo = queryAdapter(instance, IGeoTags)
        if not geo:
            return ''
        return json.dumps(geo.tags)

    def setJSON(self, instance, value, **kwargs):
        """ Set GeoJSON tags to instance annotations using IGeoTags adapter
        """
        geo = queryAdapter(instance, IGeoTags)
        if not geo:
            return

        if not isinstance(value, dict) and value:
            try:
                value = json.loads(value)
            except Exception, err:
                logger.exception(err)
                return

        # remove IGeoTagged if all geotags are removed or provide it
        # if geotags are added
        if not value:
            return

        value_len = len(value.get('features'))
        if not value_len:
            if IGeoTagged.providedBy(instance):
                noLongerProvides(instance, IGeoTagged)
        else:
            if not IGeoTagged.providedBy(instance):
                alsoProvides(instance, IGeoTagged)
        geo.tags = value

    def json2items(self, geojson, key="title", val="description"):
        """ Util method to extract dict like items geo tags from geojson struct
        """
        if not geojson:
            return

        if not isinstance(geojson, dict):
            try:
                value = json.loads(geojson)
            except Exception, err:
                logger.exception(err)
                return
        else:
            value = geojson

        features = value.get('features', [])
        if not features:
            return

        for feature in features:
            properties = feature.get('properties', {})
            key = properties.get(key, properties.get('title', ''))
            val = properties.get(val, properties.get('description', ''))
            yield (key, val)

    def json2list(self, geojson, attr='description'):
        """ Util method to extract human readable geo tags from geojson struct
        """
        if not geojson:
            return

        if not isinstance(geojson, dict):
            try:
                value = json.loads(geojson)
            except Exception, err:
                logger.exception(err)
                return
        else:
            value = geojson

        features = value.get('features', [])
        if not features:
            return

        for feature in features:
            properties = feature.get('properties', {})
            data = properties.get(attr, properties.get('description', ''))
            if data:
                yield data
            else:
                yield properties.get('title', '')

    def json2string(self, geojson, attr='description'):
        """ Util method to extract human readable geo tag from geojson struct
        """
        items = self.json2list(geojson, attr)
        for item in items:
            return item
        return ''

    def validate_required(self, instance, value, errors):
        """ Validate
        """
        value = [item for item in self.json2list(value)]
        if not value:
            request = aq_get(instance, 'REQUEST')
            label = self.widget.Label(instance)
            name = self.getName()
            if isinstance(label, Message):
                label = translate(label, context=request)
            error = _(u'${name} is required, please correct.',
                      mapping={'name': label})
            error = translate(error, context=request)
            errors[name] = error
            return error
        return None

    def convert(self, instance, value):
        """ Convert to a structure that can be deserialized to a dict
        """
        if isinstance(value, dict):
            return value
        if not value:
            return value

        try:
            json.loads(value)
        except TypeError, err:
            service = queryAdapter(instance, IJsonProvider)
            query = {
                'q': value,
                'maxRows': 10,
                'address': value
            }
            if isinstance(value, str):
                value = service.search(**query)
                if value['features']:
                    match_value = value['features'][0]
                    value['features'] = []
                    value['features'].append(match_value)
            elif isinstance(value, (tuple, list)):
                agg_value = {"type": "FeatureCollection", "features": []}
                for tag in value:
                    query['q'] = tag
                    query['address'] = tag
                    match_value = service.search(**query)
                    if match_value['features']:
                        agg_value['features'].append(
                            match_value['features'][0])
                value = agg_value
            else:
                logger.warn(err)
                return None
            value = json.dumps(value)
        except Exception, err:
            logger.exception(err)
            return None
        return value

    def setTranslationJSON(self, instance, value, **kwargs):
        """ Mutator for translations
        """
        # No translations
        if not getattr(instance, 'isCanonical', None):
            return None
        if instance.isCanonical():
            return None
        canonical = instance.getCanonical()
        value = self.getJSON(canonical)
        self.setJSON(instance, value, **kwargs)
        return value

    def setCanonicalJSON(self, instance, value, **kwargs):
        """ Mutator for canonical
        """
        isCanonical = getattr(instance, 'isCanonical', None)
        if isCanonical and not isCanonical():
            return None

        hasJSON = self.getJSON(instance)
        if not isinstance(value, dict):
            try:
                value = json.loads(value)
            except Exception:
                if hasJSON and hasJSON != '{}':
                    return None
        value = self.convert(instance, value)
        self.setJSON(instance, value, **kwargs)
        return value


class GeotagsStringField(GeotagsFieldMixin, atapi.StringField):
    """ Single geotag field
    """
    def set(self, instance, value, **kwargs):
        """ Set
        """
        new_value = self.setTranslationJSON(instance, value, **kwargs)
        if new_value is None:
            new_value = self.setCanonicalJSON(instance, value, **kwargs)
        if not value:
            return atapi.LinesField.set(self, instance, [], **kwargs)
        elif not new_value:
            return
        tag = self.json2string(new_value)
        return atapi.StringField.set(self, instance, tag, **kwargs)


class GeotagsLinesField(GeotagsFieldMixin, atapi.LinesField):
    """ Multiple geotags field
    """
    def set(self, instance, value, **kwargs):
        """ Set
        """
        new_value = self.setTranslationJSON(instance, value, **kwargs)
        if new_value is None:
            new_value = self.setCanonicalJSON(instance, value, **kwargs)
        if not value:
            return atapi.LinesField.set(self, instance, [], **kwargs)
        elif not new_value:
            return
        tags = [tag for tag in self.json2list(new_value)]
        return atapi.LinesField.set(self, instance, tags, **kwargs)
