# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import urllib2
import StringIO
import os.path

from logilab.common.decorators import monkeypatch
from logilab.database import FunctionDescr
from rql.utils import register_function
from cubicweb.server.sources import datafeed
from cubicweb.xy import xy

from cubes import skos


xy.register_prefix('dct', 'http://purl.org/dc/terms/')
xy.register_prefix('adms', 'http://www.w3.org/ns/adms#')
xy.register_prefix('dcat', 'http://www.w3.org/ns/dcat#')
xy.register_prefix('vcard', 'http://www.w3.org/2006/dcat/ns#')
xy.add_equivalence('Agent name', 'foaf:name')
xy.add_equivalence('Agent name', 'vcard:fn')  # XXX overrides ^?
xy.add_equivalence('Agent email', 'vcard:hasEmail')
xy.add_equivalence('Dataset identifier', 'dct:identifier')
xy.add_equivalence('Dataset title', 'dct:title')
xy.add_equivalence('Dataset creation_date', 'dct:issued')
xy.add_equivalence('Dataset modification_date', 'dct:modified')
xy.add_equivalence('Dataset description', 'dct:description')
xy.add_equivalence('Dataset keyword', 'dcat:keyword')
xy.add_equivalence('Dataset keyword', 'dcat:theme')
xy.add_equivalence('Dataset landing_page', 'dcat:landingPage')
xy.add_equivalence('Dataset spatial_coverage', 'dct:spatial')
xy.add_equivalence('Dataset provenance', 'dct:provenance')
xy.add_equivalence('Dataset dataset_distribution', 'dcat:distribution')
xy.add_equivalence('Dataset dataset_publisher', 'dct:publisher')
xy.add_equivalence('Dataset dataset_contact_point', 'adms:contactPoint')
xy.add_equivalence('Distribution access_url', 'dcat:accessURL')
xy.add_equivalence('Distribution description', 'dct:description')
xy.add_equivalence('Distribution format', 'dct:format')
xy.add_equivalence('Distribution licence', 'dct:license')


# DataFeedParser.retrieve_url fix to support ftp:// URLs and local files.
@monkeypatch(datafeed.DataFeedParser)
def retrieve_url(self, url, data=None, headers=None):
    """Return stream linked by the given url:
    * HTTP urls will be normalized (see :meth:`normalize_url`)
    * handle file:// URL
    * other will be considered as plain content, useful for testing purpose
    """
    headers = headers or {}
    if url.startswith(('http', 'ftp')):
        url = self.normalize_url(url)
        if url.startswith('http') and data:
            self.source.info('POST %s %s', url, data)
        else:
            self.source.info('GET %s', url)
        req = urllib2.Request(url, data, headers)
        return datafeed._OPENER.open(req, timeout=self.source.http_timeout)
    if url.startswith('file://'):
        return datafeed.URLLibResponseAdapter(open(url[7:]), url)
    if os.path.isfile(url):
        return datafeed.URLLibResponseAdapter(open(url), url)
    return datafeed.URLLibResponseAdapter(StringIO.StringIO(url), url)


# Needed until https://www.cubicweb.org/ticket/11257307 is done
@monkeypatch(skos)
def register_skos_rdf_list_mapping(reg):
    """Register minimal SKOS mapping, only describing concept scheme (for use in 'list.rdf' views).
    """
    reg.register_prefix('dct', 'http://purl.org/dc/terms/')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_etype_equivalence('ConceptScheme', 'skos:ConceptScheme')
    reg.register_attribute_equivalence('ConceptScheme', 'title', 'dct:title')
    reg.register_attribute_equivalence('ConceptScheme', 'description', 'dct:description')


# Register new Postgis functions

class ST_COLLECTIONEXTRACT(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_GEOMFROMGEOJSON(FunctionDescr):
    aggregat = True
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Geometry'


register_function(ST_COLLECTIONEXTRACT)
register_function(ST_GEOMFROMGEOJSON)
