# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-skos hooks"""

from six import text_type

from yams import ValidationError

from cubicweb import _
from cubicweb.server import hook
from cubicweb.predicates import is_instance

from cubes.skos.sobjects import dump_relations


class CreateRelationsOp(hook.DataOperationMixIn, hook.Operation):
    """Data operation updating the modification date of its data entities."""
    containercls = list

    def precommit_event(self):
        cnx = self.cnx
        for eid, relations in self.get_data():
            for subject_eid, rtype, object_eid in relations:
                if subject_eid is None:
                    subject_eid = eid
                elif cnx.deleted_in_transaction(subject_eid):
                    continue
                if object_eid is None:
                    object_eid = eid
                elif cnx.deleted_in_transaction(object_eid):
                    continue
                cnx.execute('SET X %s Y WHERE X eid %%(x)s, Y eid %%(y)s' % rtype,
                            {'x': subject_eid, 'y': object_eid})


class ReplaceExternalUriByEntityHook(hook.Hook):
    """Abstract hook to replace an ExternalUri with the same cwuri as the selected entity. To
    activate this behaviour, simply inherit from this hook and set a proper selector.

    Notice the hook has to be done on a 'before_add_entity' event as in case where the entity and
    the external uri are from an external source they will as such usually share the same extid
    which is a unique column in the `entities` system table. So this hook looks for a matching
    external uri, eventually records its relations into a data operation for later insertion
    and finally removes it.
    """
    __abstract__ = True
    __regid__ = 'skos.replace_externaluri'
    events = ('before_add_entity',)

    def __call__(self):
        cnx = self._cw
        rset = cnx.execute('ExternalUri X WHERE X cwuri %(uri)s', {'uri': self.entity.cwuri})
        if rset:
            exturi_eid = rset[0][0]
            # remember the external uri's relations and store them in an operation
            relations = dump_relations(cnx, exturi_eid, 'ExternalUri')
            CreateRelationsOp.get_instance(self._cw).add_data((self.entity.eid, relations))
            # delete the external uri before insertion of the new entity
            cnx.execute('DELETE ExternalUri X WHERE X eid %(x)s', {'x': exturi_eid})


class ReplaceExternalUriByConceptHook(ReplaceExternalUriByEntityHook):
    """Replace ExternalUri by a Concept"""
    __select__ = ReplaceExternalUriByEntityHook.__select__ & is_instance('Concept')


# SKOSSource <-> CWSource synchronization ######################################

# remove once fix for https://www.cubicweb.org/ticket/5477315 is published
# pylint: disable=wrong-import-position
from cubicweb import server  # noqa
server.BEFORE_ADD_RELATIONS.add('through_cw_source')


class CreateCWSource(hook.Hook):
    """Create a CWSource upon creation of a SKOSSource"""
    __regid__ = 'skos.create-source'
    __select__ = hook.Hook.__select__ & is_instance('SKOSSource')
    events = ('before_add_entity',)

    def __call__(self):
        if 'through_cw_source' in self.entity.cw_edited:
            return
        source = self._cw.create_entity('CWSource', name=self.entity.name, url=self.entity.url,
                                        type=u'datafeed', parser=u'rdf.skos',
                                        config=u'synchronize=no\nuse-cwuri-as-url=no')
        self.entity.cw_edited['through_cw_source'] = source.eid
        # remove once fix for https://www.cubicweb.org/ticket/5477315 is published
        nocheck = self._cw.transaction_data.setdefault('skip-security', set())
        nocheck.add((self.entity.eid, 'through_cw_source', source.eid))


class UpdateCWSource(hook.Hook):
    """update associated CWSource upon modification of name or url of a SKOSSource"""
    __regid__ = 'skos.update-source'
    __select__ = hook.Hook.__select__ & is_instance('SKOSSource')
    events = ('after_update_entity',)

    def __call__(self):
        edited = self.entity.cw_edited
        to_update = {}
        if 'name' in edited:
            to_update['name'] = edited['name']
        if 'url' in edited:
            to_update['url'] = edited['url']
        if to_update:
            self.entity.through_cw_source[0].cw_set(**to_update)


# Ensure Concept has a single preferred label in a given language label, kind, lang ################

class CheckPreferredLabelOp(hook.DataOperationMixIn, hook.Operation):
    """Data operation checking non-redundancy of labels of kind "preferred"."""
    containercls = list

    def precommit_event(self):
        concept_labels = dict((label.label_of[0].eid, label) for label in self.get_data())
        concept_eids = ',' . join(text_type(concept_eid) for concept_eid in concept_labels)
        rql = ('Any C WHERE EXISTS('
               'C preferred_label L, L language_code LC, '
               'C preferred_label L2, L2 language_code LC, '
               'NOT L identity L2), C eid IN (%s)' % concept_eids)
        for eid, in self.cnx.execute(rql):
            errors = {'': _('a preferred label in "%(lang)s" language already exists'),
                      'language_code': _('please use another language code')}
            label = concept_labels[eid]
            raise ValidationError(label.eid, errors, {'lang': label.language_code})
        rql = ('Any C WHERE EXISTS('
               'C preferred_label L, L language_code NULL, '
               'C preferred_label L2, L2 language_code NULL, '
               'NOT L identity L2), C eid IN (%s)' % concept_eids)
        for eid, in self.cnx.execute(rql):
            errors = {'': _('a preferred label without language already exists'),
                      'language_code': _('please specify a language code')}
            label = concept_labels[eid]
            raise ValidationError(label.eid, errors)


class CreateOrUpdatePrefLabelHook(hook.Hook):
    """Check for duplicate definition of a Label of kind "preferred"."""
    __regid__ = 'skos.check-preferred-label'
    __select__ = hook.Hook.__select__ & is_instance('Label')
    events = ('after_add_entity', 'after_update_entity')

    def __call__(self):
        edited = self.entity.cw_edited
        if edited.get('kind') == 'preferred':
            CheckPreferredLabelOp.get_instance(self._cw).add_data(self.entity)
        elif 'language_code' in edited and self.entity.kind == 'preferred':
            CheckPreferredLabelOp.get_instance(self._cw).add_data(self.entity)
