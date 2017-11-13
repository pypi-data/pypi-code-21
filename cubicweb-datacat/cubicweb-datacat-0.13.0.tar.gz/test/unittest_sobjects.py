"""cubicweb-datacat unit tests for server objects"""

import tempfile
import urllib2

from logilab.mtconverter import xml_escape

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    startpgcluster,
    stoppgcluster,
    testlib,
)

from cubes.datacat import cwsource_pull_data
from utils import (
    create_file,
    mediatypes_scheme,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


def transformation_sequence(cnx, script):
    tseq = cnx.create_entity('TransformationSequence')
    cnx.create_entity('TransformationStep', index=0,
                      step_script=script, in_sequence=tseq)
    return tseq


class BaseResourceFeedTC(testlib.CubicWebTC):

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'Test dataset', description=u'A dataset',
                                   in_catalog=cat)
            cnx.commit()
            self.dataset_eid = ds.eid


class ResourceFeedParserTC(BaseResourceFeedTC):

    def pull_data(self, cwsource, **kwargs):
        return cwsource_pull_data(self.repo, cwsource.eid, **kwargs)

    def test_cwsource_without_resourcefeed(self):
        with self.admin_access.cnx() as cnx:
            source = cnx.create_entity(
                'CWSource', parser=u'datacat.resourcefeed-parser',
                type=u'datafeed', name=u'test', url=u'does not matter')
            cnx.commit()
        with self.assertRaisesRegexp(Exception, 'has no ResourceFeed attached'):
            self.pull_data(source, raise_on_error=True)

    def test_base(self):
        url = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            mediatype, = mediatypes_scheme(cnx, u'text/csv')
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=url,
                media_type=mediatype,
                resource_feed_of=self.dataset_eid)
            cnx.commit()
        cwsource = resourcefeed.resource_feed_source[0]
        dist = resourcefeed.resourcefeed_distribution[0]
        stats = self.pull_data(cwsource)
        self.assertEqual(len(stats['created']), 1)
        feid = stats['created'].pop()
        with self.admin_access.cnx() as cnx:
            importlog = cnx.find('CWDataImport').one()
            logs = importlog.log
        self.assertIn('fetched data from {0}'.format(url), logs)
        self.assertIn('data import for {0} completed'.format(url), logs)
        self.assertIn('adding file #{0} to distribution #{1}'.format(
            feid, dist.eid), logs)
        self.assertIn(xml_escape('adding file #{0} to distribution').format(
            feid), logs)
        with self.admin_access.repo_cnx() as cnx:
            f = cnx.entity_from_eid(feid)
            self.assertEqual(f.data_name, 'resource.dat')
            self.assertEqual(f.data_format, 'text/csv')
            self.assertEqual(list(f.file_distribution), [dist])
        # second pull, no update of sha1
        stats = self.pull_data(cwsource)
        self.assertEqual(len(stats['created']), 0)

    def test_with_processes(self):
        url = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            mediatype, = mediatypes_scheme(cnx, u'text/csv')
            # Validation script.
            vscript_eid = cnx.create_entity(
                'ValidationScript', name=u'validation script',
                media_type=mediatype).eid
            create_file(cnx, 'pass', reverse_implemented_by=vscript_eid)
            # Transformation sequence.
            tscript = cnx.create_entity(
                'TransformationScript',
                name=u'transformation script',
                media_type=mediatype)
            create_file(cnx, open(self.datapath('cat.py')).read(),
                        data_name=u'cat.py',
                        reverse_implemented_by=tscript)
            # Create resource feed.
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=url,
                media_type=mediatype,
                resource_feed_of=self.dataset_eid,
                validation_script=vscript_eid,
                transformation_script=tscript)
            cnx.commit()
        cwsource = resourcefeed.resource_feed_source[0]
        stats = self.pull_data(cwsource)
        assert len(stats['created']) == 1
        with self.admin_access.cnx() as cnx:
            importlog = cnx.find('CWDataImport').one()
            logs = importlog.log
        self.assertIn('created validation process', logs)
        self.assertIn('created transformation process', logs)
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.find('DataTransformationProcess',
                            process_for_resourcefeed=resourcefeed.eid)
            process = rset.one()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            # There should be one result.
            output = cnx.find('File', produced_by=process).one()
            self.assertEqual([r.eid for r in output.file_distribution[0].of_dataset],
                             [self.dataset_eid])

    def test_file_update(self):
        """Update a file between two datafeed pulls"""
        with tempfile.NamedTemporaryFile() as tmpf:
            tmpf.write('coucou')
            tmpf.flush()
            with self.admin_access.repo_cnx() as cnx:
                mtype, = mediatypes_scheme(cnx, u'whatever')
                vscript_eid = cnx.create_entity(
                    'ValidationScript',
                    name=u'validation script',
                    media_type=mtype).eid
                create_file(cnx, 'pass',
                            reverse_implemented_by=vscript_eid)
                # Transformation script and process.
                tscript_eid = cnx.create_entity(
                    'TransformationScript',
                    name=u'transformation script',
                    media_type=mtype).eid
                create_file(cnx, open(self.datapath('reverse.py')).read(),
                            data_name=u'reverse',
                            reverse_implemented_by=tscript_eid)
                resourcefeed = cnx.create_entity(
                    'ResourceFeed', url=u'file://' + tmpf.name,
                    media_type=mtype,
                    validation_script=vscript_eid,
                    transformation_script=tscript_eid,
                    # Setting a "large" versions_to_keep value to prevent
                    # deletion of replaced files.
                    versions_to_keep=10,
                    resource_feed_of=self.dataset_eid)
                cnx.commit()
            cwsource = resourcefeed.resource_feed_source[0]
            stats = self.pull_data(cwsource)
            self.assertEqual(len(stats['created']), 1, stats)
            feid = stats['created'].pop()
            expected = {'content': 'uocuoc\n', 'nvalidated': 1, 'nproduced': 1}
            self._check_datafeed_output(feid, vscript_eid,
                                        tscript_eid, expected)
            # Change input file.
            tmpf.write('\nau revoir')
            tmpf.flush()
            stats = self.pull_data(cwsource)
            self.assertEqual(len(stats['created']), 1)
            feid_ = stats['created'].pop()
            # second pull: change input
            expected = {'content': 'riover ua\nuocuoc\n',
                        'nvalidated': 2, 'nproduced': 2}
            self._check_datafeed_output(feid_, vscript_eid,
                                        tscript_eid, expected)
            # Pull one more time, without changing the source.
            # third pull: no change
            stats = self.pull_data(cwsource)
            for k, v in stats.iteritems():
                self.assertFalse(v, '%s: %r' % (k, v))
            # `expected` has not changed.
            self._check_datafeed_output(feid_, vscript_eid,
                                        tscript_eid, expected)

    def _check_datafeed_output(self, feid, vscript_eid, tscript_eid, expected):
        with self.admin_access.repo_cnx() as cnx:
            output = cnx.execute(
                'File X WHERE X produced_by TP, TP process_input_file F, F eid %(f)s',
                {'f': feid}).one()
            if 'content' in expected:
                self.assertEqual(output.read(), expected['content'])
            if 'nvalidated' in expected:
                rset = cnx.execute(
                    'Any X WHERE X validated_by VP, VP validation_script S, S eid %(s)s',
                    {'s': vscript_eid})
                self.assertEqual(len(rset), expected['nvalidated'], rset)
            if 'nproduced' in expected:
                nproduced = expected['nproduced']
                rset = cnx.execute(
                    'Any X WHERE X produced_by TP, TP transformation_sequence SEQ,'
                    ' STEP in_sequence SEQ, STEP step_script S, S eid %(s)s',
                    {'s': tscript_eid})
                self.assertEqual(len(rset), nproduced, rset)

    def _check_value_error(self, cwsource):
        with self.assertRaises(ValueError) as cm:
            self.pull_data(cwsource)
        self.assertIn('MIME types of resource feeds attached',
                      str(cm.exception))

    def _check_transformations(self, cnx, stats):
        # Check both data processes have completed.
        rset = cnx.execute(
            'DataTransformationProcess X WHERE X in_state ST,'
            ' ST name "wfs_dataprocess_completed"')
        self.assertEqual(len(rset), 2)
        # Check resources and produced files.
        self.assertEqual(
            cnx.execute('Any COUNT(X) WHERE X file_distribution D')[0][0], 2)
        self.assertEqual(len(stats['created']), 1, stats)
        feid = stats['created'].pop()
        rset = cnx.execute('File X WHERE X produced_by TP, TP process_input_file F, F eid %(f)s',
                           {'f': feid})
        self.assertEqual(len(rset), 2, rset)

    def test_ftp(self):
        """Check that datafeed monkeypatch for retrieve_url handles ftp protocol"""
        url = u'ftp://user:pwd@does.not.exists'
        with self.admin_access.repo_cnx() as cnx:
            mediatype, = mediatypes_scheme(cnx, u'text/csv')
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=url,
                media_type=mediatype,
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            cwsource = resourcefeed.resource_feed_source[0]
            dfsource = self.repo.sources_by_eid[cwsource.eid]
            parser = dfsource._get_parser(cnx)
            # Just check we get an urllib2 error, meaning that we went through
            # opening the url.
            self.assertRaises(urllib2.URLError, parser.retrieve_url, url)


class GargageRessourceFeedProcessesTC(BaseResourceFeedTC):

    def test_cleanup(self):
        url = u'file://' + self.datapath('resource.dat')
        with self.admin_access.repo_cnx() as cnx:
            mediatype, = mediatypes_scheme(cnx, u'text/csv')
            vscript_eid = cnx.create_entity(
                'ValidationScript', name=u'validation script',
                media_type=mediatype)
            create_file(cnx, 'console.log("bad language ;)")',
                        reverse_implemented_by=vscript_eid)
            resourcefeed1 = cnx.create_entity(
                'ResourceFeed', url=url,
                media_type=mediatype,
                resource_feed_of=self.dataset_eid,
                validation_script=vscript_eid,
                processes_to_keep=2)
            resourcefeed2 = cnx.create_entity(
                'ResourceFeed', url=url,
                media_type=mediatype,
                resource_feed_of=self.dataset_eid,
                validation_script=vscript_eid,
                processes_to_keep=1)
            datafile = create_file(cnx, '1,2,3')
            cnx.commit()
            with cnx.security_enabled(write=False):
                processes1 = []
                for _ in range(3):
                    processes1.append(
                        cnx.create_entity('DataValidationProcess',
                                          process_for_resourcefeed=resourcefeed1,
                                          validation_script=vscript_eid,
                                          process_input_file=datafile))
                    cnx.commit()
                processes2 = []
                for _ in range(3):
                    processes2.append(
                        cnx.create_entity('DataValidationProcess',
                                          process_for_resourcefeed=resourcefeed2,
                                          validation_script=vscript_eid,
                                          process_input_file=datafile))
                    cnx.commit()

            def process_logfile(p):
                p.cw_clear_all_caches()
                return p.process_stderr[0].eid if p.process_stderr else None

            logfiles1 = map(process_logfile, processes1)
            logfiles2 = map(process_logfile, processes2)

            def process_log_files(eid):
                """Log files of processes of a resource feed with `eid`."""
                rset = cnx.execute(
                    'Any F WHERE P process_stderr F, P process_for_resourcefeed R,'
                    ' R eid %(eid)s', {'eid': eid})
                return [x for x, in rset.rows]

            with self.assertLogs(level='INFO') as cm:
                cnx.call_service('datacat.clean-resourcefeed-process-logs',
                                 eid=resourcefeed1.eid)
            self.assertEqual(len(cm.output), 1)
            self.assertIn('deleted process log files "%s"' % logfiles1[0],
                          str(cm.output[0]))

            self.assertCountEqual(process_log_files(resourcefeed1.eid),
                                  logfiles1[-2:])
            self.assertCountEqual(process_log_files(resourcefeed2.eid),
                                  logfiles2)

            with cnx.security_enabled(write=False):
                newprocess = cnx.create_entity(
                    'DataValidationProcess',
                    process_for_resourcefeed=resourcefeed1,
                    validation_script=vscript_eid,
                    process_input_file=datafile)
                cnx.commit()
                newprocess.cw_clear_all_caches()
                logfiles1.append(newprocess.process_stderr[0].eid)

            with self.assertLogs(level='INFO') as cm:
                cnx.call_service('datacat.clean-resourcefeed-process-logs')
            self.assertEqual(len(cm.output), 2)
            self.assertCountEqual(process_log_files(resourcefeed2.eid),
                                  logfiles2[-1:])
            self.assertCountEqual(process_log_files(resourcefeed1.eid),
                                  logfiles1[-2:])


if __name__ == '__main__':
    import unittest
    unittest.main()
