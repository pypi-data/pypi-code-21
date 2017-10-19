# coding=utf-8
"""Verify the `repomd.xml` file generated by a YUM distributor.

.. _repomd.xml: http://createrepo.baseurl.org/
"""
import os
import unittest
from urllib.parse import urljoin

from pulp_smash import api, cli, config, selectors, utils
from pulp_smash.constants import (
    REPOSITORY_PATH,
    RPM_NAMESPACES,
    RPM_UNSIGNED_FEED_URL,
)
from pulp_smash.tests.rpm.api_v2.utils import (
    gen_distributor,
    gen_repo,
    xml_handler,
)
from pulp_smash.tests.rpm.utils import check_issue_2277
from pulp_smash.tests.rpm.utils import set_up_module as setUpModule  # noqa pylint:disable=unused-import


class RepoMDTestCase(utils.BaseAPITestCase):
    """Tests to ensure ``repomd.xml`` can be created and is valid."""

    @classmethod
    def setUpClass(cls):
        """Generate, fetch and parse a ``repomd.xml`` file.

        Do the following:

        1. Create an RPM repository with a YUM distributor and publish it.
        2. Fetch the ``repomd.xml`` file from the distributor, and parse it.
        """
        super(RepoMDTestCase, cls).setUpClass()
        if check_issue_2277(cls.cfg):
            raise unittest.SkipTest('https://pulp.plan.io/issues/2277')

        # Create a repository with a yum distributor and publish it.
        client = api.Client(cls.cfg, api.json_handler)
        body = gen_repo()
        body['distributors'] = [gen_distributor()]
        repo = client.post(REPOSITORY_PATH, body)
        repo = client.get(repo['_href'], params={'details': True})
        cls.resources.add(repo['_href'])
        utils.publish_repo(cls.cfg, repo)

        # Fetch and parse repomd.xml
        client.response_handler = xml_handler
        path = urljoin(
            '/pulp/repos/',
            repo['distributors'][0]['config']['relative_url'],
        )
        path = urljoin(path, 'repodata/repomd.xml')
        cls.root_element = client.get(path)

    def test_tag(self):
        """Assert the XML tree's root element has the correct tag."""
        xpath = '{{{}}}repomd'.format(RPM_NAMESPACES['metadata/repo'])
        self.assertEqual(self.root_element.tag, xpath)

    def test_data(self):
        """Assert the tree's "data" elements have correct "type" attributes."""
        xpath = '{{{}}}data'.format(RPM_NAMESPACES['metadata/repo'])
        data_elements = self.root_element.findall(xpath)
        data_types = [element.get('type') for element in data_elements]
        data_types.sort()
        self.assertEqual(
            data_types,
            ['filelists', 'group', 'other', 'primary', 'updateinfo'],
        )


class FastForwardIntegrityTestCase(unittest.TestCase):
    """Ensure fast-forward publishes use files referenced by ``repomd.xml``.

    When Pulp performs an incremental fast-forward publish, it should copy the
    original repository's ``repodata/[…]-primary.xml`` file to the new
    repository, and then modify it as needed.

    According to `Pulp #1088`_, Pulp does something different: it searches for
    all files named ``repodata/[0-9a-zA-Z]*-primary.xml.*``, sorts them by
    mtime, copies the newest one to the new repository and modifies it. This
    behaviour typically works, because Pulp only creates one
    ``[…]-primary.xml`` file in a given repository. However, this behaviour is
    fragile, and it's especially likely to fail when third-party tools are used
    to supplement Pulp's functionality. What Pulp *should* do is to consult the
    old repository's ``repomd.xml`` file to find the ``[…]-primary.xml`` file.

    Do the following:

    1. Create a repository with a yum distributor, sync in some content, and
       publish it. Verify that ``[…]-primary.xml`` contains a certain phrase.
    2. Create a second ``[…]-primary.xml`` file in the published repository,
       and replace the known phrase with a new phrase. Trigger a full publish,
       and verify that the known phrase is present, not the new phrase.
    3. Create a second ``[…]-primary.xml`` file in the published repository,
       and replace the known phrase with a new phrase. Trigger an incremental
       publish, and verify that the known phrase is  present, not the new
       phrase.

    .. _Pulp #1088: https://pulp.plan.io/issues/1088
    """

    def test_all(self):
        """Ensure fast-forward publishes use files referenced by repomd.xml."""
        cfg = config.get_config()
        if selectors.bug_is_untestable(1088, cfg.version):
            self.skipTest('https://pulp.plan.io/issues/1088')
        repo = self._create_sync_repo(cfg)
        old_phrase = 'A dummy package of'
        new_phrase = utils.uuid4()

        # Publish the repository, and verify its […]-primary.xml file.
        utils.publish_repo(cfg, repo)
        primary_xml = self._read_primary_xml(cfg, repo)
        self.assertIn(old_phrase, primary_xml)
        self.assertNotIn(new_phrase, primary_xml)

        # Create a dummy-primary.xml. Trigger a regular publish.
        self._create_dummy_primary_xml(cfg, repo, old_phrase, new_phrase)
        api.Client(cfg).post(urljoin(repo['_href'], 'actions/unassociate/'), {
            'criteria': {
                'filters': {'unit': {'name': 'bear'}},
                'type_ids': ['rpm'],
            }
        })
        utils.publish_repo(cfg, repo)
        primary_xml = self._read_primary_xml(cfg, repo)
        self.assertIn(old_phrase, primary_xml)
        self.assertNotIn(new_phrase, primary_xml)

        # Create a dummy-primary.xml. Trigger an incremental fast-forward pub.
        # Fast-forward publish described here: https://pulp.plan.io/issues/2113
        self._create_dummy_primary_xml(cfg, repo, old_phrase, new_phrase)
        utils.sync_repo(cfg, repo)
        utils.publish_repo(cfg, repo)
        primary_xml = self._read_primary_xml(cfg, repo)
        self.assertIn(old_phrase, primary_xml)
        self.assertNotIn(new_phrase, primary_xml)

    def _create_dummy_primary_xml(self, cfg, repo, remove, insert):
        """Create a modified copy of the given repository's ``primary.xml``.

        Create a copy of the given repository's ``[…]-primary.xml`` file named
        ``dummy-primary.xml``. Within this file, replace all occurrences of
        ``remove`` with ``insert``. If the original XML file is gzipped, the
        new one is too.

        Return the path to ``dummy-primary.xml``.
        """
        primary_xml_path = self._get_primary_xml_path(cfg, repo)
        gzipped = True if primary_xml_path.endswith('.gz') else False

        # Create a copy of […]-primary.xml called bogus-primary.xml.
        dummy_xml_path = os.path.join(
            os.path.split(primary_xml_path)[0],
            'dummy-primary.xml'
        )
        if gzipped:
            dummy_xml_path += '.gz'

        # Alter bogus-primary.xml.
        client = cli.Client(cfg)
        client.run(['cp', primary_xml_path, dummy_xml_path])
        if gzipped:
            client.run(['gunzip', dummy_xml_path])
            dummy_xml_path = dummy_xml_path[:-len('.gz')]
        client.run([
            'sed', '-i', '-e', '/'.join(('s', remove, insert, 'g')),
            dummy_xml_path
        ])
        if gzipped:
            client.run(['gzip', dummy_xml_path])
            dummy_xml_path += '.gz'

        return dummy_xml_path

    def _read_primary_xml(self, cfg, repo):
        """Return the contents of the given repository's ``primary.xml``."""
        primary_xml_path = self._get_primary_xml_path(cfg, repo)
        gzipped = True if primary_xml_path.endswith('.gz') else False
        if gzipped:
            cmd = ['gunzip', '--to-stdout', primary_xml_path]
        else:
            cmd = ['cat', primary_xml_path]
        return cli.Client(cfg).run(cmd).stdout

    def _create_sync_repo(self, cfg):
        """Create and sync a repository. Return a detailed dict of repo info.

        Also, schedule the repository for deletion with ``addCleanup()``.
        """
        client = api.Client(cfg, api.json_handler)
        body = gen_repo()
        body['importer_config']['feed'] = RPM_UNSIGNED_FEED_URL
        body['distributors'] = [gen_distributor()]
        repo = client.post(REPOSITORY_PATH, body)
        self.addCleanup(client.delete, repo['_href'])
        utils.sync_repo(cfg, repo)
        repo = client.get(repo['_href'], params={'details': True})
        return client.get(repo['_href'], params={'details': True})

    @staticmethod
    def _get_primary_xml_path(cfg, repo):
        """Return the path to ``primary.xml``, relative to repository root.

        Given a detailed dict of information about a published, repository,
        parse that repository's ``repomd.xml`` file and tell the path to the
        repository's ``[…]-primary.xml`` file. The path is likely to be in the
        form ``repodata/[…]-primary.xml.gz``.
        """
        client = api.Client(cfg, xml_handler)
        path = urljoin(
            '/pulp/repos/',
            repo['distributors'][0]['config']['relative_url']
        )
        path = urljoin(path, 'repodata/repomd.xml')
        root_elem = client.get(path)

        # <ns0:repomd xmlns:ns0="http://linux.duke.edu/metadata/repo">
        #     <ns0:data type="primary">
        #         <ns0:checksum type="sha256">[…]</ns0:checksum>
        #         <ns0:location href="repodata/[…]-primary.xml.gz" />
        #         …
        #     </ns0:data>
        #     …
        xpath = '{{{}}}data'.format(RPM_NAMESPACES['metadata/repo'])
        data_elems = [
            elem for elem in root_elem.findall(xpath)
            if elem.get('type') == 'primary'
        ]
        xpath = '{{{}}}location'.format(RPM_NAMESPACES['metadata/repo'])
        relative_path = data_elems[0].find(xpath).get('href')
        return os.path.join(
            '/var/lib/pulp/published/yum/https/repos/',
            repo['distributors'][0]['config']['relative_url'],
            relative_path,
        )
