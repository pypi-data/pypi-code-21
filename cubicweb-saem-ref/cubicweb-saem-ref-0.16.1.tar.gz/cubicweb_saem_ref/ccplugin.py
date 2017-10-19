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
"""cubicweb-ctl plugin customizing eac-import command."""

import sys

from six import PY2

from logilab.common.decorators import monkeypatch

from cubicweb import MultipleResultsError, NoResultError
from cubicweb.toolsutils import underline_title
from cubicweb.utils import admincnx

from cubicweb_eac import ccplugin as eac

from . import _massive_store_factory, _nohook_store_factory


eac.ImportEacData.options = (
    ("authority", {
        'short': 'n', 'type': 'string',
        'default': False,
        'help': ('Name of the reference authority to use while importing data. This authority '
                 'should be linked to an NAA that will be used to attribute ARK identifiers. '
                 'If not specified, a single one is expected to be found in the database.'),
    }),
)


def _enc(string):
    if PY2 and not isinstance(string, str):
        string = string.encode('utf-8')
    return string


@monkeypatch(eac.ImportEacData)
def run(self, args):
    appid = args[0]
    repo = None
    try:
        with admincnx(appid) as cnx:
            repo = cnx.repo
            org_name = self.config.authority
            if org_name:
                try:
                    org = cnx.find('Organization', name=org_name).one()
                except NoResultError:
                    print('ERROR: there are no authority named "{}"'.format(org_name))
                    sys.exit(1)
            else:
                org_rset = cnx.find('Organization')
                try:
                    org = org_rset.one()
                except MultipleResultsError:
                    print('ERROR: there are several authorities, choose the one to use using '
                          '--authority option. It should be one of {}'.format(
                              ', '.join(_enc(org.name) for org in org_rset.entities())))
                    sys.exit(1)
            if not org.ark_naa:
                print('ERROR: authority {} is not associated to a ARK naming authority. Choose '
                      'another organization or associate it to a ARK naming authority first.'
                      .format(_enc(org.name)))
                sys.exit(1)

            print('\n%s' % underline_title('Importing EAC files'))
            if cnx.repo.system_source.dbdriver == 'postgres':
                store = _massive_store_factory(cnx, eids_seq_range=100)
                store.metagen.naa_what = org.ark_naa[0].what
            else:
                store = _nohook_store_factory(cnx)
            eac.eac_import_files(cnx, args[1:], authority=org, store=store)
    finally:
        if repo is not None:
            repo.shutdown()
