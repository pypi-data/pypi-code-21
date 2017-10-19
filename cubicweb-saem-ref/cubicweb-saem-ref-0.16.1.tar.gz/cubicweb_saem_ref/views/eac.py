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
"""cubicweb-saem-ref views for import/export of AuthorityRecord from/to EAC"""

from six import text_type

from cubicweb import tags
from cubicweb.predicates import specified_etype_implements
from cubicweb.web import formfields as ff
from cubicweb.web.views import editforms

from cubicweb_eac import views as eac

from .. import user_has_naa, user_has_authority


def naa_form_vocabulary(form, field):
    """Field vocabulary function returning the list of available authorities"""
    rset = form._cw.execute('Any XN, X ORDERBY XN WHERE X is ArkNameAssigningAuthority, X who XN')
    return [(name, text_type(eid)) for name, eid in rset]


class EACImportForm(eac.EACImportForm):
    """EAC-CPF import controller - overriden to add an NAA file, necessary to the service."""
    naafield = ff.StringField(name='naa', required=True,
                              choices=naa_form_vocabulary, sort=False)


class EACImportView(eac.EACImportView):
    """EAC-CPF import controller - overriden to provide NAA information to the service."""

    def service_kwargs(self, posted):
        """Subclass access point to provide extra arguments to the service (e.g. saem_ref cube).
        """
        return {'naa': self._cw.cnx.entity_from_eid(posted['naa'])}


class EACImportViewNoNaa(eac.EACImportView):
    __select__ = eac.EACImportView.__select__ & ~user_has_naa()

    def call(self):
        self.w(tags.h1(self._cw.__('Importing an AuthorityRecord from a EAC-CPF file')))
        if not self._cw.user.authority:
            msg = self._cw._("You must be in an organization to access this functionnality.")
            msg += u" <a href='{}'>{}</a>".format(self._cw.user.absolute_url(vid='edition'),
                                                  self._cw._('Edit your settings'))
        else:
            msg = self._cw._("Your organization must have an NAA configured to "
                             "access this functionnality.")
            authority = self._cw.user.authority[0]
            if authority.cw_has_perm('update'):
                msg += u" <a href='{}'>{}</a>".format(authority.absolute_url(vid='edition'),
                                                      self._cw._('Edit authority settings'))
        self.w(tags.div(msg))


class EACCreationFormViewNoNaa(editforms.CreationFormView):
    __select__ = (editforms.CreationFormView.__select__
                  & specified_etype_implements('AuthorityRecord')
                  & ~user_has_authority())

    def render_form(self, entity):
        self.form_title(entity)
        msg = self._cw._("You must be in an organization to access this functionnality.")
        msg += u" <a href='{}'>{}</a>".format(self._cw.user.absolute_url(vid='edition'),
                                              self._cw._('Edit your settings'))
        self.w(tags.div(msg))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (EACImportForm, EACImportView))
    vreg.register_and_replace(EACImportForm, eac.EACImportForm)
    vreg.register_and_replace(EACImportView, eac.EACImportView)
