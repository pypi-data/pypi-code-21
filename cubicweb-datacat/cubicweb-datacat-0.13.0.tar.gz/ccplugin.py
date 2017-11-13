# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-datacat command plugins"""

from __future__ import print_function

import io
import json
import os
import os.path as osp
import requests
import zipfile

from logilab.common.shellutils import ProgressBar

from cubicweb.cwctl import CWCTL
from cubicweb.dataimport.importer import SimpleImportLog
from cubicweb.toolsutils import (
    Command,
    underline_title,
)
from cubicweb.utils import admincnx

from cubes.datacat import cwsource_pull_data
from cubes.datacat.vocabularies import (
    ADMS_FRENCH_LABELS,
    eurovoc_domains,
    EUROVOC_URI,
    LICENSE_SCHEME,
    simplify_eurovoc,
)
from cubes.skos import rdfio
from cubes.skos.ccplugin import ImportSkosData
from cubes.skos.sobjects import (
    graph_extentities,
    import_skos_extentities,
)


class SyncSKOSSchemes(Command):
    """Synchronize SKOS schemes for a datacat instance.

    <instance>
      identifier of a datacat instance.

    """
    arguments = '<instance>'
    name = 'sync-schemes'
    min_args = 1
    max_args = 1

    def run(self, args):
        appid = args[0]
        with admincnx(appid) as cnx:
            rset = cnx.execute(
                'Any S ORDERBY X WHERE X is SKOSSource, X through_cw_source S')
            title = '-> synchronizing SKOS sources'
            pb = ProgressBar(len(rset), title=title)
            created, updated = set([]), set([])
            for eid, in rset:
                stats = cwsource_pull_data(cnx.repo, eid, raise_on_error=False)
                pb.update()
                created.update(stats['created'])
                updated.update(stats['updated'])
            # French translations
            qs = (u'Any C WHERE C cwuri IN ({0}), '
                  u'NOT EXISTS(L label_of C, L kind "preferred", L language_code "fr")'.format(
                      ', '.join([u"'{0}'".format(uri) for uri in ADMS_FRENCH_LABELS])))
            uri2eid = dict((concept.cwuri, concept.eid) for concept in cnx.execute(qs).entities())
            title = '-> Adding missing french labels for ADMS concepts'
            pb = ProgressBar(len(uri2eid), title=title)
            for concept_uri, concept_eid in uri2eid.items():
                fr_label = ADMS_FRENCH_LABELS.get(concept_uri)
                if fr_label:
                    label = cnx.create_entity('Label', label=fr_label, language_code=u'fr',
                                              kind=u'preferred', label_of=concept_eid)
                    created.add(label)
                pb.update()
            cnx.commit()
            print('\n   {0} created, {1} updated'.format(len(created), len(updated)))
            print('\n-> Adding constraints for license schemes')
            cnx.execute('SET CS scheme_relation RT WHERE CS cwuri %(scheme_uri)s, '
                        'RT name %(rtype_name)s',
                        {'scheme_uri': LICENSE_SCHEME, 'rtype_name': 'license_type'})
            cnx.commit()


def set_store_default(cls):
    """Set default value for "cw-store" option to "massive"."""
    for option in cls.options:
        if option[0] == 'cw-store':
            option[1]['default'] = 'massive'
            break
    return cls


@set_store_default
class ImportEurovoc(ImportSkosData):
    """Synchronize Eurovoc concept schemes for a datacat instance.

    <instance>
      identifier of a datacat instance.

    """
    arguments = '[options] <instance>'
    name = 'import-eurovoc'
    min_args = 1
    options = (ImportSkosData.options + (
        ('update', {
            'short': 'u', 'type': 'yn', 'default': False,
            'help': 'Force Eurovoc thesaurus download, even file already exists'
        }),
    ))

    def run(self, args):
        appid = args[0]
        update = self.get('update')
        with admincnx(appid) as cnx:
            datadir = osp.join(cnx.repo.config.appdatahome, 'eurovoc')
        if not osp.isdir(datadir):
            os.mkdir(datadir)
        zip_fname = osp.join(datadir, 'eurovoc_skos.zip')
        n3_fname = osp.join(datadir, 'eurovoc_skos.n3')
        simplified_fname = osp.join(datadir, 'eurovoc_skos_simple.n3')
        json_fname = osp.join(datadir, 'eurovoc_domains.json')
        print(u'\n{0}'.format(underline_title('Importing Eurovoc thesaurus')))
        if not osp.isfile(zip_fname) or update:
            print(u'Downloading eurovoc SKOS/RDF ZIP file from publications.europa.eu')
            r = requests.get(EUROVOC_URI, stream=True)
            with open(zip_fname, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        elif osp.isfile(zip_fname):
            print(u'Using existing eurovoc SKOS/RDF ZIP file {0}'.format(zip_fname))
        if not osp.isfile(n3_fname) or update:  # n3 file is faster to load
            print(u'Extracting RDF file and converting to Turtle')
            eurovoc_graph = rdfio.default_graph()
            with zipfile.ZipFile(zip_fname) as eurovoc_zip:
                eurovoc_graph.load(eurovoc_zip.open('eurovoc_skos.rdf'), rdf_format='xml')
                with open(n3_fname, 'w') as f:
                    eurovoc_graph.dump(f, rdf_format='n3')
        print(u'Preparing data for import')
        simplified_graph = rdfio.default_graph()
        if not osp.isfile(simplified_fname) or update:
            eurovoc_graph = rdfio.default_graph()
            with open(n3_fname) as f:
                eurovoc_graph.load(f, rdf_format='n3')
            # Flatten and simplify the graph
            simplify_eurovoc(eurovoc_graph, simplified_graph)
            with open(simplified_fname, 'w') as f:
                simplified_graph.dump(f, rdf_format='n3')
        else:
            with open(simplified_fname) as f:
                simplified_graph.load(f, rdf_format='n3')
        if not osp.isfile(json_fname) or update:
            with io.open(json_fname, 'w', encoding='utf-8') as f:
                f.write(unicode(json.dumps(eurovoc_domains(simplified_graph), ensure_ascii=False,
                                           sort_keys=True, indent=2, separators=(u',', u':'))))
            print(u'-> JSON file with Eurovoc domains created at {0}'.format(json_fname))
        print(u'Importing data')
        with admincnx(appid) as cnx:
            import_log = SimpleImportLog('eurovoc.import')
            cwsource = cnx.execute(u'Any S WHERE S is CWSource, S url %(eurovoc_uri)s',
                                   {'eurovoc_uri': EUROVOC_URI}).one()
            store = self.cw_store_factories[self.get('cw-store')](cnx)
            (created, updated), conceptschemes = import_skos_extentities(
                cnx, graph_extentities(simplified_graph), import_log, source=cwsource, store=store)
            cnx.commit()
            print(u'Created: {0}\nUpdated: {0}'.format(len(created), len(updated)))
            if conceptschemes:
                print(u'Concept schemes:\n* {0}'.format('\n* '.join(conceptschemes)))
            _update_source(cnx, cwsource)
            cnx.repo.shutdown()


def _update_source(cnx, cwsource):
    """Update cw_source relation of entities to point to Eurovoc CWSource.
    """
    sql = cnx.system_sql
    sqlqs = ("UPDATE cw_source_relation SET eid_to=%(source)s WHERE eid_from in ("
             "SELECT _X.cw_eid FROM cw_{0} AS _X WHERE _X.cw_cwuri ILIKE '%%eurovoc%%')")
    for tablename in ('Label', 'Concept', 'ConceptScheme'):
        sql(sqlqs.format(tablename), {'source': cwsource.eid})
    cnx.commit()


class CleanResourceFeedProcesses(Command):
    """Remove ancient resource feed's processes.

    <instance>
      identifier of a datacat instance.
    """
    arguments = '<instance>'
    name = 'clean-processes'
    min_args = 1
    max_args = 1

    def run(self, args):
        appid = args[0]
        with admincnx(appid) as cnx:
            deleted = cnx.call_service('datacat.clean-resourcefeed-process-logs')
            cnx.commit()
        if deleted:
            print('deleted %d process logs' % len(deleted))
        else:
            print('nothing deleted')


for cmd in (SyncSKOSSchemes, ImportEurovoc, CleanResourceFeedProcesses):
    CWCTL.register(cmd)
