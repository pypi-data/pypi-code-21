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

from io import BytesIO

from pyramid.view import view_config

from cubicweb.dataimport.importer import SimpleImportLog

from cubes.skos import to_unicode
from cubicweb_eac import dataimport


@view_config(
    route_name='eac.import',
    request_method='POST',
    accept='application/json',
    renderer='json',
)
def eac_import(request):
    cnx = request.cw_cnx
    if cnx.session.anonymous_session:
        request.response.status_int = 401
        return {'error': 'This service requires authentication.'}
    if cnx.user.naa is None:
        request.response.status_int = 403
        return {'error': 'Authenticated user is not linked to an organisation, '
                'or his organisation has no ARK naming authority.'}

    try:
        _, _, eid = cnx.call_service('eac.import',
                                     stream=BytesIO(request.body),
                                     import_log=SimpleImportLog('<ws>'),
                                     naa=cnx.user.naa)

    except dataimport.InvalidXML as exc:
        request.response.status_int = 400
        return {'error': 'Invalid XML file',
                'details': to_unicode(exc)}

    except dataimport.MissingTag as exc:
        if exc.tag_parent:
            err = request.cw_request.__(
                'Missing tag %(tag)s within element %(parent)s in XML file')
            params = {'tag': exc.tag, 'parent': exc.tag_parent}
        else:
            err = request.cw_request.__('Missing tag %(tag)s in XML file')
            params = {'tag': exc.tag}
        request.response.status_int = 400
        return {'error': 'Unexpected EAC data',
                'details': err % params}

    except Exception as exc:  # pylint: disable=broad-except
        cnx.exception('error while importing EAC using web service')
        request.response.status_int = 500
        return {'error': 'EAC import failed'}

    else:
        record = cnx.find('AuthorityRecord', eid=eid).one()
        return {'ark': record.ark}


def includeme(config):
    config.add_route(
        'eac.import', '/authorityrecord',
        request_method='POST',
        accept='application/json',
        # XXX it would be nice if POST with other Content-Type would be routed to cubicweb
        # header='Content-Type: application/xml',
    )
    config.scan(__name__)
