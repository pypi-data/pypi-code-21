# coding=utf-8
from fudge import Fake

from tests.base import BaseTest
from mali_commands.legit.object_store.gcs.gcs_object_store import GCSDownload


class TestGCSDownload(BaseTest):

    def testGetRequest(self):
        object_name = 'object_name_' + self.some_random_shit()
        signed_url = 'signed_url_' + self.some_random_shit()

        signed_url_service = Fake()\
            .expects('get_signed_urls')\
            .with_args(['GET'], [object_name])\
            .returns({'GET': [signed_url]})

        gcs_downloader = GCSDownload(signed_url_service)
        request = gcs_downloader._get_request('', '', object_name)

        self.assertEqual(request.uri, signed_url)
