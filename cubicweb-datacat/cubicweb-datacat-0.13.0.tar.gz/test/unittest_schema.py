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

"""Tests for cubicweb-datacat schema."""


from cubicweb import ValidationError
from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
    startpgcluster,
    stoppgcluster,
)

from utils import (
    create_file,
    mediatypes_scheme,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class DatasetRelationsTC(testlib.CubicWebTC):
    """Test case for Dataset entity type relations."""

    configcls = PostgresApptestConfiguration

    def test_dataset_dcat_theme_relation(self):
        """Check that constraint for ``theme`` relation on Dataset entity type is enforced."""
        with self.admin_access.repo_cnx() as cnx:
            # A concept scheme with a concept, and we link a catalog to this scheme
            scheme = cnx.create_entity('ConceptScheme', title=u'My Thesaurus')
            label = cnx.create_entity('Label', label=u'My Concept', kind=u'preferred',
                                      label_of=cnx.create_entity('Concept', in_scheme=scheme))
            concept = label.label_of[0]
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    theme_taxonomy=scheme,
                                    catalog_publisher=cnx.create_entity('Agent', name=u'bob'))
            cnx.commit()
            cnx.create_entity('Dataset', title=u'My Dataset', description=u'Dataset 1',
                              in_catalog=cat, dcat_theme=concept)
            cnx.commit()
            # Another scheme not related to the catalog
            scheme2 = cnx.create_entity('ConceptScheme', title=u'My Second Thesaurus')
            label2 = cnx.create_entity('Label', label=u'My Second Concept', kind=u'preferred',
                                       label_of=cnx.create_entity('Concept', in_scheme=scheme2))
            concept2 = label2.label_of[0]
            cnx.commit()
            with self.assertRaises(ValidationError) as cm:
                cnx.create_entity('Dataset', title=u'My Second Dataset', description=u'Dataset 2',
                                  in_catalog=cat, dcat_theme=concept2)
                cnx.commit()
                self.assertEqual(cm.exception.msg,
                                 "Theme must belong to the dataset's catalog vocabulary")
            # To have a theme, a dataset must be in a catalog
            with self.assertRaises(ValidationError) as cm:
                # No in_catalog
                cnx.create_entity('Dataset', title=u'My Third Dataset', description=u'Dataset 3',
                                  dcat_theme=concept)
                cnx.commit()
                self.assertEqual(cm.exception.msg,
                                 "Theme must belong to the dataset's catalog vocabulary")


class ResourceFeedTC(testlib.CubicWebTC):

    configcls = PostgresApptestConfiguration

    def test_resourcefeed_read_permissions(self):
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, u'bob', ('users', ))
            agent = cnx.create_entity('Agent', name=u'doe')
            catalog = cnx.create_entity('DataCatalog', title=u'c',
                                        description=u'd',
                                        catalog_publisher=agent)
            ds = cnx.create_entity('Dataset', title=u'd', description=u'd',
                                   in_catalog=catalog)
            mediatype, = mediatypes_scheme(cnx, u'whatever')
            cnx.create_entity('ResourceFeed',
                              url=u'ftp://user:secret@example.org',
                              media_type=mediatype,
                              resource_feed_of=ds)
            cnx.commit()
        with self.new_access(u'anon').cnx() as cnx:
            rset = cnx.find('ResourceFeed')
            self.assertEqual(len(rset), 0)
        with self.new_access(u'bob').cnx() as cnx:
            rset = cnx.find('ResourceFeed')
            self.assertEqual(len(rset), 0)

    def test_script_mimetype_constraints(self):
        """Check MIME type constraints on validation/transformation_script
        relations.
        """
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'ds', description=u'A dataset', in_catalog=cat)
            allpurpose, textcsv, textplain = mediatypes_scheme(
                cnx, u'application/octet-stream', u'text/csv', u'text/plain')
            cnx.create_entity('ValidationScript', name=u'csv',
                              media_type=textcsv,
                              implemented_by=create_file(cnx, 'pass'))
            cnx.create_entity('ValidationScript', name=u'plain',
                              media_type=textplain,
                              implemented_by=create_file(cnx, 'pass'))
            cnx.create_entity('ValidationScript', name=u'allpurpose',
                              media_type=allpurpose,
                              implemented_by=create_file(cnx, 'pass'))
            cnx.create_entity('ResourceFeed', url=u'a/b/c',
                              media_type=allpurpose,
                              resource_feed_of=ds)
            cnx.commit()
            with self.assertRaises(ValidationError) as cm:
                cnx.execute('SET R validation_script S WHERE S name "csv"')
                cnx.commit()
            self.assertEqual(cm.exception.errors,
                             {'validation_script-subject': (
                                 u'script does not handle resource feed data format')})
            cnx.rollback()
            cnx.execute('SET R validation_script S WHERE S name "allpurpose"')
            cnx.commit()


class ConcepConstraintTC(testlib.CubicWebTC):
    """Test case for schema constraints about the ``Concept`` entity type."""

    configcls = PostgresApptestConfiguration

    def test_license_type_constraint(self):
        """Check that a license type can only be set on a concept which is in the right concept
        scheme."""
        with self.admin_access.repo_cnx() as cnx:
            type_scheme = cnx.create_entity('ConceptScheme', title=u'Type scheme')
            type_concept = cnx.create_entity('Concept', in_scheme=type_scheme)
            cnx.create_entity('Label', label_of=type_concept, label=u'Share-alike',
                              kind=u'preferred', language_code=u'en')
            lic_scheme = cnx.create_entity('ConceptScheme', title=u'License scheme')
            other_scheme = cnx.create_entity('ConceptScheme', title=u'Other scheme')
            cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                        {'cs': lic_scheme.eid, 'rt': 'license_type'})
            cnx.commit()
            # License type can be set on concept in License scheme
            license = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                        license_type=type_concept.eid)
            cnx.create_entity('Label', label_of=license, label=u'My Custom License',
                              kind=u'preferred', language_code=u'en')
            cnx.commit()
            # License type cannot be set on concept in Other scheme
            with self.assertRaises(ValidationError) as cm:
                license = cnx.create_entity('Concept', in_scheme=other_scheme,
                                            license_type=type_concept.eid)
                cnx.create_entity('Label', label_of=license, label=u'My Custom License',
                                  kind=u'preferred', language_code=u'en')
                cnx.commit()
            self.assertEqual(cm.exception.errors,
                             {u'license_type-subject': u'Only concepts in licenses scheme can '
                              'have a license type'})


if __name__ == '__main__':
    import unittest
    unittest.main()
