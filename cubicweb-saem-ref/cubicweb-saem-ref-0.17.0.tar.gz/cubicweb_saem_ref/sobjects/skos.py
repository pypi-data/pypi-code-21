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
"""SKOS import overrides"""

import sys

from cubicweb.dataimport.stores import NoHookRQLObjectStore

from cubes.skos import sobjects as skos

from . import SAEMMetadataGenerator


def _store(cnx, **kwargs):
    metagen = SAEMMetadataGenerator(cnx, **kwargs)
    # XXX detect if import is started through source-sync, because the massive store isn't usable
    # when other connections are active on the database
    if 'source-sync' in sys.argv and cnx.repo.system_source.dbdriver == 'postgres':
        from cubicweb.dataimport.massive_store import MassiveObjectStore
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        return NoHookRQLObjectStore(cnx, metagen=metagen)


class RDFSKOSImportService(skos.RDFSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        return super(RDFSKOSImportService, self)._do_import(stream, import_log,
                                                            store=_store(self._cw), **kwargs)


class LCSVSKOSImportService(skos.LCSVSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        scheme = self._cw.find('ConceptScheme', cwuri=kwargs['scheme_uri']).one()
        naa_what = scheme.cw_adapt_to('IArkNAALocator').naa_what()
        store = _store(self._cw, naa_what=naa_what)
        return super(LCSVSKOSImportService, self)._do_import(stream, import_log,
                                                             store=store, **kwargs)


class SKOSParser(skos.SKOSParser):
    """parser overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, url, raise_on_error):
        return super(SKOSParser, self)._do_import(url, raise_on_error=raise_on_error,
                                                  store=_store(self._cw, source=self.source))


def registration_callback(vreg):
    vreg.register_and_replace(RDFSKOSImportService, skos.RDFSKOSImportService)
    vreg.register_and_replace(LCSVSKOSImportService, skos.LCSVSKOSImportService)
    vreg.register_and_replace(SKOSParser, skos.SKOSParser)
