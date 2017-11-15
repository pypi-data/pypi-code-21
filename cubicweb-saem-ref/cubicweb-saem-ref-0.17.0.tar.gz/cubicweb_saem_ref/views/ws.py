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
"""cubicweb-saem-ref Web Services"""

from rql import TypeResolverException

from cubicweb import NoResultError
from cubicweb.view import View
from cubicweb.predicates import (match_form_params, match_http_method,
                                 match_user_groups)
from cubicweb.web.views import json

from cubicweb_saem_ref import permanent_url


class AssignArkWebService(json.JsonMixIn, View):
    """JSON view to assign a new Ark for external usage."""

    __regid__ = 'saem.ws.ark'
    __select__ = (
        match_user_groups('users', 'managers')
        & match_form_params('organization')
        & match_http_method('POST')
    )

    # XXX could check Accept=application/json
    def call(self):
        org_ark = self._cw.form['organization']
        org_ark = org_ark.replace('ark:/', '')

        def error(msg):
            self.wdata([{'error': msg.format(org_ark)}])

        try:
            org = self._cw.find('Organization', ark=org_ark).one()
        except (TypeResolverException, NoResultError):
            error('No organization matching identifier "{0}".')
        else:
            if not org.ark_naa:
                error('Organization "{0}" cannot assign ARK identifiers.')
            else:
                ark = self._cw.call_service(
                    'saem.attribute-ark', naa=org.ark_naa[0])
                self.wdata([{'ark': ark}])


class AssignArkWebServiceMissingOrganization(AssignArkWebService):
    __select__ = (
        match_user_groups('users', 'managers')
        & match_http_method('POST')
    )

    def call(self):
        self.wdata([{'error': 'Missing required "organization" query parameter.'}])


class AssignArkWebServiceNonPOST(AssignArkWebService):
    __select__ = match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service is only accessible using POST.'}])


class AssignArkWebServiceNonAuthenticated(AssignArkWebService):
    __select__ = ~match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service requires authentication.'}])


class ListArchivalUnitsWebService(json.JsonMixIn, View):
    """JSON view returning the list of archival units (site archives) with their
    associated organization units with the 'deposit' role (services versant).
    """

    __regid__ = 'saem.ws.archival-units'

    def call(self):
        def base_descr(unit):
            return {
                'name': unit.name,
                'ark': unit.ark,
                'url': permanent_url(unit),
            }

        def unit_descr(unit):
            descr = base_descr(unit)
            descr.update({
                'state': unit.cw_adapt_to('IWorkflowable').state,
                'authority': base_descr(unit.authority[0]),
            })
            return descr

        unit_rql = ('Any X,XA,XN,XSN,XO,XON,XOA WHERE '
                    'X archival_role AR, '
                    'X ark XA, X name XN, '
                    'X in_state XS, XS name XSN, '
                    'X authority XO, XO name XON, XO ark XOA')
        descriptions = []
        for archival_unit in self._cw.execute(
                unit_rql + ', AR name "archival"').entities():
            archival_unit_descr = unit_descr(archival_unit)
            archival_unit_descr['deposit-units'] = []

            for deposit_unit in self._cw.execute(
                    unit_rql + ', AR name "deposit", XO archival_unit AU, AU eid %(au)s',
                    {'au': archival_unit.eid}).entities():
                archival_unit_descr['deposit-units'].append(unit_descr(deposit_unit))

            descriptions.append(archival_unit_descr)

        self.wdata(descriptions)
