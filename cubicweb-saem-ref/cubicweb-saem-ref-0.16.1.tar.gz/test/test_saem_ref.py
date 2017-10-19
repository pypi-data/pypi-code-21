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
"""cubicweb-saem-ref automatic tests"""

from functools import partial
from unittest import TestCase
from logilab.common import attrdict

from cubicweb.devtools import testlib
from cubicweb.schema import SCHEMA_TYPES

from cubicweb_saem_ref import cwuri_url

import testutils


class CWURI_URLTC(TestCase):

    def test(self):
        class entity(attrdict):
            @property
            def _cw(self):
                return self

            def build_url(self, path):
                return 'http://built/' + path

        self.assertEqual(cwuri_url(entity({'cwuri': 'whatever'})),
                         'whatever')
        self.assertEqual(cwuri_url(entity({'cwuri': 'ark:/123'})),
                         'http://built/ark:/123')
        self.assertEqual(cwuri_url(entity({'cwuri': 'http://domain.org/ark:/123'})),
                         'http://domain.org/ark:/123')


class ArkURLTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            testutils.authority_with_naa(cnx)
            cnx.commit()

    def test_absolute_url_use_ark(self):
        ark_etypes = [eschema.type for eschema in self.schema['ark'].subjects()]
        create_entity_for = {
            'Agent': partial(testutils.agent, name=u'bob'),
            'AuthorityRecord': partial(testutils.authority_record, name=u'rec'),
            'Concept': partial(testutils.concept, label=u'l'),
            'ConceptScheme': partial(testutils.setup_scheme, title=u't'),
            'Organization': partial(testutils.authority_with_naa),
            'OrganizationUnit': partial(testutils.organization_unit, name=u'ou'),
            'SEDAArchiveTransfer': testutils.setup_profile,
        }
        baseurl = self.vreg.config['base-url']
        with self.admin_access.cnx() as cnx:
            testutils.setup_scheme(cnx, u'example', u'l')
            cnx.commit()
            for etype in ark_etypes[:]:
                # with self.subTest(etype=etype):
                entity = create_entity_for[etype](cnx)
                assert entity.ark
                url = entity.absolute_url()
                assert url.startswith(baseurl)
                path = url[len(baseurl):]
                self.assertEqual(path, u'ark:/' + entity.ark)
                ark_etypes.remove(etype)
        if ark_etypes:
            self.fail('entity types not checked {}'.format(ark_etypes))


class AutomaticWebTest(testlib.AutomaticWebTest):
    test_ten_each_config = None  # deactivate attempt to auto populate
    skip_views = set([
        'calendar',
        'csvexport',
        'ecsvexport',
        'ejsonexport',
        'filetree',
        'hcal',
        'jsonexport',
        'n3rdf',
        'oneweekcal',
        'onemonthcal',
        'owlabox',
        'rsetxml',
        'rss',
        'security',
        'treeview',
        'xbel',
        'skos.source-sync',
    ])

    @property
    def no_auto_populate(self):
        seda_types_to_skip = [eschema.type for eschema in self.schema.entities()
                              if eschema.type.startswith('SEDA')
                              and eschema != 'SEDAArchiveTransfer']
        eac_types_to_skip = ['EACResourceRelation',
                             'HierarchicalRelation',
                             'ChronologicalRelation',
                             'AssociationRelation']
        cw_types_to_skip = [etype for etype in SCHEMA_TYPES
                            if etype not in ('CWEType', 'CWRType')]
        return seda_types_to_skip + eac_types_to_skip + cw_types_to_skip

    @property
    def ignored_relations(self):
        seda_types_to_skip = [rschema.type for rschema in self.schema.relations()
                              if rschema.type.startswith('seda_')
                              and rschema not in ('seda_archive_unit',
                                                  'seda_binary_data_object')]
        ext_types_to_skip = [rschema.type for rschema in self.schema.relations()
                             if 'ExternalUri' in rschema.objects()
                             or 'ExternalUril' in rschema.subjects()]

        return set(seda_types_to_skip + ext_types_to_skip + ['use_email'])

    def post_populate(self, cnx):
        unit, alt, alt_seq = testutils.create_archive_unit(
            cnx.find('SEDAArchiveTransfer').one())
        testutils.create_data_object(alt_seq)

        cnx.execute('SET L kind "preferred" WHERE NOT EXISTS (L label_of X, L kind "preferred")')

    def to_test_etypes(self):
        '''only test views for entities of the returned types'''
        no_auto_populate = self.no_auto_populate
        # skip email address as well because we drop its alias attribute which makes standard views
        # crashing, while it's only a second class citizen here so it's not actually a problem
        etypes = [eschema.type for eschema in self.schema.entities()
                  if not (eschema.final
                          or eschema.type in no_auto_populate
                          or eschema == 'EmailAddress')]
        return etypes

    def list_views_for(self, rset):
        for view in super(AutomaticWebTest, self).list_views_for(rset):
            if view.__regid__ in self.skip_views:
                continue
            yield view

    # XXX needed until 3.25 is released
    def list_boxes_for(self, rset):
        """returns the list of boxes that can be applied on `rset`"""
        req = rset.req
        for box in self.vreg['ctxcomponents'].possible_objects(req, rset=rset,
                                                               view=None):
            yield box


if __name__ == '__main__':
    import unittest
    unittest.main()
