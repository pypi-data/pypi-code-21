# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-ctl plugin introducing skos-import command.
"""
from __future__ import print_function

import logging

from cubicweb.toolsutils import Command, underline_title
from cubicweb.cwctl import CWCTL
from cubicweb.utils import admincnx
from cubicweb.dataimport.importer import SimpleImportLog

from cubes.skos import rdfio
from cubes.skos.sobjects import graph_extentities, import_skos_extentities


def _massive_store_factory(cnx, **kwargs):
    from cubicweb.dataimport.massive_store import MassiveObjectStore
    return MassiveObjectStore(cnx, **kwargs)


def _nohook_store_factory(cnx, **kwargs):
    from cubicweb.dataimport.stores import NoHookRQLObjectStore
    return NoHookRQLObjectStore(cnx, **kwargs)


def _rql_store_factory(cnx, **kwargs):
    from cubicweb.dataimport.stores import RQLObjectStore
    return RQLObjectStore(cnx, **kwargs)


class LoggingImportLog(SimpleImportLog):
    logger = logging.getLogger('skos.import')

    def __init__(self):
        pass

    def _log(self, severity, msg, path, line):
        self.logger.log(severity, msg)


class ImportSkosData(Command):
    """Import a RDF SKOS concept scheme.

    <instance>
      identifier of the instance into which the scheme will be imported. Should use the skos cube.

    <filepath>
      path to the SKOS files to import.

    """
    arguments = '[options] <instance> <filepath>...'
    name = 'skos-import'
    min_args = 2
    options = (
        ('cw-store',
         {'short': 's',
          'type': 'choice', 'choices': ('rql', 'nohook', 'massive'), 'default': 'rql',
          'help': 'cubicweb store type: rql, nohook or massive (from the most secure but slowest '
          'to the less secure but fastest).'
          }),
        ('rdf-store',
         {'short': 'r',
          'type': 'choice', 'choices': ('librdf', 'rdflib'), 'default': 'rdflib',
          'help': 'RDF store type: librdf or rdflib.'
          }),
    )

    rdf_store_factories = {
        'librdf': rdfio.LibRDFRDFGraph,
        'rdflib': rdfio.RDFLibRDFGraph,
    }

    cw_store_factories = {
        'massive': _massive_store_factory,
        'nohook': _nohook_store_factory,
        'rql': _rql_store_factory,
    }

    def run(self, args):
        print(u'\n%s' % underline_title('Importing Skos dataset'))
        appid = args[0]
        graph = self.rdf_store_factories[self.get('rdf-store')]()
        for filepath in args[1:]:
            print(u'loading {} into RDF graph'.format(filepath))
            graph.load(filepath)
        import_log = LoggingImportLog()
        with admincnx(appid) as cnx:
            store = self.cw_store_factories[self.get('cw-store')](cnx)
            (created, updated), conceptschemes = import_skos_extentities(
                cnx, graph_extentities(graph), import_log, store=store)
            cnx.commit()
            print(u'Created: %d\nUpdated: %d' % (len(created), len(updated)))
            if conceptschemes:
                print(u'Concept schemes:\n* %s' % '\n* '.join(conceptschemes))
        cnx.repo.shutdown()


CWCTL.register(ImportSkosData)
