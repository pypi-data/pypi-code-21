# -*- coding: utf-8 -*-
""" RDF Marshaller module for geotags """

from eea.geotags.field.location import GeotagsFieldMixin
from eea.geotags.interfaces import IGeoTags
from eea.geotags.rdf.country_groups import COUNTRY_GROUPS
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.archetypes.interfaces import IATField2Surf
from eea.rdfmarshaller.interfaces import ISurfSession
from zope.component import adapts, getAdapter
from zope.interface import implements, Interface

import surf
import rdflib


class GeotagsField2Surf(ATField2Surf):
    """Adapter to express geotags field with RDF using Surf."""
    implements(IATField2Surf)
    adapts(GeotagsFieldMixin, Interface, ISurfSession)

    prefix = "dcterms"
    name = "spatial"

    def value(self):
        """desired RDF output is like:

        <document:Document
        rdf:about="
        http://www.eea.europa.eu/data-and-maps/daviz/learn-more/prepare-data">
        ...
        <dct:spatial>
            <geo:SpatialThing>
            <rdfs:label>Rome (Latium, Italy)</rdfs:label>
            <dcterms:title>Rome (Latium, Italy)</dcterms:title>
            <rdfs:comment>Latium, Italy</rdfs:comment>
            <dcterms:type>capital of a political entity</dcterms:type>
            <geo:lat>41.901514</geo:lat>
            <geo:long>12.460774</geo:long>
            <owl:sameAs rdf:resource="http://sws.geonames.org/3169070/">
            </geo:SpatialThing>
        </dct:spatial>
        <dct:spatial>
            <geo:SpatialThing>
            <rdfs:label>Bucharest (București, Romania)</rdfs:label>
            <dcterms:title>Bucharest (București, Romania)</dcterms:title>
            <rdfs:comment>Bucureşti, Romania</rdfs:comment>
            <dcterms:type>capital of a political entity</dcterms:type>
            <geo:lat>44.437711</geo:lat>
            <geo:long>26.097367</geo:long>
            <owl:sameAs rdf:resource="http://sws.geonames.org/683506/">
            </geo:SpatialThing>
        </dct:spatial>
        ...
        </document:Document>

        """
        # create a GeoPoint Class
        SpatialThing = self.session.get_class(surf.ns.GEO.SpatialThing)

        geo = getAdapter(self.context, IGeoTags)

        output = []
        i = 0

        cty_names = {u'Macedonia': u'Former Yugoslav Republic of'
                                   u' Macedonia, the',
                     u'Czechia': u'Czech Republic',
                     u'Kosovo': u'Kosovo (UNSCR 1244/99)'}
        cty_names_keys = cty_names.keys()

        country_groups = COUNTRY_GROUPS
        country_groups_keys = country_groups.keys()
        country_groups_keys_index = [ki[0] for ki in country_groups_keys]
        for feature in geo.getFeatures():
            rdfp = self.session.get_resource("#geotag%s" % i, SpatialThing)

            label = feature['properties']['title']
            # do not add current countries_group locations as they
            # will be added on rdf export when adding all of the country groups
            if label in country_groups_keys_index:
                continue
            description = feature['properties']['description']
            if label in cty_names_keys:
                label = cty_names[label]
                description = label
            rdfp[surf.ns.RDFS['comment']] = description

            if label == description or not description:
                friendly_name = label
            else:
                friendly_name = label + ' (' + description + ')'
            rdfp[surf.ns.DCTERMS['title']] = friendly_name
            rdfp[surf.ns.RDFS['label']] = friendly_name

            tags = feature['properties']['tags']
            rdfp[surf.ns.DCTERMS['type']] = tags

            latitude = feature['properties']['center'][0]
            rdfp[surf.ns.GEO['lat']] = float(latitude)

            longitude = feature['properties']['center'][1]
            rdfp[surf.ns.GEO['long']] = float(longitude)

            other = feature['properties'].get('other', {})
            if other.has_key('geonameId'):
                geonamesURI = 'http://sws.geonames.org/%s/' % (
                            str(feature['properties']['other']['geonameId']))
                rdfp[surf.ns.OWL['sameAs']] = rdflib.URIRef(geonamesURI)
            rdfp.update()
            output.append(rdfp)
            i += 1

        # 85617 add country groups to rdf output
        found_groups = []
        location = set(self.context.location)
        correct_country_names = cty_names.values()
        for k, v in country_groups.items():
            differences = set(v).difference(location)
            if differences:
                for country_name in correct_country_names:
                    if country_name in differences:
                        differences.remove(country_name)
                if not differences:
                    found_groups.append(k)
            else:
                found_groups.append(k)
        for group in found_groups:
            label = group[0]
            if label in location:
                continue
            rdfp = self.session.get_resource("#geotag%s" % i, SpatialThing)
            title = group[1]
            full_title = label + ' (' + title + ')'
            rdfp[surf.ns.DCTERMS['title']] = full_title
            rdfp[surf.ns.RDFS['label']] = full_title
            rdfp[surf.ns.RDFS['comment']] = title + ': ' + \
                                    ', '.join(country_groups[(label, title)])
            rdfp[surf.ns.DCTERMS['type']] = 'countries_group'
            rdfp[surf.ns.SKOS['notation']] = label
            uri = 'http://rdfdata.eionet.europa.eu/eea/countries/%s' % label
            rdfp[surf.ns.OWL['sameAs']] = rdflib.URIRef(uri)
            rdfp.update()
            output.append(rdfp)
            i += 1

        return output
