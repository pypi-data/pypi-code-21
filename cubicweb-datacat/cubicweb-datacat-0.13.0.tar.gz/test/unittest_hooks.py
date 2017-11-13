"""cubicweb-datacat unit tests for hooks"""

from datetime import datetime

from pytz import utc

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
    startpgcluster,
    stoppgcluster,
)

from utils import (
    create_file,
    mediatypes_scheme,
    produce_file,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


def transformation_script(cnx, script_code, mtype):
    return cnx.create_entity('TransformationScript', name=u'script',
                             media_type=mtype,
                             implemented_by=create_file(cnx, script_code))


class ResourceFeedHooksTC(testlib.CubicWebTC):

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'Test dataset', description=u'A dataset',
                                   in_catalog=cat)
            cnx.commit()
            self.dataset_eid = ds.eid

    def test_distribution_created(self):
        with self.admin_access.repo_cnx() as cnx:
            mtype, = mediatypes_scheme(cnx, u'text/plain')
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=u'a/b/c',
                media_type=mtype,
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            self.assertTrue(resourcefeed.resourcefeed_distribution)
            dist = resourcefeed.resourcefeed_distribution[0]
            self.assertEqual(dist.media_type[0].label(), u'text/plain')
            self.assertEqual([x.eid for x in dist.of_dataset],
                             [self.dataset_eid])

    def test_resourcefeed_cwsource(self):
        with self.admin_access.repo_cnx() as cnx:
            mtype, = mediatypes_scheme(cnx, u'whatever')
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=u'a/b/c',
                media_type=mtype,
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            source = resourcefeed.resource_feed_source[0]
            self.assertEqual(
                source.config,
                'use-cwuri-as-url=no\nsynchronization-interval=7d')
            self.assertEqual(source.url, resourcefeed.url)
            resourcefeed.cw_set(url=u'c/b/a')
            cnx.commit()
            source.cw_clear_all_caches()
            self.assertEqual(source.url, u'c/b/a')

    def test_resourcefeed_transformation_sequence(self):
        """Test for datacat.add/drop-transformation-sequence hooks."""
        with self.admin_access.cnx() as cnx:
            mtype, = mediatypes_scheme(cnx, u'whatever')
            script = cnx.create_entity(
                'TransformationScript', name=u'script',
                media_type=mtype,
                implemented_by=create_file(cnx, 'pass'))
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=u'a/b/c',
                media_type=mtype,
                transformation_script=script,
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            tseq = cnx.find('TransformationSequence').one()
            tstep = tseq.reverse_in_sequence[0]
            self.assertEqual(tstep.index, 0)
            self.assertEqual(list(tstep.step_script), [script])
            resourcefeed.cw_set(transformation_script=None)
            cnx.commit()
            self.assertFalse(cnx.find('TransformationSequence'))

    def test_linkto_dataset(self):
        with self.admin_access.repo_cnx() as cnx:
            inputfile = create_file(cnx, 'data')
            mtype, = mediatypes_scheme(cnx, u'whatever')
            code = (
                'from __future__ import print_function\n'
                'print("plop", end="")\n'
            )
            tscript = transformation_script(cnx, code, mtype)
            resourcefeed = cnx.create_entity('ResourceFeed', url=u'a/b/c',
                                             media_type=mtype,
                                             resource_feed_of=self.dataset_eid,
                                             transformation_script=tscript)
            cnx.commit()
            produce_file(cnx, resourcefeed, inputfile)
            rset = cnx.execute('Any X WHERE X file_distribution D, D eid %s' %
                               resourcefeed.resourcefeed_distribution[0].eid)
            self.assertEqual(len(rset), 1, rset)
            outdata = rset.get_entity(0, 0).read()
            self.assertEqual(outdata, 'plop')

    def test_file_replaced(self):
        with self.admin_access.repo_cnx() as cnx:
            mtype, = mediatypes_scheme(cnx, u'whatever')
            tscript = transformation_script(cnx, 'pass', mtype)
            resourcefeed = cnx.create_entity('ResourceFeed', url=u'a/b/c',
                                             resource_feed_of=self.dataset_eid,
                                             media_type=mtype,
                                             versions_to_keep=2,
                                             transformation_script=tscript)
            cnx.commit()
            outfile1 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data'))
            outfile2 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data 2'))
            outfile3 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data 3'))
            rset = cnx.execute('Any F1,F2 WHERE F1 replaces F2')
            self.assertEqual(rset.rowcount, 2)
            self.assertIn([outfile2.eid, outfile1.eid], rset.rows)
            self.assertIn([outfile3.eid, outfile2.eid], rset.rows)
            rset = cnx.execute(
                'Any X WHERE X file_distribution D, D eid %(d)s',
                {'d': resourcefeed.resourcefeed_distribution[0].eid})
            self.assertEqual(rset.rowcount, 1)
            self.assertEqual(rset[0][0], outfile3.eid)
            # Test "datacat.clear-replaced-files" hook.
            resourcefeed.cw_set(versions_to_keep=1)
            cnx.commit()
            with self.assertLogs('cubicweb.session', level='INFO') as cm:
                outfile4 = produce_file(cnx, resourcefeed,
                                        create_file(cnx, 'data 4'))
                cnx.commit()
            self.assertEqual(len(cm.output), 1)
            # Deleting outfile2 triggers outfile1 deletion, per composite
            # flag on `replaces` relation.
            self.assertIn('deleting replaced File #%d' % outfile2.eid,
                          cm.output[0])
            self.assertFalse(cnx.find('File', eid=outfile1.eid))
            self.assertFalse(cnx.find('File', eid=outfile2.eid))
            rset = cnx.execute('Any F1,F2 WHERE F1 replaces F2')
            self.assertEqual(rset.rowcount, 1)
            self.assertIn([outfile4.eid, outfile3.eid], rset.rows)


class DatesHooksTC(testlib.CubicWebTC):

    configcls = PostgresApptestConfiguration

    def test_issued_modified(self):
        past = datetime(2008, 1, 4, 3, 4, 5, tzinfo=utc)
        future = datetime(3000, 1, 4, 3, 4, 5, tzinfo=utc)
        with self.admin_access.cnx() as cnx:
            catalog = cnx.create_entity(
                'DataCatalog', title=u'c', description=u'd', issued=past,
                catalog_publisher=cnx.create_entity('Agent', name=u'publisher'))
            dataset = cnx.create_entity(
                'Dataset', title=u'ds', description=u'A dataset',
                in_catalog=catalog)
            dist = cnx.create_entity(
                'Distribution', title=u'di', of_dataset=dataset,
                issued=future, modified=past)
            cnx.commit()
            self.assertEqual(catalog.issued, past)
            self.assertEqual(catalog.modified, past)
            self.assertGreater(dataset.issued, past)
            self.assertEqual(dataset.modified, dataset.issued)
            self.assertGreater(dataset.issued, past)
            self.assertEqual(dist.modified, past)
            self.assertEqual(dist.issued, future)
            dist.cw_set(access_url=u'http://example.org')
            cnx.commit()
            self.assertGreater(dist.modified, past)
            self.assertEqual(dist.issued, future)


class FileDistributionRelationHooksTC(testlib.CubicWebTC):

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', identifier=u'ds', title=u'ds',
                                   description=u'A dataset', in_catalog=cat)
            self.distribution_eid = cnx.create_entity(
                'Distribution', of_dataset=ds, title=u'THE distr',
                description=u'one and only', access_url=u'http://example.org').eid
            cnx.commit()

    @staticmethod
    def create_file(cnx, **kwargs):
        """Simplified version of utils.create_file"""
        return create_file(cnx, data_name=u"foo.txt", data="xxx", **kwargs)

    def create_distribution_file(self, cnx, **kwargs):
        """Create a file link to self.distribution_eid"""
        return self.create_file(cnx, file_distribution=self.distribution_eid,
                                **kwargs)

    def test_update_distribution_on_create_filedistribution(self):
        with self.admin_access.repo_cnx() as cnx:
            mediatypes_scheme(cnx, u'text/csv')
            cnx.commit()
            distr = cnx.entity_from_eid(self.distribution_eid)
            self.assertIsNone(distr.byte_size)
            self.assertFalse(distr.distribution_format)
            self.assertFalse(distr.media_type)
            self.assertIsNone(distr.download_url)
            distr_file = self.create_distribution_file(cnx, data_format=u'text/csv')
            cnx.commit()
            self.assertEqual(distr.byte_size, distr_file.size())
            self.assertEqual(distr.media_type[0].label(), distr_file.data_format)
            self.assertIsNone(distr.download_url)

    def test_update_distribution_on_create_and_on_update(self):
        """Test the value of issued and modified
            - when a file is added : issued ~= modified = time when the file is added
            - when a new file is added : issued ~= modified = time when the new file is added
            - when the last file is updated : issued = time when the file was added,
                                              modified = time when the file was updated
            - when an older file is updated : nothing change
        """
        with self.admin_access.repo_cnx() as cnx:
            distr = cnx.entity_from_eid(self.distribution_eid)
            file_v1 = self.create_distributionfile_and_check_date(cnx, distr)
            file_v2 = self.create_distributionfile_and_check_date(cnx, distr)
            self.update_file_and_check_date(cnx, distr, file_v2, current_file=True)
            self.update_file_and_check_date(cnx, distr, file_v1, current_file=False)

    def create_distributionfile_and_check_date(self, cnx, distr):
        before = distr.creation_date
        distr_file = self.create_distribution_file(cnx)
        cnx.commit()
        after = datetime.now(utc)
        distr.cw_clear_all_caches()
        for date in [distr.issued, distr.modified]:
            self.assertGreater(date, before)
            self.assertLess(date, after)
        return distr_file

    def update_file_and_check_date(self, cnx, distr, distr_file, current_file):
        issued_before, modified_before = distr.issued, distr.modified
        distr_file.cw_set(data_name=u'bar.txt')
        cnx.commit()
        distr.cw_clear_all_caches()
        self.assertEqual(distr.issued, issued_before)
        if current_file:
            self.assertGreater(distr.modified, modified_before)
        else:
            self.assertEqual(distr.modified, modified_before)

    def test_set_title_description(self):
        with self.admin_access.repo_cnx() as cnx:
            distr_file = self.create_distribution_file(cnx)
            self.assertEqual(distr_file.title, 'THE distr')
            self.assertEqual(distr_file.description, 'one and only')


if __name__ == '__main__':
    import unittest
    unittest.main()
