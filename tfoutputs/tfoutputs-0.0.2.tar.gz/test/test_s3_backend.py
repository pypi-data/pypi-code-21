import pytest
import os
from tfoutputs.backends.backend import S3Backend


class TestS3Backend():
    @pytest.fixture()
    def s3_backend(self):
        config = {'bucket_name': 'fake.bucket.for.vcr',
                  'bucket_key': 'terraform.tfstate',
                  'bucket_region': 'eu-west-1'
                  }
        return S3Backend(config)

    # need to VCR this.
    def test_save(self, s3_backend, vcr_test):
        with vcr_test.use_cassette('s3backend.yml'):
            file = s3_backend.save()
            assert (os.path.exists(file))
